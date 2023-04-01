"""Compare string characteristics with 'opponent' str.
A timer shows periodically the amount of rows left.

"""

import time
from collections import defaultdict  # this time factory int to sum

import eisenmp.utils.eisenmp_utils as g_utils


def worker_entrance(toolbox):
    """
    - WORKER - Called in a loop.

    Start, Entry, Exit of this single process worker.
    We return True to get next list chunk, whatever object is in the rows.
    Fed from mp_input_q to our toolbox. toolbox is our work instance with queues,
    messages, list chunk, and work tools like language dictionary or hash list.

    toolbox.foo, gives also access to all attributes and values
    of the 'modConf.foo' instance, you have created
    """
    # don't need a dictionary in mp_tools_q, we get generator lists to reduce, find a valid word
    busy = workload_get(toolbox)
    list_reduce(toolbox)  # start worker function
    if not busy:
        return False
    # send_eta_data(toolbox)  # no data, pb list shrink, worker has timer
    return True


def workload_get(toolbox):
    """"""
    while 1:
        if not toolbox.mp_input_q.empty():
            toolbox.next_lst = toolbox.mp_input_q.get()
            toolbox.num_lists += 1
            break
    if toolbox.stop_msg in toolbox.next_lst:  # eisenmp.iterator_loop() informs stop, no more lists
        return False  # loop worker sends shutdown msg to next worker - generator is empty
    return True


def remove_header(toolbox):
    """Transport ticket with consecutive number.
    Remove if no recreation of order is necessary.
    Can reuse list for result, if rebuild order.

    Use self.header_msg attribute to overwrite default header string
    """
    # toolbox.mp_print_q.put(toolbox.next_lst[0])
    del toolbox.next_lst[0]  # remove header str


def list_reduce(toolbox):
    """Each Process takes only one chunk of the dict/list.
    Store char type [r, o, y] and count of search string.
    Compare string characteristics with 'opponent' str.
    Remove a word from list if char not in word or char type count does not match.
    Keep only matching words in the list.

    :params: str_to_comp: given str to search in wordlists/dict
    """
    busy = True
    if toolbox.stop_msg in toolbox.next_lst:  # inform we want exit
        busy = False
    remove_header(toolbox)

    str_to_comp = toolbox.str_permutation
    shrink_list = condense_list_from_mem_replace_spec_char(str_to_comp, toolbox.next_lst)
    word_list = shrink_list.copy()  # iter one and del other
    comp_typ_cnt_dict = char_type_count(str_to_comp)  # str compare

    start_time = time.perf_counter()
    for idx, word in enumerate(shrink_list):

        word_typ_cnt_dict = char_type_count(word)  # word in list to compare
        start_time = timer_show_rows_left(idx, start_time, word_list, toolbox)

        for char, char_count in comp_typ_cnt_dict.items():
            if char not in word_typ_cnt_dict.keys():
                if word in word_list:
                    word_list.remove(word)
            else:
                if word in word_list:
                    word_list.remove(word) if char_count != word_typ_cnt_dict[char] else None  # short circuit None last

    result_lst = [toolbox.result_header_proc,
                  word_list]
    toolbox.mp_output_q.put(result_lst)

    return busy


def char_type_count(a_str):
    """Char count to identify string 'opponents' with unequal char count, but same length.
    """
    c_dict = defaultdict(int)
    for char in a_str:
        c_dict[char] += 1  # {'r': 3, 'o': 1, 'c': 1}
    return c_dict


def condense_list_from_mem_replace_spec_char(str_to_comp, word_list):
    """A list already in mem.
    Reduce. Replace str chars only for shrink candidates.

    :params: str_to_comp: search str
    :params: word_list: list to shrink with strings only of size str_to_comp
    """
    ret_list = []
    for word in word_list:
        if len(word) == len(str_to_comp):
            replaced = g_utils.replace_special_char(word)
            ret_list.append(replaced)
    return ret_list


def timer_show_rows_left(idx, start_time, word_list, toolbox):
    """Better readable.
    Show rows left in list.
    """
    seconds = 5
    if not (idx % 1_000):  # reduce performance hit, if any
        end_time = int(round((time.perf_counter() - start_time)))
        if end_time >= seconds:
            toolbox.mp_print_q.put(f'{toolbox.worker_name}. ... {len(word_list):,} rows, list({toolbox.num_lists}) ')
            start_time = time.perf_counter()
    return start_time  # kept if
