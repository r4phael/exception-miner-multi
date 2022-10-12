import ast
import pandas as pd
from dataset_generators_py.task1_dataset_generator import TryDatasetGenerator
from dataset_generators_py.task2_dataset_generator import ExceptDatasetGenerator
from miner_py_utils import has_except


content = """def wait_for_grpc_server(server_process, client, subprocess_args, timeout=60):
    start_time = time.time()

    last_error = None

    while True:
        try:
            client.ping("")
            return
        except DagsterUserCodeUnreachableError:
            last_error = serializable_error_info_from_exc_info(sys.exc_info())

        if timeout > 0 and (time.time() - start_time > timeout):
            raise Exception(
                f"Timed out waiting for gRPC server to start after {timeout}s with arguments: \"{' '.join(subprocess_args)}\". Most recent connection error: {str(last_error)}"
            )

        if server_process.poll() != None:
            raise Exception(
                f"gRPC server exited with return code {server_process.returncode} while starting up with the command: \"{' '.join(subprocess_args)}\""
            )

        sleep(0.1)"""

# 1.selecionar arquivos python que contém um try-except
# 2.pecorrer a AST e verificar quais métodos possuem try-except

tree = ast.parse(content)
func_defs = [f for f in ast.walk(tree) if isinstance(f, ast.FunctionDef)]
func_defs_try_except = [f for f in func_defs if has_except(f)]

# 3. Dataset1 ->
# 	3.1 para cada método, tokeniza os statements do método;
# 	3.2 se o statement estiver dentro de um try, coloca 1, caso contrário 0;
dg1 = TryDatasetGenerator(func_defs_try_except)
df = pd.DataFrame(dg1.generate())
print(df)

# debug print
for _, fs in df.iterrows():
    for fdef in (zip(fs['labels'], fs['lines'])):
        print(fdef)
    print()

# 4. Dataset 2->
# 	4.1 para cada método, extrair or par {código do método, except):
# 		4.1.1 o código do método com o try sem o except;
# 		4.1.2 o código do except.
dg2 = ExceptDatasetGenerator(func_defs_try_except)
df = pd.DataFrame(dg2.generate())
print(df)

# debug print
print()
for _, fs in df.iterrows():
    print(fs['try'])
    print(fs['except'])
    print()
