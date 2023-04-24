import os
import unittest
import unittest.mock as mock

import eisenmp
import eisenmp.eisenmp_worker_loader as loader


class TestLoader(unittest.TestCase):
    """ https://pytest-mock.readthedocs.io/en/latest/usage.html
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
    def test_mp_worker_entry_fail_no_worker_module_loaded(self, mp):
        """fails for current Main()
        assert multiprocessing.process.current_process().name == 'Process-42'
        'MainProcess' != 'Process-42'

        mock a module must use the module imports and assert them also there.
        """
        mp.process.current_process().name = 'Process-42'  # to feed toolbox.WORKER_ID
        assert eisenmp.eisenmp_worker_loader.mp.process.current_process().name == 'Process-42'

        emp = eisenmp.Mp()
        emp.run_proc()  # start queues, kwargs_env -> see test_procenv.test_run_proc description
        emp.enable_q_box_threads()  # init queue grabber threads, out and print
        try:
            loader.mp_worker_entry(**emp.kwargs_env)  # ProcEnv.kwargs_env is to preserve volatile kwargs for tests
        except Exception as e:
            print(e)

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
