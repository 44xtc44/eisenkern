# eisenmp
 
Python 3.7 [Multiprocess](https://en.wikipedia.org/wiki/Multiprocessing) 
[Framework](https://en.wikipedia.org/wiki/Software_framework) for Server and Mobiles 

Features:

* Load modules from Network or FS. Load **multi, independent and before a worker**
* Run every Python generator on _every_ CPU core
* Process Manager, Load a fixed number of server or container into each process
* Build port groups with CPU cores and network adapters
* Create **categories of Queues**, read them with **all custom vars** in a **ToolBox** dictionary, used by the worker
* See the features above in the
[Examples repository](https://github.com/44xtc44/eisenmp_examples) 
* All scenarios follow the **Template style** and have descriptions
* no libraries, light weight; (Linux, Windows)

Generator - iterator chunks on every CPU core:
- [Generator yield](https://docs.python.org/3/reference/expressions.html#yieldexpr)
or 
[(expression)](https://peps.python.org/pep-0289/)
output 1, 2, 3, 4, 5 ➜ [ [1,2] [3,4] [5] ] eisenmp iterator list ➜ chunks for your Worker
- (A) Mngr(): Import and instantiate **eisenmp**. Register the worker in (also) a list. 
- (B) Mngr(): Assign Worker load and process count.
- (C) Mngr(): Call **iterator** run_q_feeder(generator=Mngr generator)
- (D) Wkr(): Loop over load count list chunks. Return False to **auto exit worker and process**, or get next chunk 
[Examples](https://github.com/44xtc44/eisenmp_examples)

One Server (or more) on every CPU core:
- (A) Mngr(): Import and instantiate **eisenmp**. Register the worker module in a list.
- (D.1) Wkr(): The **worker** starts **ONE** server, blocks (run_forever on IP: foo port: 42) and serves whatever
- (D.2) Wkr(): The **worker** starts **MANY** server. Server start call must be threaded, set **stop_msg_disable=True**
- Server read queues: Follow the Generator todo
[Examples](https://github.com/44xtc44/eisenmp_examples)

Port groups:
- Map **toolbox.worker_id**'s ➜ to server ports on CPU cores ➜ to an IP address, 
[Examples](https://github.com/44xtc44/eisenmp_examples)

## How it works
You need one **Call (Mngr)** and one **Worker** fun() in the module.
- class ModuleConfiguration, instance **modConf** collects content of default and custom variables, data types 
- **modConf** updates eisenmp with its own instance dictionary 
- Use default or create **custom Queue**s; They can own category names for easy deployment
- eisenmp threaded method **run_q_feeder** can be called multiple times to fill the worker Queues with generator output

The loader imports **arbitrary** modules. Iterator loop threads (option) put work chunks in queues.
The **first registered module function**, the worker, is called in an **endless loop**, as long as it exits after 
each own cycle. It is the **last loaded module**.

Following modules in the register list (LIFO) execute a thread start function to not block the Worker module. 
They may control the worker and have access to its started instances references (offset address). 
main(), Parent Process has no access in 
[spawned](https://docs.python.org/3/library/multiprocessing.html?highlight=spawn#spawn) Child processes.

See also the watchdog threaded module in the [Examples](https://github.com/44xtc44/eisenmp_examples) , please.


Default ``six Queues``
- ``Input`` serial number header, ``Output`` result and stop lists w. header, ``Process`` shutdown
- ``Tools``, ``Print``, ``Info``

Default means **ready to use**:
- **mp_input_q** lists have a header with a **serial number** to be able to recreate the original order of chunks
- **mp_tools_q** for big tools stuff delivery to every single Worker proc module;
It may be a 27GB rainbow table; See the bruteforce (small) example, please
- Output **can** be stored if **store_result** is set in config

## Issues
eisenmp can run on Python 3.6 (Ubuntu test), but not the samples. Crash of Flask and SqlAlchemy

## How to run the examples?
Clone the repo [Examples](https://github.com/44xtc44/eisenmp_examples) and ``run an eisenmp_exa_...``.

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
 [itertools](https://docs.python.org/3/library/itertools.html?highlight=itertools.permutations#itertools.permutations)
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
