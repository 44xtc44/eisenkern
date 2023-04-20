Manager
#######

| Ease Bruteforce attacks.
| Use of all CPU cores on Android devices with Python .so modules.

You feed:

* location of modules to load
* number of processes and workload for a process
* custom queues and variables for the worker

Create instance:

::

    emp = eisen.Mp()

Generator
~~~~~~~~~~

| Spread generator load over multiple processes with an in-build iterator.

Queue creation methods
~~~~~~~~~~~~~~~~~~~~~~
| Eases the creation and debugging of multiple queues.
| Standard Queue name: ``queue_cust_dict_std_create``
| Category plus Queue name: ``queue_cust_dict_category_create``

::

    blue_q_7_max_3 = ('blue_q_7', 3)
    # simple: q_name and q_maxsize as unpacked list
    emp.queue_cust_dict_std_create(*blue_q_7_max_3)

    cat_1_input_q_3_max_10 = ('category_1', 'input_q_3', 10)
    # category plus name: q_category, q_name and q_maxsize as unpacked list
    emp.queue_cust_dict_category_create(*cat_1_input_q_3_max_10)


Queue list
----------

| Find Queues in ``q_name_id_lst`` list. Find queue names via object id, object reference or vice versa.

::

    emp = eisen.Mp()
    emp.q_name_id_lst

    # queue tuple (name, id, q_ref), all custom created queues will be appended
    self.q_name_id_lst = [('mp_input_q (default)', id(self.mp_input_q), self.mp_input_q)]

kwargs
~~~~~~~~~~~

| eisenmp heavily uses kwargs dictionary as a container (worker toolbox).
| Custom variables, lists, objects created in the modConf instance are available for the worker module.


Which information needs eisenmp?
********************************

eisenmp needs information about process count, each process workload and start method.

| A ``ModuleConfiguration`` class is used to collect information, variables and data for the worker module.
| A class instance for :ref:`Worker data variables` is created to store all the information and make it
| also available within the manager module.

Worker Loader
~~~~~~~~~~~~~

| eisenmp worker module loader list reveals the modules to load. Can load independent from Main() and multiple modules.
| Modules are collected in a `worker_modules` list. Load order is (LIFO) last in first out.
| First worker module is loaded last and is allowed to block the loader loop.
| All other modules must start threaded.

::

    class ModuleConfiguration:  # name your own class and feed eisenmp with the dict

        template_module = {
            'WORKER_PATH': os.path.join(dir_name, 'worker', 'eisenmp_exa_wrk_double.py'),
            'WORKER_REF': 'worker_entrance',
        }
        watchdog_module = {
            'WORKER_PATH': os.path.join(os.path.dirname(dir_name), 'worker', 'eisenmp_exa_wrk_watchdog.py'),
            'WORKER_REF': 'mp_start_show_threads',
        }

        def __init__(self):

            self.worker_modules = [  # in-bld-res
                self.template_module,  # other modules must start threaded, else we hang
                self.watchdog_module  # second; thread function call mandatory, last module loaded first
            ]


Worker data variables
~~~~~~~~~~~~~~~~~~~~~

| Default process start method is `spawn`. You can only read parent process values, you have preserved in kwargs.
| `spawn` means all references of in-build datatypes are lost in the child process.
| The offset start address pointer of the parent object is not accessible in the child.

| `spawn` reading 3rd party API lists and dictionaries is ok. Updating is possible *but* you update a black hole.
| Use Module communication sparingly and directly via pipes or a (SQLite) database. Python shared manager is utter slow.


::

            # Multiprocess vars - override default
            self.NUM_PROCS = 2  # your process count, each 'batch' on one CPU core, default is None: one proc/CPU core
            self.NUM_ROWS = 3  # your workload spread, list (generator items) to calc in one loop, default None: 1_000
            self.RESULTS_STORE = True  # keep in dictionary, will crash the system if store GB network chunks in mem
            self.RESULTS_PRINT = True  # result rows of output are collected in a list, display if processes are stopped
            self.RESULT_LABEL = 'fake production of audio and video for WHO studios'  # RESULT_LABEL for RESULTS_PRINT
            self.RESULTS_DICT_PRINT = True  # shows content of results dict with ticket numbers, check tickets
            # self.START_METHOD = 'fork'  # 'spawn' is default if unused; also use 'forkserver' or 'fork' on Unix only

            # work to do
            self.sleep_time = 20  # watchdog
            self.num_of_lists = 0  # worker lists done counter


| Worker data information is stored in ``modConf`` instance during configuration phase.

::

    modConf = ModuleConfiguration()  # Accessible in the manager and worker module.


eisenmp Instance
~~~~~~~~~~~~~~~~

``modConf`` instance dictionary is dumped into eisenmp. Means ``all attributes will be keys`` in kwargs.

::

    emp = eisenmp.Mp()
    emp.start(**modConf.__dict__)  # create processes, load worker mods, start threads (output_p coll, info)

Example

::

    def manager_entry():
        """
        - Generator - One time execution.

        Divide workload between processes / CPU
        -
        """
        q_cat_name_maxsize = [
            # q_category, q_name, q_maxsize; find your 100 Queues in the debugger, toolbox
            ('batch_1', 'audio_lg', 5),  # queues for batch_1
            ('batch_1', 'video_in', 1),  # dict avail. in worker module: toolbox.batch_1['video_in'].get()
            ('batch_7', 'audio_lg', 3),  # queues for batch_7
            ('batch_7', 'video_in', 1)
        ]
        emp = eisenmp.Mp()

        # create custom queues with category and name
        emp.queue_cust_dict_category_create(*q_cat_name_maxsize)  # create queues, store in {custom} {category} dict

        audio_q_b1 = emp.queue_cust_dict_cat['batch_1']['audio_lg']  # USE Queue:
        video_q_b1 = emp.queue_cust_dict_cat['batch_1']['video_in']  # worker module: toolbox.batch_1['video_in'].get()
        audio_q_b7 = emp.queue_cust_dict_cat['batch_7']['audio_lg']
        video_q_b7 = emp.queue_cust_dict_cat['batch_7']['video_in']  # toolbox.batch_7['video_in'].get()

        emp.start(**modConf.__dict__)  # create processes, load worker mods, start threads (output_p coll, info)
        emp.run_q_feeder(generator=audio_generator_batch_1(), input_q=audio_q_b1)
        emp.run_q_feeder(generator=video_generator_batch_1(), input_q=video_q_b1)
        emp.run_q_feeder(generator=audio_generator_batch_7(), input_q=audio_q_b7)
        emp.run_q_feeder(generator=video_generator_batch_7(), input_q=video_q_b7)

        return emp