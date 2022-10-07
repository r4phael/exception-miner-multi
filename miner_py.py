import pandas as pd
import pathlib
import os, shutil
import ast
from tqdm import tqdm
#from subprocess import call
from subprocess import PIPE, run, call
from pydriller import Git
from utils import create_logger

logger = create_logger("exception_py_miner", "exception_py_miner.log")
projects = pd.read_csv("projects_py.csv", sep=",")


if not os.path.exists('output/py/results'):
    os.mkdir('output/py/results')


for index, row in projects.iterrows():
    #repo = Repository(row['repo'], clone_repo_to="projects")
    #commits_count = CommitsCount(path_to_repo= os.path.join('projects', row['repo']))
    #for commit in Repository(row['repo'], clone_repo_to="projects").traverse_commits():
    project = row['name']

    try:
        path = os.path.join(os.getcwd(),'projects/py/', project)
        git_cmd = "git clone {}.git --recursive {}".format(row['repo'], path)
        call(git_cmd, shell=True)
        gr = Git(path)
        logger.warning("Exception Miner: cloned project: {}".format(project))

    except Exception as e:
        logger.warning("Exception Miner: error in project: {}, error: {}".format(project, str(e)))
    
    if not os.path.exists("output/py/results/{}".format(project)):
        os.mkdir("output/py/results/{}".format(project))
    
    
    files =  gr.files()  
    for file in tqdm(files):
    #file = 'home/r4ph21/desenv/exception-miner/projects/py/modern-python-101/03_Flow_Control/print_my_name.py'
        if (pathlib.Path(r'{0}'.format(file)).suffix == ".py"):
            print(file)
            #print(os.path.basename(file))
            shutil.copy(file, "except_file.py")
            output_path = os.path.join("output/py/files/{}".format(project), os.path.basename(file))
            try:
                with open(file, "rb") as f:
                    content = f.read()
                    tree = ast.parse(content)
                    print(tree)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ExceptHandler):
                        print ("###### File {0} in project {1} have exception: {2}.#######".format(file, project, str(node)))
                        f.close
                        shutil.move(file, "output/py/results/{}/{}".format(project, os.path.basename(file)))
                        
            except Exception as e:
                f.close
                print ("###### Error!!! in project {0} and file: {1}. exception: ##########".format(project, file, str(e)))

