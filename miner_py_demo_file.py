# 1.selecionar arquivos python que contém um try-except
# 2.pecorrer a AST e verificar quais métodos possuem try-except

import ast
import pandas as pd
from miner_py_src.task1_dataset_generator import TryDatasetGenerator
from miner_py_src.task2_dataset_generator import ExceptDatasetGenerator

import miner_py_src.miner_py_utils as mpu
from miner_py_src.miner_py_utils import has_except, has_nested_catch

# file = '/home/eric3/git/exception-miner/output/py/results/django/_functions.py'
# file = '/home/eric3/git/exception-miner/output/py/results/django/admin_list.py'
# file = '/home/eric3/git/exception-miner/output/py/results/SublimeLinter/backend.py'
# file = '/home/eric3/git/exception-miner/output/py/results/django/makemessages.py'
# file = '/home/eric3/git/exception-miner/miner_py_src/tests/test1.py'
file = '/home/eric3/git/exception-miner/miner_py_src/tests/test2.py'

with open(file) as f:
    tree = ast.parse('\n'.join(f.readlines()))
    func_defs = [f for f in ast.walk(tree) if isinstance(f, ast.FunctionDef)]
    func_defs_try_except = [f for f in func_defs if has_except(
        f) and not has_nested_catch(f)]

    # 3. Dataset1 ->
    # 	3.1 para cada método, tokeniza os statements do método;
    # 	3.2 se o statement estiver dentro de um try, coloca 1, caso contrário 0;
    dg1 = TryDatasetGenerator(func_defs_try_except)
    df = pd.DataFrame(dg1.generate())
    print(df)
    mpu.print_pair_task1(df)

    # 4. Dataset 2->
    # 	4.1 para cada método, extrair or par {código do método, except):
    # 		4.1.1 o código do método com o try sem o except;
    # 		4.1.2 o código do except.
    dg2 = ExceptDatasetGenerator(func_defs_try_except)
    df = pd.DataFrame(dg2.generate())
    print(df)
    mpu.print_pair_task2(df)
