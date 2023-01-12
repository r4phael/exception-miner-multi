from utils import create_logger
from miner_py_src.split_dataset import save_task1_pkl, save_task2_onmt
from miner_py_src.miner_py_utils import (
    check_function_has_except_handler,
    check_function_has_nested_try,
    check_function_has_try,
    count_lines,
    is_bad_except_handling,
)
from miner_py_src.task2_dataset_generator import ExceptDatasetGenerator
from miner_py_src.task1_dataset_generator import TryDatasetGenerator
import argparse
import pandas as pd
import pathlib
import os
import shutil
import ast
from tqdm import tqdm

# from subprocess import call
from subprocess import call
from pydriller import Git
from random import sample, seed
from miner_py_src.stats import FileStats

seed(10)


logger = create_logger("exception_py_miner", "exception_py_miner.log")


# Functio to sum two


def fetch_repositories():
    projects = pd.read_csv("projects_py.csv", sep=",")

    if not os.path.exists("output/py/results"):
        os.makedirs("output/py/results")

    for index, row in projects.iterrows():
        # repo = Repository(row['repo'], clone_repo_to="projects")
        # commits_count = CommitsCount(path_to_repo= os.path.join('projects', row['repo']))
        # for commit in Repository(row['repo'], clone_repo_to="projects").traverse_commits():
        project = row["name"]
        files_with_try = []

        try:
            path = os.path.join(os.getcwd(), "projects/py/", project)
            git_cmd = "git clone {}.git --recursive {}".format(row["repo"], path)
            call(git_cmd, shell=True)
            gr = Git(path)
            logger.warning("Exception Miner: cloned project: {}".format(project))

        except Exception as e:
            logger.warning(
                "Exception Miner: error in project: {}, error: {}".format(
                    project, str(e)
                )
            )
            continue

        if not os.path.exists("output/py/results/{}".format(project)):
            os.mkdir("output/py/results/{}".format(project))

        files = [
            f for f in gr.files() if pathlib.Path(r"{0}".format(f)).suffix == ".py"
        ]
        for file in tqdm(files):

            print("File: {}".format(file))
            # print(os.path.basename(file))
            # shutil.copy(file, "except_file.py")
            # output_path = os.path.join(
            #     "output/py/files/{}".format(project), os.path.basename(file)
            # )
            try:
                with open(file, "rb") as f:
                    content = f.read()
                    tree = ast.parse(content)
                    # print(tree)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ExceptHandler):
                        print(
                            "###### File {0} in project {1} have exception: {2}.#######".format(
                                file, project, str(node)
                            )
                        )
                        f.close()
                        shutil.move(
                            file,
                            "output/py/results/{}/{}".format(
                                project, os.path.basename(file)
                            ),
                        )

                        files_with_try.append(file)

            except Exception as e:
                print(
                    f"###### Error!!! in project {project} and file: {file}. exception: {str(e)} ##########"
                )

        # print("Files with try {}".format(files_with_try))
        files_without_try = [f for f in files if f not in files_with_try]

        files_without_try = sample(
            files_without_try,
            len(files_with_try)
            if len(files_with_try) < len(files_without_try)
            else len(files_without_try),
        )

        # Write negative files inside
        write_files(files=files_without_try, project=project)

        # Remove repos from disk
        shutil.rmtree(os.path.join(os.getcwd(), "projects/py/", project))


def write_files(files, project):
    for file in files:
        if os.path.basename(file) not in [
            "__init__.py",
            "__main__.py",
            "setup.py",
            "test.py",
            "tests.py",
            "runtests.py",
        ]:
            try:
                with open(file, "rb") as f:
                    shutil.move(
                        file,
                        "output/py/results/{}/{}".format(
                            project, os.path.basename(file)
                        ),
                    )
            except FileNotFoundError as e:
                print(
                    f"###### Error!!! to locate file in {project} and file: {file}. exception: {str(e)} ##########"
                )


def get_files():
    paths = pathlib.Path(r"output/py/results/").glob("**/*.py")
    files = [x for x in paths if x.is_file()]
    return files


def save_datasets(task1: pd.DataFrame, task2: pd.DataFrame):
    print("Saving pickle datasets ...")

    os.makedirs("output/py/data", exist_ok=True)

    save_task1_pkl(task1)
    save_task2_onmt(task2)


def preprocess():
    files = get_files()

    task1, task2 = build_datasets(files)

    # print(task1)
    # print(task2)
    save_datasets(task1, task2)


def build_datasets(files):
    filestats = FileStats()
    task1 = pd.DataFrame()
    task2 = pd.DataFrame()

    pbar = tqdm(files)

    func_defs = []
    for file in pbar:
        pbar.set_description(f"Processing {str(file)[-40:].ljust(40)}")
        # 1.selecionar arquivos python que contém um try-except
        # 2.pecorrer a AST e verificar quais métodos possuem try-except
        with open(file, "r") as f:
            try:
                content = f.read()
                tree = ast.parse(content)
            except SyntaxError as ex:
                print(f"###### SyntaxError Error!!! file: {file}.\n{str(ex)}")
            except UnicodeDecodeError as ex:
                print(f"###### UnicodeDecodeError Error!!! file: {file}.\n{str(ex)}")
            else:
                for f in ast.walk(tree):
                    if not isinstance(f, ast.FunctionDef):
                        continue

                    if 7 < count_lines(f, file) <= 100:
                        func_defs.append(f)

                    filestats.metrics(f, file)
    filestats.num_files = len(files)
    filestats.num_functions = len(func_defs)
    print(filestats)

    func_defs_try_except = [
        f
        for f in func_defs
        if check_function_has_except_handler(f) and not check_function_has_nested_try(f)
    ]

    negative_samples = [f for f in func_defs if check_function_has_try(f) == 0]
    try:
        func_defs_no_try = sample(negative_samples, len(func_defs_try_except))
    except ValueError:
        func_defs_no_try = negative_samples

    # 3. Dataset1 ->
    # 	3.1 para cada método, tokeniza os statements do método;
    # 	3.2 se o statement estiver dentro de um try, coloca 1, caso contrário 0;
    dg1 = TryDatasetGenerator(func_defs_try_except + func_defs_no_try)
    task1 = dg1.generate()

    # 4. Dataset 2->
    # 	4.1 para cada método, extrair or par {código do método, except):
    # 		4.1.1 o código do método com o try sem o except;
    # 		4.1.2 o código do except.
    dg2 = ExceptDatasetGenerator(func_defs_try_except)
    task2 = pd.DataFrame(dg2.generate())
    return task1, task2


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Repository miner and preprocess.")
    parser.add_argument(
        "--mode",
        type=str,
        help="fetch repositories or preprocess",
        required=False,
        default=None,
        choices=["fetch", "preprocess"],
    )

    args = parser.parse_args()

    if args.mode == "fetch":
        fetch_repositories()
    elif args.mode == "preprocess":
        preprocess()
    else:
        fetch_repositories()
        preprocess()
