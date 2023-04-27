import unittest

import eisenmp.utils.eisenmp_utils as e_utils


class TestUtils(unittest.TestCase):
    """ thread_shutdown_wait() is tested in TestColl already
    """
    def test_consecutive_number(self):
        """
        """
        a_lst = [0, 1, 2, 3, 4]
        b_lst = []
        generator = e_utils.consecutive_number()
        for idx in range(5):
            b_lst.append(next(generator))
        assert a_lst == b_lst

    def test_result_dict_update(self):
        """

        :params: res_val: tuple
        """
        queue_header_msg = 'fakeQ'
        res_val = ('foo', 'bar', 42)
        res = e_utils.Result()
        res.result_dict_update(queue_header_msg, res_val)
        a_lst = res.result_dict[queue_header_msg]
        assert a_lst == [res_val]
