# eisenmp
#########
 
Python 3.7

`Multiprocessor <https://en.wikipedia.org/wiki/Multiprocessing>`_
`Framework <https://en.wikipedia.org/wiki/Software_framework>`_ for Server and Mobiles

Forget about pools, swim in the sea.

Features:

* Create **uniform** multiprocess programs for your projects
* Calculate your Python generator output on _every_ CPU core
* Worker **module_loader** decouples your Worker imports from Main()
* **auto Exit** of worker and process
* Start methods, **spawn**, **fork** and **forkserver**
* Create **port groups** on CPU cores and connect network adapters
* Process **START_SEQUENCE_NUM** Worker on a CPU core can grab a specific queue 0=red_q, 1=blue_q, 2=yellow_q
* **Categories of Queues**, read them with **all custom vars** in a worker **ToolBox** dictionary
* Visit the features above in the
`Examples gitHub repository <https://github.com/44xtc44/eisenmp_examples>`_,
or get the `PyPi package <https://pypi.org/project/eisenmp-examples/>`_,
run **eisenmp_url** simpleHTTP Ajax server
* All scenarios run on **reusable Template Modules**. Enjoy the descriptions and discover.
* no libraries, light weight; (Linux, Windows)

## How it works
You write two functions and two modules.
Let's call 'em **Generator.py** and **Worker.py**.

1. Generator.py starts a new process, _but_ the target is **module_loader.py** (loader).
2. loader imports your (independent) Worker.py module from file system. 
This makes sure that only imports of the worker.py module are loaded, without side effects.
3. loader sits in a loop and calls your Worker.py entry function endless. Until there is no more work in the queues.
This loop keeps the process alive.
4. **q_feeder** iterator sends a STOP Worker message with the last chunk. Your Worker reads STOP, return False and exit. 
5. The **module loader** then puts a STOP Worker message in all other input queues.
Loader runs idle and awaits the internal STOP Process message. **Next** Worker reads STOP, exit ...

Default ``six Queues``
- ``Input`` worker lists, ``Output`` result and stop lists, ``Process`` shutdown
- ``Tools``, ``Print``, ``Info``

### In detail:

Generator - iterator chunks on every CPU core:
- `Generator yield <https://docs.python.org/3/reference/expressions.html#yieldexpr>`_
or 
[(expression)](https://peps.python.org/pep-0289/)
output 1, 2, 3, 4, 5 ➜ eisenmp iterator list [ [1,2] [3,4] [5] ] ➜ **NUM_ROWS** chunks for your Worker
- (A) Mngr(): Import and instantiate **eisenmp**. Register the worker in (also) a list. 
- (B) Mngr(): Assign Worker load and process count.
- (C) Mngr(): Call **iterator** run_q_feeder(generator=Mngr generator)
- (D) Wkr(): Loop over **NUM_ROWS** list chunks. Return False to **auto exit worker and process**, or get next chunk 
`Examples gitHub repository <https://github.com/44xtc44/eisenmp_examples>`_,
or get the `PyPi package <https://pypi.org/project/eisenmp-examples/>`_

One Server (or more) on every CPU core:
- (A) Mngr(): Import and instantiate **eisenmp**. Register the worker module in a list.
- (D.1) Wkr(): The **worker** starts **ONE** server, blocks (run_forever on IP: foo port: 42) and serves whatever
- (D.2) Wkr(): The **worker** starts **MANY** server. Server start call must be threaded, set **STOP_MSG_DISABLE=True**
- Server read queues: Follow the Generator todo
`Examples gitHub repository <https://github.com/44xtc44/eisenmp_examples>`_,
or get the `PyPi package <https://pypi.org/project/eisenmp-examples/>`_

Port groups:
- Map **toolbox.WORKER_ID**'s ➜ to server ports on CPU cores ➜ to an IP address, 
`Examples gitHub repository <https://github.com/44xtc44/eisenmp_examples>`_,
or get the `PyPi package <https://pypi.org/project/eisenmp-examples/>`_

### ready to use:
- **run_q_feeder()** iterator lists get a **serial number** header to recreate the original order of chunks
- **mp_tools_q** for big tools stuff delivery to every single Worker proc module;
It may be a 27GB rainbow table; See the bruteforce (small) example, please
- Output **can** be stored if **RESULTS_STORE** is set in config


## Issues
eisenmp can run on Python 3.6 (Ubuntu test), but not the samples.

## How to run the examples?
Clone the repo [Examples gitHub](https://github.com/44xtc44/eisenmp_examples) and ``run an eisenmp_exa_...``.

Brute force cracks strings of an online-game alphabet salad quest. 

    .. read wordlist .\lang_dictionaries\ger\german.dic
    .. read wordlist .\lang_dictionaries\eng\words.txt

	[BRUTE_FORCE]	cfhhilorrs

    Create processes. Default: proc/CPU core
    0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 
    
    ... proc Process-7 ... rohrschilf
    ... proc Process-14 ... rohrschilf
    ... proc Process-16 ... rohrschilf
    ... proc Process-7 ... rohrschilf
    ... proc Process-13 ... schilfrohr
    ... proc Process-13 ... schilfrohr
    ... proc Process-11 ... schilfrohr
    ... proc Process-11 ... schilfrohr

	generator empty, run time iterator 5 seconds

	exit WORKER 15
	exit WORKER 16
	exit WORKER 2
	exit WORKER 10
	exit WORKER 11
	exit WORKER 12
	exit WORKER 8
	exit WORKER 3
	exit WORKER 4
	exit WORKER 6
	exit WORKER 14
	exit WORKER 5
	exit WORKER 7
	exit WORKER 13
	exit WORKER 1
	exit WORKER 9

    --- Result for [CFHHILORRS]---
    
     rohrschilf
    
     schilfrohr

    --- END ---

	Processes are down.
    BF Time in sec: 12
    
    Process finished with exit code 0

    Inbuild example, assert a scrambled string. Use brute force or condensing.
    We use an english (.6M) plus a german (2M) wordlist and make a dictionary of it. To gain more read speed.
    (A) len(str) <=  11, combined brute force dictionary attack with a permutation generator. itertool prod. duplicates
        Permutation lists grow very fast, reaching Terabyte size.
    (B) len(str) >=  12, pre reduce a len(str) list. Kick out words which are not matching char type and count.

`eisenmp` uses Pythons permutation generator
 `itertools <https://docs.python.org/3/library/itertools.html?highlight=itertools.permutations#itertools.permutations>`_
for the brute force attack example.

    Another example downloads a large list and calculates average for one column.
    Python CSV extracts the column and we calculate the average with the assigned number
    of Porcesses/CPU cores. It can be more processes than CPU cores, if it makes sense.


- large lists https://www.stats.govt.nz/large-datasets/csv-files-for-download/ Crown copyright ©. 
All material Stats NZ produces is protected by Crown copyright.
Creative Commons Attribution 4.0 International licence.
- German dict https://sourceforge.net/projects/germandict/. License Public Domain
- English dict Copyright (c) J Ross Beresford 1993-1999. All Rights Reserved.
- ORM Flask-SQLAlchemy https://pypi.org/project/Flask-SQLAlchemy-Project-Template/ License MIT 44xtc44

Cheers
