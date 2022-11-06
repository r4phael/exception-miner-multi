from miner_py import get_datasets

files = [
    # '/home/eric3/git/exception-miner/output/py/results/django/_functions.py',
    # '/home/eric3/git/exception-miner/output/py/results/django/admin_list.py',
    # '/home/eric3/git/exception-miner/output/py/results/SublimeLinter/backend.py',
    # '/home/eric3/git/exception-miner/output/py/results/django/makemessages.py',
    # '/home/eric3/git/exception-miner/miner_py_src/tests/test1.py',
    # '/home/eric3/git/exception-miner/miner_py_src/tests/test2.py',
    # '/home/eric3/git/exception-miner/miner_py_src/tests/test3.py',
    # '/home/eric3/git/exception-miner/miner_py_src/tests/test4.py',
    '/home/eric3/git/exception-miner/miner_py_src/tests/test5.py'
]

task1, task2 = get_datasets(files)

# print(task1)
# mpu.print_pair_task1(task1)

# print(task2)
# mpu.print_pair_task2(task2)
