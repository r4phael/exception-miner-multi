import json
import os
import pathlib
from subprocess import PIPE, call, run

import pandas as pd
from pydriller import Git
from tqdm import tqdm

from utils import create_logger

logger = create_logger("exception_miner", "exception_miner.log")


def fetch_gh(projects, dir='projects/py/'):
    for index, row in projects.iterrows():
        project = row['name']
        try:
            path = os.path.join(os.getcwd(), dir, project)
            git_cmd = "git clone {}.git --recursive {}".format(
                row['repo'], path)
            call(git_cmd, shell=True)
            logger.warning("EH MINING: cloned project")
        except Exception as e:
            logger.warning(f"EH MINING: error cloing project {project} {e}")


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
        logger.warning(
            "Exception Miner: Before init git repo: {}".format(project))
        gr = Git(path)
        logger.warning(
            "Exception Miner: After init git repo: {}".format(project))

        files = [
            f
            for f in gr.files()
            if pathlib.Path(rf"{f}").suffix == ".py" and not os.path.islink(f)
        ]

        return files

    except Exception as ex:
        logger.warning(
            "Exception Miner: error in project: {}, error: {}".format(
                project, str(ex))
        )


def collect_smells(files, project):
    for file in tqdm(files):
        if pathlib.Path(file).suffix == ".py":
            try:
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
                tqdm.write(
                    "###### Error!!! in project {0} and file: {1}. exception: ##########".format(
                        project, file, str(ex)
                    )
                )


if __name__ == "__main__":
    projects = pd.read_csv("projects_py.csv", sep=",")
    fetch_gh(projects=projects)
    for index, row in projects.iterrows():
        files = fetch_repositories(row['name'])
        collect_smells(files, row['name'])
