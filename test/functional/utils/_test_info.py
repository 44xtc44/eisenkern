import time
import unittest
import threading

import eisenmp
import eisenmp.utils.eisenmp_info as info
import eisenmp.utils.eisenmp_utils as e_utils


class Helper:
    def __init__(self):
        self.is_on = True


helper = Helper()


class TestInfo(unittest.TestCase):
    """ thread_shutdown_wait() is tested in TestColl already
    """
    def test_class_proc_info_start_stop(self):
        """Threaded class
        Thread needs (name, print_q, info_q_box, **kwargs)
        """
        thread_list = []
        thread_name = 'fakeInfo'
        emp = eisenmp.Mp()

        infoThread = info.ProcInfo(thread_name, emp.mp_print_q, emp.info_q_box, **emp.kwargs_env)
        infoThread.start()
        thread_list.append(infoThread)

        names_list = [thread.name for thread in threading.enumerate()]
        assert thread_name in names_list

        helper.is_on = False
        for t in thread_list:
            t.cancel()
        e_utils.thread_shutdown_wait(thread_name)
        names_list = [thread.name for thread in threading.enumerate()]
        assert thread_name not in names_list

    @staticmethod
    def run_fake_thread():
        """"""
        while helper.is_on:
            time.sleep(.1)
