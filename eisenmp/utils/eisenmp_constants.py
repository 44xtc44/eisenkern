""" eisenmp package constants definition
"""
GOT_RESULT_RESULT_THREAD = 'RESULT_INTERIM_GOT'  # append it to a list, use it for interim results during runtime
HEADER_MSG = 'INPUT_Q_HEAD'  # the default iterator writes a list header row, header and serial number, can be custom
NUM_ROWS = 1_000  # workload for one CPU core of generator output, the default iterator appends as row to a list
PERF_HEADER_ETA = 'PERF_HEADER_ETA'  # begin of performance list header to calc ETA
STOP_MSG = 'STOP'  # worker knows iterator is empty, no more new lists, can exit, return False
STOP_CONFIRM = 'WORKER_STOPS'  # worker writes stop message to mp_output_q
STOP_PROCESS = 'STOP_PROC'  # 'output_q_box_view' triggers all procs stop, if all worker confirmed stop
OUTPUT_HEADER = 'OUTPUT_HEADER'  # begin of output header, 'output_q_box_view' collects result lists
RESULTS_STORE = False
NUM_PROCS = None  # default, all processor cores
RESULT_LABEL = 'add a "RESULT_LABEL" var'
TICKET_ID_PREFIX = '_TID_'
ALL_QUEUES_LIST = 'ALL_QUEUES_LIST'  # module_loader puts stop msg in queues
