import threading
import time
import unittest

import eisenmp
import eisenmp.eisenmp_q_coll as coll
import eisenmp.utils.eisenmp_utils as e_utils
import eisenmp.utils.eisenmp_constants as const


class Helper:
    def __init__(self):
        self.is_on = True


helper = Helper()


class TestColl(unittest.TestCase):
    """
    """
    run_thread = True

    def test_fun_thread_class(self):
        """init thread and switch it on/off.
        """
        thread_name = 'eisenmp_FakeThread'
        thread_list = []

        fakeThread = coll.FunThread(thread_name, self.run_fake_thread)
        fakeThread.start()
        thread_list.append(fakeThread)
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

    def test_print_queue(self):
        """"""
        emp = eisenmp.Mp()  # create queues
        emp.enable_print_q()  # start collector thread
        msg = 'foo left the building'
        emp.mp_print_q.put(msg)
        time.sleep(1)  # while loop crashes the coverage thingy

        assert msg in emp.print_q_box
        for t in emp.thread_list:
            t.cancel()
        e_utils.thread_shutdown_wait(*emp.thread_list)

    def test_output_queue_stop_msg(self):
        """not like print q, we need lists here for stop and result
        enable_output_q calls output_q_loop, calls stop msg func, result msg func

        loader.all_worker_exit_msg(**emp.kwargs_env)
        worker endless loop broken, received stop from StopIteration queue feeder
        """
        emp = eisenmp.Mp()
        emp.enable_output_q()

        process_name = 'Process-321'
        code_word_stop = 'foo bar'
        emp.mp_output_q.put([const.STOP_CONFIRM + process_name, code_word_stop])
        time.sleep(.1)
        result_lst = [row for key, val in emp.output_q_box.items() for row in val]
        assert code_word_stop in result_lst

        for t in emp.thread_list:
            t.cancel()
        e_utils.thread_shutdown_wait(*emp.thread_list)

    def test_output_queue_result_msg(self):
        """not like print q, we need lists here for stop and result
        enable_output_q calls output_q_loop, calls stop msg func, result msg func

        loader.all_worker_exit_msg(**emp.kwargs_env)
        worker endless loop broken, received stop from StopIteration queue feeder
        """
        emp = eisenmp.Mp()
        emp.enable_output_q()

        process_name = 'Process-321'
        code_word_result = 'blacklist'
        emp.mp_output_q.put([const.OUTPUT_HEADER + process_name, code_word_result])
        time.sleep(.1)
        result_lst = [row for key, val in emp.output_q_box.items() for row in val]
        assert code_word_result in result_lst

        for t in emp.thread_list:
            t.cancel()
        e_utils.thread_shutdown_wait(*emp.thread_list)
