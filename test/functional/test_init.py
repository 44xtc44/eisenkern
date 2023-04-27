import threading
import unittest
import eisenmp
import eisenmp.utils.eisenmp_constants as const


class TestInit(unittest.TestCase):
    """
    """
    def test_create_transport_ticket(self):
        """['fake_queue;_TID_0;']
        result can be stored as dict[fake_queue] = {_TID_1: foo, _TID_2: bar}
        """
        fake_queue = 'fake_queue'
        num_gen = (num for num in range(10))  # need only one num
        ticket_header_lst = eisenmp.create_transport_header(num_gen, q_name=fake_queue)
        assert ticket_header_lst == [fake_queue + ';' + const.TICKET_ID_PREFIX + f'{str(0)};']

    def test_q_feeder_loop(self):
        """need thread to grab input_q, must shut down after signal
        """
        emp = eisenmp.Mp()
        generator_items = 10
        work_load = 2
        worker_chunks = int((generator_items / work_load) + 1)  # int makes floor from float, plus stop msg
        fake_gen = (num for num in range(generator_items))
        emp.kwargs = {'generator': fake_gen, 'ROWS_MAX': 2}
        feeder_input_q = emp.kwargs['input_q'] = emp.mp_input_q
        q_name = eisenmp.q_name_get(emp.q_name_id_lst, feeder_input_q)
        assert q_name == 'mp_input_q (default)'

        threading.Thread(target=self.grab_from_q_feeder_loop,
                         args=(emp, worker_chunks), ).start()
        emp.q_feeder()

    @staticmethod
    def grab_from_q_feeder_loop(emp, worker_chunks):
        """leech q until empty
        no thread daemon - block main() until q empty
        generator empty, one stop msg added (+1)
        """
        idx = 0
        while 1:

            if not emp.mp_input_q.empty():
                lst = emp.mp_input_q.get()
                idx += 1
                if const.STOP_MSG in lst:
                    assert idx == worker_chunks
                    break  # generator is empty

    def test_reset(self):
        """"""
        emp = eisenmp.Mp()
        emp.all_threads_stop = True
        emp.begin_proc_shutdown = True

        emp.reset()
        assert emp.all_threads_stop is False
        assert emp.begin_proc_shutdown is False
