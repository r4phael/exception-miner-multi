import pandas as pd
import pathlib
import os
from tqdm import tqdm
from subprocess import call
from pydriller import Git
from utils import create_logger


logger = create_logger("exception_miner", "exception_miner.log")
projects = pd.read_csv("projects.csv", sep=",")


#command = '/home/r4ph21/desenv/eh-mining/pmd/pmd-bin-6.41.0/bin/run.sh pmd -d {0} -R eh-ruleset.xml -f json -r {1}'.format('projects/elasticsearch-hadoop', 'data/output.json')
#subprocess.call([command], shell=True, executable='/bin/bash')
for index, row in projects.iterrows():
    #repo = Repository(row['repo'], clone_repo_to="projects")
    #commits_count = CommitsCount(path_to_repo= os.path.join('projects', row['repo']))
    #for commit in Repository(row['repo'], clone_repo_to="projects").traverse_commits():
    project = row['name']

    try:
        path = os.path.join(os.getcwd(),'projects/', project)
        git_cmd = "git clone {}.git --recursive {}".format(row['repo'], path)
        call(git_cmd, shell=True)
        gr = Git(path)
        logger.warning("Exception Miner: cloned project: {}".format(project))

    except Exception as e:
        logger.warning("Exception Miner: error in project: {}, error: {}".format(project, str(e)))

    if not os.path.exists("output/{}".format(project)):
        os.mkdir("output/{}".format(project))

    files =  gr.files()  
    for file in tqdm(files):
        if (pathlib.Path(file).suffix == ".java"):
            #print(file)
            #print(os.path.basename(file))
            output_path = os.path.join("output/{}".format(project), os.path.basename(file))
            try:
                call(['java', '-jar', 'javaparser-maven-sample-1.0-SNAPSHOT-shaded.jar', file, output_path])
            except:
                print ("###### Error!!! processing the java parse! in project {0} and file: {1} ##########".format(project, file))          

    



