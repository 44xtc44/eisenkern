""" eisenmp constants single location

    * default queues names from procenv

    | **mp_info_q**  # performance data, or other
    | **mp_tools_q**  # data too big to send with every list to worker
    | **mp_print_q**  # formatted screen output with multiprocessor lock(), use sparse
    | **mp_input_q**  # default input
    | **mp_output_q**  # default, results and stop msg
    | **mp_process_q**  # proc shutdown msg's to ...worker_loader module

    * reserved names

    | **START_METHOD**  default `spawn`, `fork`, `forkserver`
    | **START_SEQUENCE_NUM**  process start number, use it to assign queues to CPU cores
    | **NEXT_LIST**  next list from your generator -> iterator creates list
    | **RESULTS_STORE**  keep in dictionary, will crash the system if store GB network chunks in mem
    | **RESULTS_PRINT**  result rows of output are collected in a list, display if processes are stopped
    | **RESULTS_DICT_PRINT**  shows content of results dict with ticket ID num _TID_
    | **RESULT_LABEL**  `revised.csv, Average calculation` pretty print header for RESULTS_PRINT
    | **WORKER_ID**  Process-1 -> 1
    | **WORKER_PID**  process pid
    | **WORKER_NAME**  process name
    | **MULTI_TOOL**  tools_q, can be any prerequisite object for a module (made for huge wordlists for bruteforce)
    | **STOP_MSG**  not in mp_print_q, ...worker_loader module in one process informs other processes about stop
    | **STOP_CONFIRM**  output_q_box collect thread gets worker messages, send exit messages to now idle processes
    | **OUTPUT_HEADER**  ident proc result output_q_box (not stop msg) and copy result to result[INPUT_HEADER]
    | **INPUT_HEADER** should be the input queue name, ident queue result if multiple queues are used on one output
    | **PERF_HEADER_ETA**  str PERF_HEADER_ETA
    | **PERF_CURRENT_ETA**  header of list rows done for info_thread
    
    * plus constants names mentioned below

"""


ROWS_MAX = 1_000  # workload for one CPU core of generator output, the default iterator appends as row to a list
PERF_HEADER_ETA = 'PERF_HEADER_ETA'  # begin of performance list header to calc ETA
STOP_MSG = 'STOP'  # worker knows iterator is empty, no more new lists, can exit, return False
STOP_CONFIRM = 'WORKER_STOPS'  # worker writes stop message to mp_output_q
STOP_PROCESS = 'STOP_PROC'  # 'output_q_box_view' triggers all procs stop, if all worker confirmed stop
OUTPUT_HEADER = 'OUTPUT_HEADER'  # begin of output header, 'output_q_box_view' collects result lists
RESULTS_STORE = False
PROCS_MAX = None  # default, all processor cores
RESULT_LABEL = 'add a "RESULT_LABEL" var'
TICKET_ID_PREFIX = '_TID_'
ALL_QUEUES_LIST = 'ALL_QUEUES_LIST'  # module_loader puts stop msg in queues
