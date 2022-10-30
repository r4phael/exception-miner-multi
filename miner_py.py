import argparse
import pandas as pd
import pathlib
import os
import shutil
import ast
from tqdm import tqdm
#from subprocess import call
from subprocess import PIPE, run, call
from pydriller import Git
from miner_py_src.task1_dataset_generator import TryDatasetGenerator
from miner_py_src.task2_dataset_generator import ExceptDatasetGenerator
from miner_py_src.miner_py_utils import has_except, has_nested_catch
from miner_py_src.split_dataset import save_task1_pkl, save_task2_pkl
from utils import create_logger

logger = create_logger("exception_py_miner", "exception_py_miner.log")


def fetch_repositories():
    projects = pd.read_csv("projects_py.csv", sep=",")

    if not os.path.exists('output/py/results'):
        os.makedirs('output/py/results')

    for index, row in projects.iterrows():
        #repo = Repository(row['repo'], clone_repo_to="projects")
        #commits_count = CommitsCount(path_to_repo= os.path.join('projects', row['repo']))
        # for commit in Repository(row['repo'], clone_repo_to="projects").traverse_commits():
        project = row['name']

        try:
            path = os.path.join(os.getcwd(), 'projects/py/', project)
            git_cmd = "git clone {}.git --recursive {}".format(
                row['repo'], path)
            call(git_cmd, shell=True)
            gr = Git(path)
            logger.warning(
                "Exception Miner: cloned project: {}".format(project))

        except Exception as e:
            logger.warning(
                "Exception Miner: error in project: {}, error: {}".format(project, str(e)))

        if not os.path.exists("output/py/results/{}".format(project)):
            os.mkdir("output/py/results/{}".format(project))

        files = gr.files()
        for file in tqdm(files):
            #file = 'home/r4ph21/desenv/exception-miner/projects/py/modern-python-101/03_Flow_Control/print_my_name.py'
            if (pathlib.Path(r'{0}'.format(file)).suffix == ".py"):
                print(file)
                # print(os.path.basename(file))
                shutil.copy(file, "except_file.py")
                output_path = os.path.join(
                    "output/py/files/{}".format(project), os.path.basename(file))
                try:
                    with open(file, "rb") as f:
                        content = f.read()
                        tree = ast.parse(content)
                        # print(tree)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ExceptHandler):
                            print("###### File {0} in project {1} have exception: {2}.#######".format(
                                file, project, str(node)))
                            f.close()
                            shutil.move(
                                file, "output/py/results/{}/{}".format(project, os.path.basename(file)))

                except Exception as e:
                    f.close()
                    print(
                        f"###### Error!!! in project {project} and file: {file}. exception: {str(e)} ##########")


def preprocess():
    paths = pathlib.Path(r'output/py/results/').glob('**/*.py')
    files = [x for x in paths if x.is_file()]

    task1 = pd.DataFrame()
    task2 = pd.DataFrame()

    pbar = tqdm(files)
    for file in pbar:
        pbar.set_description(f"Processing {str(file)[-40:].ljust(40)}")
        # 1.selecionar arquivos python que contém um try-except
        # 2.pecorrer a AST e verificar quais métodos possuem try-except
        with open(file) as f:
            content = f.read()
            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                print(
                    f"###### SyntaxError Error!!! file: {file}.\n{str(e)}")
                continue
            func_defs = [f for f in ast.walk(
                tree) if isinstance(f, ast.FunctionDef)]
            func_defs_try_except = [f for f in func_defs if has_except(
                f) and not has_nested_catch(f)]

            # 3. Dataset1 ->
            # 	3.1 para cada método, tokeniza os statements do método;
            # 	3.2 se o statement estiver dentro de um try, coloca 1, caso contrário 0;
            dg1 = TryDatasetGenerator(func_defs_try_except)
            task1 = pd.concat([task1, pd.DataFrame(dg1.generate())])

            # 4. Dataset 2->
            # 	4.1 para cada método, extrair or par {código do método, except):
            # 		4.1.1 o código do método com o try sem o except;
            # 		4.1.2 o código do except.
            dg2 = ExceptDatasetGenerator(func_defs_try_except)
            task2 = pd.concat([task2, pd.DataFrame(dg2.generate())])

    print(task1)
    print(task2)
    print('Saving pickle datasets ...')

    os.makedirs('output/py/data', exist_ok=True)
    save_task1_pkl(task1)
    save_task2_pkl(task2)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Repository miner and preprocess.')
    parser.add_argument(
        '--mode', type=str, help='fetch repositories or preprocess',
        required=False, default=None, choices=['fetch', 'preprocess'])

    args = parser.parse_args()

    if args.mode == 'fetch':
        fetch_repositories()
    elif args.mode == 'preprocess':
        preprocess()
    else:
        fetch_repositories()
        preprocess()
