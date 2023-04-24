"""Worker and mates module loader.
Mate worker modules MUST call a threaded start_function(),
else we hang. See watchdog.

"""

import os
import sys
import multiprocessing as mp

import eisenmp.utils.eisenmp_constants as const


class ToolBox:
    """Storage box for a Single Worker Process.
    Switch as much data fields to constant like shape. Used in worker.
    User can distinguish between custom and (automatic) in-build variables or constants.

    """
    def __init__(self):
        # default queues names from procenv
        self.mp_info_q = None  # performance data, or other
        self.mp_tools_q = None  # data too big to send with every list to worker
        self.mp_print_q = None  # formatted screen output with multiprocessor lock(), use sparse
        self.mp_input_q = None
        self.mp_output_q = None
        self.mp_process_q = None  # proc shutdown msg's
        # reserved names
        self.NEXT_LIST = None  # next list from your generator -> iterator creates list
        self.WORKER_ID = None  # Process-1 -> 1
        self.WORKER_PID = None  # process pid
        self.WORKER_NAME = None  # process name
        self.MULTI_TOOL = None  # tools_q, can be any prerequisite object for a module (made for bruteforce attacks)
        self.STOP_MSG = None  # not mp_print_q, ...worker_loader in one process informs other processes about stop
        self.STOP_CONFIRM_AND_PROCNAME = ''  # output_q_box thread gets worker messages, stop and results
        self.OUTPUT_HEADER = ''  # identify proc result in output_q_box
        self.INPUT_HEADER = ''  # ident proc result output_q_box (not stop msg) and copy result to result[INPUT_HEADER]
        self.PERF_HEADER_ETA = None  # str PERF_HEADER_ETA
        self.PERF_CURRENT_ETA = None  # header of list rows done for info_thread
        self.kwargs = None


def module_path_load(file_path):
    """Imports the module from path and returns it in the env.
    """
    path, f_name = os.path.split(file_path)
    modulename, _ = os.path.splitext(f_name)

    if path not in sys.path:
        sys.path.insert(0, path)
    return __import__(modulename)


def all_worker_exit_msg(toolbox):
    """
    Warning: Signal stop event to [ALL] -----> worker MODULES, not to PROCESS.

    :params: toolbox: tools and Queues for processes
    """
    stop_token_lst = [const.OUTPUT_HEADER,
                      const.STOP_MSG]  # 'STOP' was sent if last list was produced; now we inform other worker

    for q in toolbox.ALL_QUEUES_LIST:  # next worker on any q reads 'stop_token_lst', except 'mp_print_q'
        if q.empty():
            q.put(stop_token_lst)

    toolbox.mp_output_q.put([toolbox.STOP_CONFIRM_AND_PROCNAME])  # essential msg for caller, count stop to exit
    toolbox.mp_print_q.put(f'\texit WORKER {toolbox.WORKER_ID}')


def mp_worker_entry(**kwargs):
    """Entry.
    We are 'disconnected' from parent process now.
    Only Queue communication. Threads can exec() 'string' commands.
    All references are dead. Variables ok. We read only, here.
    """
    worker = None
    # assembled vars and names
    name = mp.process.current_process().name
    proc_id = name.split('-')
    tool_box = {name: ToolBox()}
    tool_box[name].__dict__.update(kwargs)  # ToolBox class, add user defined attributes of ModuleConfiguration inst
    # defaults
    tool_box[name].WORKER_ID = int(proc_id[1])
    tool_box[name].WORKER_PID = int(os.getpid())
    tool_box[name].WORKER_NAME = name
    tool_box[name].STOP_MSG = const.STOP_MSG
    tool_box[name].STOP_CONFIRM_AND_PROCNAME = const.STOP_CONFIRM + name
    tool_box[name].OUTPUT_HEADER = const.OUTPUT_HEADER
    tool_box[name].PERF_HEADER_ETA = const.PERF_HEADER_ETA  # performance list header for ProcInfo
    tool_box[name].PERF_CURRENT_ETA = None
    tool_box[name].kwargs = kwargs

    toolbox = tool_box[name]  # use normal instance like

    if 'worker_modules' not in kwargs:  # need mp_print_q
        msg = 'worker_loader: No Worker Module to start - exit function'
        toolbox.mp_print_q.put(msg)
        raise Exception(msg)

    # Module Loader
    mod_fun_lst = []
    for row in kwargs['worker_modules']:
        if len(row):
            path_t, ref_t = row.items()
            worker_path, worker_ref = path_t[1], ref_t[1]

            worker_mod = module_path_load(worker_path)  # str path to -> imported module now available
            fun_ref_exec = getattr(worker_mod, worker_ref)  # reference: can make function call now
            mod_fun_lst.append(fun_ref_exec)

    # Function executor
    if len(mod_fun_lst):
        mod_fun_len = len(mod_fun_lst)

        for workmate in range(mod_fun_len):
            if len(mod_fun_lst) >= 2:
                mate_fun = mod_fun_lst.pop()
                mate_fun(toolbox)
        worker = mod_fun_lst.pop()  # last but not least

    while 1:
        busy = worker(toolbox)  # until worker reads the iterator STOP msg
        if not busy:
            all_worker_exit_msg(toolbox)  # stop msg in all queues, if not all loaded worker are threads
            break

    while 1:

        msg_lst = toolbox.mp_process_q.get()  # loader keeps proc alive and awaits, 'stop_proc'
        if const.STOP_PROCESS in msg_lst:
            # [baustelle] ask in wrk loop
            for q in toolbox.ALL_QUEUES_LIST:  # multiple qs feeder may stick if first sent the worker stop
                if not q.empty():
                    q.get()
            break
