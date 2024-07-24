import pandas as pd
import logging
import time
import requests
import json
import os

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# projects = ["django", "flask", "pytorch", "pandas"]
projects = ["flask"]
dfs=[]

def get_prompt(function, binary_anwsers=True):
    premise = "You will be provided with a python code snippet."
    code_text = function
    only = '' if binary_anwsers else "only"
    instructions = (
        f"Based on the code above, I need you to identify if this code need an exception handling mechanism."
        + f"Please respond {only} with a yes or no."
    )
    final_text = [
        premise,
        "<code>",
        code_text,
        "</code>",
        instructions
    ]   
    final_text = "\n".join(final_text)
    return final_text

def collect_df(functions=[]):
    for project in projects:
        #filenames = glob.glob(f"../output/parser/*.csv")
        #df = pd.read_csv(f"../output/parser/{project}_stats.csv")
        df = pd.read_csv("/home/r4ph/desenv/exception-miner-multi/output/parser/py/flask_stats.csv")
        df['project'] = project
        dfs.append(df)

    # for fun in df[df['n_try_except'] == 1].str_code_without_try_except.values:
    #     functions.append(fun)

    pos_samples = df[df['n_try_except'] == 1]
    neg_samples = df[df['n_try_except'] == 0].sample(n=len(pos_samples), random_state=42)
    
    # concat and shuffle the DataFrame rows
    return pd.concat([pos_samples, neg_samples], ignore_index=True).sample(frac=1)

def call_llama(prompt, model_name="codellama"):

    headers = {
        "Content-Type": "application/json"
    }

    data = {
            "model": model_name,
            "prompt" :prompt,
            "stream": False
            }

    response = requests.post("http://localhost:11434/api/generate", headers=headers, data=json.dumps(data))
    return response


start = time.time()
model_name = "codellama"
df = collect_df()
output = []

for i, row in df.iterrows():
    if row['n_try_except'] == 1:
        prompt = get_prompt(row['str_code_without_try_except'])
    else:
        prompt = get_prompt(row['func_body'])

    response = call_llama(prompt=prompt)
    logger.info(response.json())
    logger.info(f'Generated {len(response.json())} tokens in {(time.time() - start):.2f} seconds')
    output.append(response.json()['response'])

df['llm_response'] = output
df.to_csv(f"{os.getcwd()}/{projects[0]}_llm.csv", index=False)