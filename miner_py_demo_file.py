from miner_py import build_datasets
import miner_py_src.miner_py_utils as mpu
from miner_py_src.stats import FileStats, TBLDStats, CBGDStats

file_stats = FileStats()
tbld_stats = TBLDStats()
cgbd_stats = CBGDStats()

files = [
    './miner_py_src/tests/test1.py',
    './miner_py_src/tests/test2.py',
    './miner_py_src/tests/test3.py',
    './miner_py_src/tests/test4.py',
    './miner_py_src/tests/test5.py',
    './miner_py_src/tests/test6.py',
    './miner_py_src/tests/bad_exception_handling.py',
]

task1, task2 = build_datasets(files, file_stats, tbld_stats, cgbd_stats)
# save_datasets(task1, task2)

print(task1)
mpu.print_pair_task1(task1)

print(task2)
mpu.print_pair_task2(task2)

print(file_stats)
print(tbld_stats)
print(cgbd_stats)
