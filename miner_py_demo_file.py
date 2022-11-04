# 1.selecionar arquivos python que contém um try-except
# 2.pecorrer a AST e verificar quais métodos possuem try-except

import ast
import pandas as pd
from miner_py_src.task1_dataset_generator import TryDatasetGenerator
from miner_py_src.task2_dataset_generator import ExceptDatasetGenerator
from random import sample

import miner_py_src.miner_py_utils as mpu
from miner_py_src.miner_py_utils import has_except, has_nested_catch, has_try

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

func_defs = []
for file in files:
    with open(file) as f:
        content = f.read()
        try:
            tree = ast.parse(content)
        except SyntaxError as ex:
            print(f"###### SyntaxError Error!!! file: {file}.\n{str(ex)}")
            continue
        func_defs += [f for f in ast.walk(
            tree) if isinstance(f, ast.FunctionDef)]

    func_defs_try_except = [f for f in func_defs if has_except(
        f) and not has_nested_catch(f)]

    negative_samples = [f for f in func_defs if not has_try(f)]
    try:
        func_defs_no_try = sample(
            negative_samples,
            len(func_defs_try_except))
    except ValueError:
        func_defs_no_try = negative_samples

    # 3. Dataset1 ->
    # 	3.1 para cada método, tokeniza os statements do método;
    # 	3.2 se o statement estiver dentro de um try, coloca 1, caso contrário 0;
    dg1 = TryDatasetGenerator(func_defs_try_except + func_defs_no_try)
    task1 = pd.DataFrame(dg1.generate())
    print(task1)
    mpu.print_pair_task1(task1)

    # 4. Dataset 2->
    # 	4.1 para cada método, extrair or par {código do método, except):
    # 		4.1.1 o código do método com o try sem o except;
    # 		4.1.2 o código do except.
    dg2 = ExceptDatasetGenerator(func_defs_try_except)
    task2 = pd.DataFrame(dg2.generate())
    print(task2)
    mpu.print_pair_task2(task2)
