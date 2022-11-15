from miner_py import build_datasets
from miner_py_src.miner_py_utils import print_pair_task1

files = [
    # './miner_py_src/tests/test1.py',
    # './miner_py_src/tests/test2.py',
    # './miner_py_src/tests/test3.py',
    # './miner_py_src/tests/test4.py',
    './miner_py_src/tests/test5.py'
]

task1, task2 = build_datasets(files)
# save_datasets(task1, task2)

# print(task1)
# print_pair_task1(task1)

# print(task2)
# mpu.print_pair_task2(task2)
