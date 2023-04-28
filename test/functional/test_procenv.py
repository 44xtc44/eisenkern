import time
import unittest
import eisenmp


class TestProcEnv(unittest.TestCase):
    """
    """

    def test_queue_cust_dict_std_create(self):
        """creation of queues with list entry to track, debug queues
        ProcEnv.q_name_id_lst [(name, id(queue object), queue reference]
        """
        emp = eisenmp.Mp()

        blue_q_7_max_3 = ('blue_q_7', 3)
        emp.queue_cust_dict_std_create(blue_q_7_max_3)

        two_q_lst = [('blue_q_7', 3), ('red_q_1', 1)]
        try:
            emp.queue_cust_dict_std_create(*two_q_lst)
        except ValueError:
            pass  # must fail, q name already exists

        three_q_lst = [('orange_q_2', 2), ('cyan_q_4', 4), ('black_q_5', 5)]
        # simple: q_name and q_maxsize as unpacked list
        emp.queue_cust_dict_std_create(*three_q_lst)

        assert len(emp.q_name_id_lst) == 5  # two_q_lst was rejected

    def test_queue_cust_dict_category_create(self):
        """Queue name is **category|queue_name** batch_1|audio_lg
        """
        emp = eisenmp.Mp()

        batch_1_audio_lg_max_3 = ('batch_1', 'audio_lg', 5)  # name is 'batch_1|audio_lg'
        emp.queue_cust_dict_category_create(batch_1_audio_lg_max_3)

        two_q_lst = [('batch_1', 'audio_lg', 5), ('batch_1', 'red_q_1', 1)]
        try:
            emp.queue_cust_dict_category_create(*two_q_lst)
        except ValueError:
            pass  # must fail, q name already exists

        three_q_lst = [('batch_1', 'orange_q_2', 2), ('batch_1', 'cyan_q_4', 4), ('batch_1', 'black_q_5', 5)]
        # category: q_category, q_name and q_maxsize as unpacked list
        emp.queue_cust_dict_category_create(*three_q_lst)

        assert len(emp.q_name_id_lst) == 5  # two_q_lst was rejected

    def test_run_proc(self):
        """
        run_proc
            updates kwargs with queue names and lists
            update kwargs with process start id START_SEQUENCE_NUM
            kwargs updates ProcEnv.kwargs_env to keep the values for test
            proc start target worker loader module
            proc reference in proc_list

        Problems so far
            (A)worker module loader is idle? How we check?
            (B)loader should !hang! in process_q loop and wait for stop,
            but we can not see a raise Error in another process, it seems

            (C)print_q is not open until we run emp.start(),
            (D)procs run in a separate process, we must wait loop for prints
            msg = 'worker_loader: No Worker Module to start - exit function'
        """
        emp = eisenmp.Mp()

        core_count = emp.core_count_get()  # how many physical cores on system
        # emp.run_proc()
        emp.start()  # contains emp.run_proc()
        # {key: proc start, value overwritten until core_count}
        assert emp.kwargs_env['START_SEQUENCE_NUM'] == core_count - 1  # core_count starts zero

    @staticmethod
    def coverage_fails_test_run_proc_wait_fail_worker_loader():  # pragma: no cover
        """Coverage fails to assign no cover attribute and breaks the test
        remove staticmethod if fixed

        msg = 'worker_loader: No Worker Module to start - exit function' not only displayed,
        but msg counted in print_q_box
        """
        emp = eisenmp.Mp()

        core_count = emp.core_count_get()  # how many physical cores on system
        # emp.run_proc()
        emp.start()  # contains emp.run_proc()
        # {key: proc start, value overwritten until core_count}
        assert emp.kwargs_env['START_SEQUENCE_NUM'] == core_count - 1  # core_count starts zero
        print(emp.proc_list)
        print(emp.kwargs_env)
        start = time.perf_counter()
        while 1:  # pragma: no cover
            end = round((time.perf_counter() - start))
            if end >= 15:  # pragma: no cover
                assert end <= 15
                break
            if len(emp.print_q_box) >= core_count:  # pragma: no cover
                break
