from miner_py import get_datasets

files = [
    './miner_py_src/tests/test1.py',
    './miner_py_src/tests/test2.py',
    './miner_py_src/tests/test3.py',
    './miner_py_src/tests/test4.py',
    './miner_py_src/tests/test5.py'
]

task1, task2 = get_datasets(files)

# print(task1)
# mpu.print_pair_task1(task1)

# print(task2)
# mpu.print_pair_task2(task2)
