import threading
import contextlib
import multiprocessing

import eisenmp.utils.eisenmp_utils as e_utils
import eisenmp.utils.eisenmp_constants as const
from eisenmp.eisenmp_procenv import ProcEnv
from eisenmp.utils.eisenmp_info import ProcInfo


class FunThread(threading.Thread):
    """Thread maker.

    """
    def __init__(self, name, fun_ref, *args, **kwargs):
        super().__init__()
        # thread
        self.name = name
        self.daemon = True
        self.cancelled = False
        # stuff
        self.fun_ref = fun_ref  # no ()
        self.args = args
        self.kwargs = kwargs

    def run(self):
        """_inst.start()"""
        self.fun_ref(*self.args, **self.kwargs)
        self.cancel()

    def cancel(self):
        self.cancelled = True


class QueueCollect(ProcEnv):
    """Queue message collector and printer. Logging from prints.
    Messages in input and output Q have header.
    One can decide later what to do. Alter, or monitor.

    - Output `can` be stored in a box. `store_result` set

    """

    def __init__(self):
        super().__init__()
        # collect box
        self.info_q_box = {}
        self.print_q_box = []
        self.output_q_box = {}  # dict multi thread access
        # internal lists
        self.stop_list = []  # proc stop answered, worker names collector
        self.result_lst = []  # collected findings from procs for this run
        # collect results [baustelle]
        self.e_utilsResult = e_utils.Result()  # interim result calc for long-running task

        self.begin_proc_shutdown = False

    def enable_q_box_threads(self):
        """Collect Q messages and put em in a box for review, if enabled
        """
        self.enable_print_q()
        self.enable_output_q()

    def enable_info_q(self):
        """Thread for loop."""
        infoQThread = FunThread('eisenmp_InfoQThread', self.info_q_loop)
        infoQThread.start()
        self.thread_list.append(infoQThread)

    def enable_info_thread(self):
        """Shows % done, time left, if fed with an end value"""
        args_inf = [self.info_proc_info_thread,
                    self.mp_print_q,
                    self.info_q_box]
        self.pi = ProcInfo(*args_inf, **self.kwargs_env)  # ProcInfo sits on a subclassed thread
        self.pi.start()  # cancel() the thread in 'thread_end_join'

    def enable_print_q(self):
        """Thread for loop."""
        printQThread = FunThread('eisenmp_PrintQThread', self.print_q_loop)
        printQThread.start()
        self.thread_list.append(printQThread)

    def enable_output_q(self):
        """Start a thread loop to not block the show.
        Want collect stop confirm worker msg and results, all lists
        """
        outputQThread = FunThread('eisenmp_OutputQThread', self.output_q_loop)
        outputQThread.start()
        # self.thread_list.append(outputQThread)

    def print_q_loop(self):
        """Use a Print Q and a thread for formatted printing.

        Use it only sparingly. BLOCKS the whole multiprocessing.
        """
        while 1:
            if self.all_threads_stop:
                break
            try:
                if not self.mp_print_q.empty():
                    with multiprocessing.Lock():
                        msg = self.mp_print_q.get()
                        self.print_q_box.append(msg)
                        print(msg)
            except Exception as e:
                with contextlib.redirect_stdout(None):
                    print(e)

    def info_q_loop(self):
        """Print info or collect statistics from boxed messages.
        Box is a standard dict with num generator for unique keys.
        """
        while 1:
            if self.all_threads_stop:
                break
            generator = e_utils.consecutive_number()
            while not self.all_threads_stop:
                if not self.mp_info_q.empty():
                    msg = self.mp_info_q.get()
                    num = next(generator)
                    self.info_q_box[num] = msg
                    pass

    def output_q_loop(self):
        """Grab output from Queue and put it in a box.
        Use consecutive_number to create unique keys.

        Note: Multiple threads can loop over the box (dict).
        """
        generator = e_utils.consecutive_number()
        while 1:
            if self.all_threads_stop:
                break
            if not self.mp_output_q.empty():
                worker_output = self.mp_output_q.get()
                serial_num = next(generator)
                self.output_q_box[serial_num] = worker_output
                is_STOP_MSG = self.output_q_search_stop_confirm(serial_num)
                self.output_q_box_view_results(serial_num) if not is_STOP_MSG else None

    def output_q_search_stop_confirm(self, serial_num):
        """Search stop msg of workers and put 'em in a list.
        Stop processes and threads, if list is full.
        {1: ['RESULT_HEADER;PRIME_NUM;_TID_1;Process-1', ['10000079']], 24: ['PROC_STOP;Process-5']}

        :params: serial_num: serial number of `output_q_loop`
        """
        outbox = self.output_q_box
        if type(outbox[serial_num]) is list:
            outbox_list = outbox[serial_num]

            list_header = outbox_list[0]
            if list_header[:len(const.STOP_CONFIRM)] == const.STOP_CONFIRM:
                if self.worker_mods_down_ask(list_header):
                    self.print_findings()

                    self.begin_proc_shutdown = True
                    self.stop_proc()
                    self.end_proc()
                    self.all_threads_stop = True

                    self.stop_thread()
                    self.end_thread()

                return True

    def output_q_box_view_results(self, serial_num):
        """Only `lists` with header accepted.
        Box is a dictionary. {key: val} 'output_q_loop()' -> output_q_box[num]: payload or stop msg

        {1: ['RESULT_HEADER;PRIME_NUM;_TID_1;Process-1', ['10000079']], 24: ['PROC_STOP;Process-5']}

        Result header: RESULT_HEADER
        Delivery header: PRIME_NUM;_TID_;0  ['header_msg' and eisenmp, custom iterator, loop ticket id, split(;)]

        Add your custom header_msg, taken from double Q Example:
        - mP.run_q_feeder(generator=generator_aud, feeder_input_q=audio_q_b1, header_msg='BATCH_1_A')  # custom head
        - mP.run_q_feeder(generator=generator_vid, feeder_input_q=video_q_b1, header_msg='BATCH_1_V')

        :params: serial_num: serial number of `output_q_loop`
        """
        outbox = self.output_q_box
        if type(outbox[serial_num]) is list:
            outbox_list = outbox[serial_num]  # value of consecutive_number key is the list with results or stop msg

            list_header = outbox_list[0]
            if list_header[:len(const.OUTPUT_HEADER)] == const.OUTPUT_HEADER:
                result_row = outbox_list[1]

                if 'RESULTS_STORE' in self.kwargs_env and self.kwargs_env['RESULTS_STORE']:  # store results switch
                    queue_header_msg, queue_ticket_id = self.proc_result_store(list_header)
                    if not queue_ticket_id:
                        return

                    res_val = (queue_ticket_id, result_row)  # tuple
                    self.e_utilsResult.result_dict_update(queue_header_msg, res_val)  # result_dict['PRIME_NUM']=res_val

                if 'RESULTS_PRINT' in self.kwargs_env and self.kwargs_env['RESULTS_PRINT']:
                    self.proc_result_list_findings(result_row)

    @staticmethod
    def proc_result_store(list_header):
        """"""
        queue_head = list_header[len(const.OUTPUT_HEADER):]  # remove 'RESULT_HEADER'
        queue_head_lst = queue_head.split(';')  # search ticket number
        queue_header_msg = queue_head_lst[0]  # 'PRIME_NUM', use as key for result dict
        queue_ticket_id = None
        for str_section in queue_head_lst:
            if str_section[:len(const.TICKET_ID_PREFIX)] == const.TICKET_ID_PREFIX:
                queue_ticket_id = str_section
                break
        return queue_header_msg, queue_ticket_id

    def proc_result_list_findings(self, p_result_row):
        """RESULT DICT in utils, collect all results
        Append to result list for print out at finish.
        Add to a dict to monitor results via additional thread during runtime. [baustelle]

        STOP msg was also appended!

        :params: p_result_row: process loop result list row, can be a list in this row
        """
        if const.STOP_MSG in str(p_result_row):
            return

        if type(p_result_row) is list:
            [self.result_lst.append(str(row) + '\n') for row in p_result_row if str(row)]  # internal list
        else:
            self.result_lst.append(str(p_result_row) + '\n')

    def worker_mods_down_ask(self, list_header):
        """All worker MODULES confirm shutdown.

        Worker is using the original name of its process in shut down msg.
        Process IS still running. Worker module entry function returned False.

        :params: list_header: answer of WORKER MODULE to stop request; string with proc id at end
        :returns: None; True if done
        """
        WORKER_NAME = list_header[len(const.STOP_CONFIRM):]
        self.stop_list.append(WORKER_NAME)
        pending = any([True for proc in self.proc_list if proc.name not in self.stop_list])
        if not pending:
            return True

    def print_findings(self):
        """Condensed result list for this run.
        A thread can sum the results in 'Result' class.
        """
        c_lst = []
        generator = (line.split('...') for line in list(set(self.result_lst)))
        try:
            c_lst = list(set([tup[2] for tup in generator]))
        except IndexError:
            c_lst.extend(self.result_lst)

        lbl = self.kwargs_env['RESULT_LABEL'] if 'RESULT_LABEL' in self.kwargs_env else const.RESULT_LABEL
        c_lst.insert(0, f'\n--- Result for [{lbl}]---\n')
        c_lst.append('    --- END ---\n')
        print('\n'.join(c_lst))  # procs down

        if 'RESULTS_DICT_PRINT' in self.kwargs_env and self.kwargs_env['RESULTS_DICT_PRINT']:
            print(e_utils.Result.result_dict)
