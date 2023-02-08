from subprocess import PIPE, run, call
import pandas as pd
import pathlib
import os, shutil
import json
from typing import List

from tqdm import tqdm

from pydriller import Git
from utils import create_logger
from miner_py_src.tree_sitter_lang import parser as tree_sitter_parser
from tree_sitter.binding import Node
from miner_py_src.stats import FileStats

from miner_py_src.miner_py_utils import (
    check_function_has_except_handler,
    check_function_has_nested_try,
    check_function_has_try,
    count_lines_of_function_body,
    get_function_defs,
    get_function_def,
    is_try_except_pass,
    is_bad_exception_handling,
)

logger = create_logger("exception_miner", "exception_miner.log")


def fetch_repositories(project):

    # projects = pd.read_csv("projects.csv", sep=",")
    # for index, row in projects.iterrows():
    # repo = Repository(row['repo'], clone_repo_to="projects")
    # for commit in Repository(row['repo'], clone_repo_to="projects").traverse_commits():
    # project = row["name"]

    if not os.path.exists("output/pytlint"):
        os.mkdir("output/pytlint")

    if not os.path.exists(f"output/pytlint/{project}"):
        os.mkdir(f"output/pytlint/{project}")

    try:
        path = os.path.join(os.getcwd(), "projects/py", project)
        # git_cmd = "git clone {}.git --recursive {}".format(row["repo"], path)
        # call(git_cmd, shell=True)
        gr = Git(path)
        logger.warning("Exception Miner: cloned project: {}".format(project))

        files = [
            f
            for f in gr.files()
            if pathlib.Path(rf"{f}").suffix == ".py" and not os.path.islink(f)
        ]

        return files

    except Exception as ex:
        logger.warning(
            "Exception Miner: error in project: {}, error: {}".format(project, str(ex))
        )


def collect_smells(files, project):
    for file in tqdm(files):
        if pathlib.Path(file).suffix == ".py":
            # print(file)
            # print(os.path.basename(file))
            output_path = os.path.join(
                "output/files/{}".format(project), os.path.basename(file)
            )
            try:
                print(file)
                command = "pylint {0} -v --output {1} --output-format json --disable=all --enable {2}".format(
                    file,
                    f"output/pytlint/{project}/{os.path.basename(file)}.json",
                    "exceptions",
                    # "E0701,E0702,E0704,E0710,E0711,E0712,W0702,W0718,W0705,W0706,W0707,W0711,W0715,W0716,W0719",
                    # os.path.dirname(file),
                    # os.path.basename(file),
                )
                run([command], shell=True, executable="/bin/bash", stdout=PIPE)

                # open json file a get if there is empty list, if empty list, delete file, if not empty list, keep file:
                with open(
                    f"output/pytlint/{project}/{os.path.basename(file)}.json", "r"
                ) as json_file:
                    data = json.load(json_file)
                    if data == []:
                        os.remove(
                            f"output/pytlint/{project}/{os.path.basename(file)}.json"
                        )

            except Exception as ex:
                print(
                    "###### Error!!! in project {0} and file: {1}. exception: ##########".format(
                        project, file, str(ex)
                    )
                )


def collect_stats(files, project):

    df = pd.DataFrame(
        columns=["file", "function", "n_try_except", "n_try_pass", "n_generic_except"]
    )

    file_stats = FileStats()
    pbar = tqdm(files)
    func_defs: List[Node] = []
    for file_path in pbar:
        print(f"File: {file_path}")
        pbar.set_description(f"Processing {str(file_path)[-40:].ljust(40)}")

        with open(file_path, "rb") as file:
            try:
                content = file.read()
            except UnicodeDecodeError as ex:
                tqdm.write(
                    f"###### UnicodeDecodeError Error!!! file: {file_path}.\n{str(ex)}"
                )
                continue
        try:
            tree = tree_sitter_parser.parse(content)
        except SyntaxError as ex:
            tqdm.write(f"###### SyntaxError Error!!! file: {file_path}.\n{str(ex)}")
        else:
            captures = get_function_defs(tree)
            for child in captures:
                func_defs.append(get_function_def(child))
                file_stats.metrics(child, file_path)
                metrics = file_stats.get_metrics(child)
                df = pd.concat(
                    [
                        pd.DataFrame(
                            [[file_path, child, metrics[0], metrics[1], metrics[2]]],
                            columns=df.columns,
                        ),
                        df,
                    ],
                    ignore_index=True,
                )
    file_stats.num_files += len(files)
    file_stats.num_functions += len(func_defs)

    # func_defs_try_except = [
    #     f for f in func_defs if check_function_has_except_handler(f)
    # ]  # and not check_function_has_nested_try(f)    ]

    # func_defs_try_pass = [f for f in func_defs if is_try_except_pass(f)]

    print(file_stats)
    df.to_csv(f"output/stats.csv", index=False)


if __name__ == "__main__":
    project = "django"
    files = fetch_repositories(project)
    # collect_smells(files, project)
    collect_stats(files, project)
