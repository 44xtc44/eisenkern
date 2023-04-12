import time
import threading


class Result:
    """Finest results only here.

    """
    result_dict = {}

    def result_dict_update(self, key: str, id_result: tuple) -> None:
        """Sort results yourself.
        If something is wrong, you see one TID is not there.

        Tuple for simple extraction: id, result = result_dict['PRIME_NUM']
        {'PRIME_NUM': [(ticket_id, result_lst), (ticket_id, result_lst)]}

        :params: key: str name of the queue feeder 'header_msg' argument
        :params: result_value_t: tuple(_TID_0, result)
        """
        if key not in self.result_dict:
            self.result_dict[key] = []
        self.result_dict[key].append(id_result)


def consecutive_number():
    """Want a stamp on each list header.
    Used for Queue messages get() and put in box_dict[num] = msg
    Can rebuild original order if worker puts result in a list
    with same num as order list.
    """
    idx = 0
    while 1:
        yield idx
        idx += 1


def thread_shutdown_wait(*threads):
    """We return if none of the thread names are listed anymore.
    Blocks!

    :params: *threads: arbitrary list of thread names
    """
    busy = True
    while busy:
        names_list = [thread.name for thread in threading.enumerate()]
        busy = True if any([True for thread in threads if thread in names_list]) else False
        time.sleep(.1)
