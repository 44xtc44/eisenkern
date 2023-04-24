"""ProcEnv

"""
import time
import multiprocessing as mp
from multiprocessing import Queue

import eisenmp.eisenmp_worker_loader as loader
import eisenmp.utils.eisenmp_utils as e_utils
import eisenmp.utils.eisenmp_constants as const

mp.set_start_method('spawn', force=True)  # override in ProcEnv.run_proc


class ProcEnv:
    """Create the environment for worker processes on CPUs.
    All queues shared among processes.
    'maxsize=1' can be altered, should be tested and documented.

    - **Queues ONLY**
    - custom Queue builder with a queue in a dict to show a name
    - another Queue builder can add a category name, dict in dict

    """

    def __init__(self):
        # CPU - process
        self.PROCS_MAX = self.core_count_get()  # user override in mod
        self.proc_list = []  # join processes at the end
        # Queues
        self.q_max_size = 1
        self.mp_info_q = Queue(maxsize=self.q_max_size)  # fake news and performance data
        self.mp_tools_q = Queue(maxsize=self.q_max_size)  # feeder is thread
        self.mp_print_q = Queue(maxsize=self.q_max_size)  # [!mp blocking!] OMG use sparse, formatted output
        self.mp_input_q = Queue(maxsize=self.q_max_size)  # order lists
        self.mp_output_q = Queue(maxsize=self.q_max_size)  # results and stop confirmation
        self.mp_process_q = Queue(maxsize=self.q_max_size)  # stop order
        self.queue_std_dict = {'mp_info_q': self.mp_info_q,
                               'mp_tools_q': self.mp_tools_q,
                               'mp_print_q': self.mp_print_q,
                               'mp_input_q': self.mp_input_q,
                               'mp_output_q': self.mp_output_q,
                               'mp_process_q': self.mp_process_q}
        self.queue_cust_dict_std = {}  # std dict, val is a q
        self.queue_cust_dict_cat = {}  # custom category, dict in dict
        self.q_lst = []  # all queues in a list, clean up; 'queue_lst_get'
        # queue tuple (name, id, q_ref), all custom created queues will be appended
        self.q_name_id_lst = [('mp_input_q (default)', id(self.mp_input_q), self.mp_input_q)]

        # Threads - Collect queue grabber
        self.thread_list = []
        self.info_q_thread_name = 'eisenmp_info_q_thread'
        self.input_q_thread_name = 'eisenmp_input_q_thread'
        self.output_q_thread_name = 'eisenmp_output_q_thread'
        self.print_q_thread_name = 'eisenmp_print_q_thread'
        self.tools_q_thread_name = 'eisenmp_tools_q_thread'
        #    ProcInfo
        self.info_proc_info_thread = 'eisenmp_ProcInfo_thread'  # gang
        self.pi = None  # ProcInfo Sub-thread instance thread, start(), cancel()

        # Main switch
        self.all_threads_stop = False  # ends thread loops
        # update
        self.kwargs_env = {}

    def queue_name_avail_get(self, name):
        """"""
        for tup in self.q_name_id_lst:
            if name == tup[0]:
                raise ValueError(f'eisenmp: Queue {name} already exists in ProcEnv.q_name_id_lst')
        return True

    def queue_cust_dict_std_create(self, *queue_name_maxsize: tuple):
        """create q, name and maxsize as unpacked list ('blue_q_7', 7)
        - Two queue creator functions. All use tuple to ease unpacking.

        'queue_cust_dict_std_create' - > 'queue_cust_dict_std'
        'queue_cust_dict_category_create' - > 'queue_cust_dict_cat'
        """
        for name, maxsize in queue_name_maxsize:
            self.queue_name_avail_get(name)
            self.queue_cust_dict_std[name] = Queue(maxsize=maxsize)
            self.q_name_id_lst.append((name, id(self.queue_cust_dict_std[name]), self.queue_cust_dict_std[name]))

    def queue_cust_dict_category_create(self, *queue_cat_name_maxsize: tuple):
        """('category_1', 'input_q_3', 10)
        """
        for cat, name, maxsize in queue_cat_name_maxsize:
            self.queue_name_avail_get(cat + '|' + name)

            new_dct = {name: Queue(maxsize=maxsize)}
            if cat not in self.queue_cust_dict_cat:
                self.queue_cust_dict_cat[cat] = {}
            self.queue_cust_dict_cat[cat].update(new_dct)
            self.q_name_id_lst.append((cat + '|' + name, id(new_dct[name]), new_dct[name]))

    def queue_lst_get(self):
        """List of qs for shut down msg put in, of ...worker_loader.py
        """
        q_lst = [self.mp_input_q]

        for q in self.queue_cust_dict_std.values():  # custom, std dict
            self.q_lst.append(q)
        for cat_dct in self.queue_cust_dict_cat.values():  # custom, category dict
            for q in cat_dct.values():
                q_lst.append(q)

        self.q_lst.extend(q_lst)
        return self.q_lst

    @staticmethod
    def core_count_get():
        """"""
        num = 1 if not mp.cpu_count() else mp.cpu_count() / 2  # hyper thread
        return int(num)

    def kwargs_env_update_custom(self, **kwargs):
        """override default PROCS_MAX,
        'queue_lst_get' for worker loader stop msg in all qs
        """
        self.PROCS_MAX = kwargs['PROCS_MAX'] if 'PROCS_MAX' in kwargs and kwargs['PROCS_MAX'] else self.core_count_get()
        kwargs.update(self.queue_std_dict)
        kwargs.update(self.queue_cust_dict_std)
        kwargs.update(self.queue_cust_dict_cat)
        all_qs_dict = {const.ALL_QUEUES_LIST: self.queue_lst_get(),
                       'Q_NAME_ID_LST': self.q_name_id_lst}  # view q name,id,ref in debugger: 'q_name_id_lst'
        kwargs.update(all_qs_dict)
        return kwargs

    def run_proc(self, **kwargs):
        """Create a Process for each CPU core, if `num_proc` None set or not set.
        - kwargs dict is updated for worker 'toolbox', reveals all vars and dead references (spawn) available

        :params: kwargs: -
        :params: start_method: selection spawn, fork
        :params: START_SEQUENCE_NUM: useful if eisenmp instance is called often, process numbers rise, but start from 0
        :params: target=loader: the worker_loader module is loaded and keeps the process alive
        """
        kwargs = self.kwargs_env_update_custom(**kwargs)

        start_method = 'spawn' if 'START_METHOD' not in kwargs else kwargs['START_METHOD']
        mp.set_start_method(start_method, force=True)

        print(f'\nCreate {self.PROCS_MAX} processes.')
        for core in range(self.PROCS_MAX):
            print(core, end=" ")
            # start_sequence_num always starts zero and is independent of sub-process spawn number
            start_sequence_num = {'START_SEQUENCE_NUM': core}  # worker in proc can grab a specific queue 0=red,1=blue
            kwargs.update(start_sequence_num)
            self.kwargs_env.update(kwargs)  # pytest kwargs

            proc = mp.Process(target=loader.mp_worker_entry,
                              kwargs=kwargs)
            proc.start()

            self.proc_list.append(proc)
        self.mp_print_q.put('\n')

    def stop_proc(self):
        """All worker must have confirmed shutdown msg."""
        for proc in range(len(self.proc_list)):
            self.mp_process_q.put(['Simon Says:', const.STOP_PROCESS])

        for process in self.proc_list:
            while process.is_alive():
                time.sleep(.1)

    def end_proc(self):
        """Graceful shutdown join.
        """
        for proc in self.proc_list:
            proc.join()
        print('\tProcesses are down.')

    def stop_thread(self):
        """"""
        for thread in self.thread_list:
            thread.cancel()

    def end_thread(self):
        """Instance and normal threads."""
        e_utils.thread_shutdown_wait(*self.thread_list)
        for t in self.thread_list:
            t.join()
