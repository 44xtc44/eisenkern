import os
import unittest
import unittest.mock as mock

import eisenmp
import eisenmp.eisenmp_worker_loader as loader


class ModuleConfiguration:  # name your own class and feed eisenmp with the dict
    """
    """
    dir_name = os.path.dirname(__file__)
    test_module = {
        'WORKER_PATH': os.path.join(dir_name, 'test_loader.py'),
        'WORKER_REF': 'worker_entrance'
    }

    def __init__(self):

        self.worker_modules = [  # in-bld-res
            self.test_module,  # other modules must start threaded, else we hang
            # self.watchdog_module  # second; thread function call mandatory, last module loaded first
        ]

        # Multiprocess vars - override default
        self.PROCS_MAX = 2  # your process count, each 'batch' on one CPU core, default is None: one proc/CPU core


modConf = ModuleConfiguration()  # Accessible in the module


class TestLoader(unittest.TestCase):
    """
    """
    @staticmethod
    def my_isfile(filename):
        """Test function which calls os.path.isfile
        """
        if os.path.isfile(filename):
            return "Yes"
        else:
            return "Wrong"

    @mock.patch('os.path.isfile')
    def test_mock(self, mock_isfile):
        """self test
        also: mock_isfile = mock.patch('os.path.isfile')
        """
        mock_isfile.return_value = True
        assert self.my_isfile('foo') == 'Yes'

    @mock.patch('eisenmp.eisenmp_worker_loader.mp')   # attempt to mock whole module, import multiprocessing as mp
    def test_mp_worker_entry_process_name(self, mp):
        """fails for current Main()
        assert multiprocessing.process.current_process().name == 'Process-42'
        'MainProcess' != 'Process-42'

        mock a module must use the module imports and assert them also there.
        """
        mp.process.current_process().name = 'Process-42'  # to feed toolbox.WORKER_ID
        assert eisenmp.eisenmp_worker_loader.mp.process.current_process().name == 'Process-42'

    def test_toolbox_class(self):
        """
        """
        toolbox = loader.ToolBox()
        assert toolbox.mp_info_q is None  # performance data, or other
        assert toolbox.mp_tools_q is None  # data too big to send with every list to worker
        assert toolbox.mp_print_q is None  # formatted screen output with multiprocessor lock(), use sparse
        assert toolbox.mp_input_q is None
        assert toolbox.mp_output_q is None
        assert toolbox.mp_process_q is None  # proc shutdown msg's
        # reserved names
        assert toolbox.NEXT_LIST is None  # next list from your generator -> iterator creates list
        assert toolbox.NEXT_LIST is None  # next list from your generator -> iterator creates list
        assert toolbox.WORKER_ID is None  # Process-1 -> 1
        assert toolbox.WORKER_PID is None  # process pid
        assert toolbox.WORKER_NAME is None  # process name
        # toolbox.MULTI_TOOL is None  # tools_q, can be any prerequisite object for a module
        assert toolbox.STOP_MSG is None  # not mp_print_q, ...worker_loader in one process informs
        assert toolbox.STOP_CONFIRM_AND_PROCNAME == ''  # output_q_box thread gets worker messages, stop and results
        assert toolbox.OUTPUT_HEADER == ''  # identify proc result in output_q_box
        assert toolbox.INPUT_HEADER == ''  # ident proc result output_q_box (not stop msg) and copy result
        assert toolbox.PERF_HEADER_ETA is None  # str PERF_HEADER_ETA
        assert toolbox.PERF_CURRENT_ETA is None  # header of list rows done for info_thread
        assert toolbox.kwargs is None

    def test_loader(self):
        """No queue grabber start, we do get().
        """
        emp = eisenmp.Mp()
        emp.run_proc(**modConf.__dict__)
        emp.enable_q_box_threads()
        msg = emp.mp_info_q.get()
        assert msg == 'foo'


def worker_entrance(toolbox):
    """Print msg to show module is loaded.
    """
    toolbox.mp_info_q.put('foo')
    return False
