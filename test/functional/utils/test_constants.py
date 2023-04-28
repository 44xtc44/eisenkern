import unittest

import eisenmp.utils.eisenmp_constants as const


class TestConstants(unittest.TestCase):
    """
    """
    def test_constants(self):
        """
        """
        assert const.ROWS_MAX == 1_000
        assert const.PERF_HEADER_ETA == 'PERF_HEADER_ETA'
        assert const.STOP_MSG == 'STOP'
        assert const.STOP_CONFIRM == 'WORKER_STOPS'
        assert const.STOP_PROCESS == 'STOP_PROC'
        assert const.OUTPUT_HEADER == 'OUTPUT_HEADER'
        assert const.RESULTS_STORE is False
        assert const.PROCS_MAX is None
        assert const.RESULT_LABEL == 'add a "RESULT_LABEL" var'
        assert const.TICKET_ID_PREFIX == '_TID_'
        assert const.ALL_QUEUES_LIST == 'ALL_QUEUES_LIST'
