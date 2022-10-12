# 1.selecionar arquivos python que contém um try-except
# 2.pecorrer a AST e verificar quais métodos possuem try-except

import ast
import pandas as pd
from dataset_generators_py.task1_dataset_generator import TryDatasetGenerator
from dataset_generators_py.task2_dataset_generator import ExceptDatasetGenerator

import miner_py_utils as mpu
from miner_py_utils import has_except

with open('test1.py') as f:
    tree = ast.parse('\n'.join(f.readlines()))
    func_defs = [f for f in ast.walk(tree) if isinstance(f, ast.FunctionDef)]
    func_defs_try_except = [f for f in func_defs if has_except(f)]

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
