import pandas as pd
import psycopg2
import glob
import json
from utils import create_logger

logger = create_logger("exception_miner", "exception_miner.log")


def return_conn_pg():
    conn = psycopg2.connect("host={} user={} dbname=exception_miner password={} port={}".format("127.0.0.1", "exception_miner", "exception_miner", "5432"))
    conn.set_session(autocommit=True)
    cur = conn.cursor()
    return cur

def insert_pylint(project, df_py):

    cur = return_conn_pg()

    cur.execute("""CREATE TABLE IF NOT EXISTS exceptions_pylint (type VARCHAR, module VARCHAR, obj VARCHAR, beginLine INT, beginColumn INT,	endLine INT, endColumn INT, path VARCHAR, symbol VARCHAR, message VARCHAR, message_id VARCHAR, project VARCHAR)""")

    logger.warning(f"Exception Miner: ingesting {project} into pytlint table:")
    
    cur.execute(f"""DELETE FROM exceptions_pylint WHERE project = '{project}';""")

    for i, row in df_py.iterrows():
        #print(row)
        cur.execute(("""INSERT INTO exceptions_pylint (type, module, obj, beginLine, beginColumn, endLine, endColumn, path, symbol, message, message_id, project)
                                VALUES (%s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s  );"""), list(row))

def insert_parser(project, df):
    
    cur = return_conn_pg()

    cur.execute("""CREATE TABLE IF NOT EXISTS exceptions_parser (file VARCHAR, function VARCHAR, n_try_except INT, n_try_pass INT, 
                                                                    n_generic_except INT, n_raise INT, n_captures_broad_raise INT, 
                                                                    n_captures_try_except_raise INT, n_captures_misplaced_bare_raise INT, project VARCHAR)""")

    logger.warning(f"Exception Miner: ingesting {project} into parser table")

    cur.execute(f"""DELETE FROM exceptions_parser WHERE project = '{project}';""")

    for i, row in df.iterrows():
        #print(row)
        cur.execute(("""INSERT INTO exceptions_parser (file, function, n_try_except, n_try_pass, n_generic_except, n_raise,
                            n_captures_broad_raise, n_captures_try_except_raise, n_captures_misplaced_bare_raise, project)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s );"""), list(row))


def ingest_db_pylint(projects, dfs=[]):
    
    for project in projects:
        filenames = glob.glob(f"output/pytlint/{project}/*.json")
        for filename in filenames:
            with open(filename, encoding='utf-8') as json_data:
                data = json.load(json_data)
                df = pd.json_normalize(data)
                df['project'] = project
                dfs.append(df)
        df = pd.concat(dfs, ignore_index=True)
        insert_pylint(project, df)


def ingest_db_parser(projects):

    #dfs=[]

    for project in projects:
        #filenames = glob.glob(f"../output/parser/*.csv")
                
        df = pd.read_csv(f"output/parser/{project}_stats.csv")
        df['project'] = project
        
        #TODO: Remove duplicates from parser
        df = df.drop_duplicates()
       
        insert_parser(project, df)


if __name__ == "__main__":
    projects = ["django", "flask", "pytorch", "pandas"]
    ingest_db_parser(projects)
    #ingest_db_pylint(projects)