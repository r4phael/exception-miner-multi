# 1.selecionar arquivos python que contém um try-except
# 2.pecorrer a AST e verificar quais métodos possuem try-except

import ast
import pandas as pd
from miner_py_src.task1_dataset_generator import TryDatasetGenerator
from miner_py_src.task2_dataset_generator import ExceptDatasetGenerator
from random import sample

import miner_py_src.miner_py_utils as mpu
from miner_py_src.miner_py_utils import has_except, has_nested_catch, has_try

from miner_py import get_datasets

files = [
    # '/home/eric3/git/exception-miner/output/py/results/django/_functions.py',
    # '/home/eric3/git/exception-miner/output/py/results/django/admin_list.py',
    # '/home/eric3/git/exception-miner/output/py/results/SublimeLinter/backend.py',
    # '/home/eric3/git/exception-miner/output/py/results/django/makemessages.py',
    # '/home/eric3/git/exception-miner/miner_py_src/tests/test1.py',
    # '/home/eric3/git/exception-miner/miner_py_src/tests/test2.py',
    # '/home/eric3/git/exception-miner/miner_py_src/tests/test3.py',
    '/home/eric3/git/exception-miner/miner_py_src/tests/test4.py'
]

task1, task2 = get_datasets(files)

print(task1)
mpu.print_pair_task1(task1)

print(task2)
mpu.print_pair_task2(task2)
