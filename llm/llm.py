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

def prompt_default(function, binary_anwsers=True):
    premise = "You will be provided with a python code snippet."
    code_text = function
    instructions = (
        f"Based on the code above, I need you to identify if this code need an exception handling mechanism."
        #+ f"If yes, please return only yes and the code in completion. If not return only the word 'no'."
        + f"Please return only with the word yes or 'no'."
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


def prompt_1_shot(function):
    example_code = "result = 1 / n"
    example_result = "yes\ntry:\n    result = 1 / n\nexcept ZeroDivisionError:\n    print('Division by zero is not allowed')"
    
    final_text = (
        f"Here is an example:\n<code>\n{example_code}\n</code>\n"
        f"Output: {example_result}\n\n"
        "Now, analyze the following code:\n"
        f"<code>\n{function}\n</code>\n"
        "Does this code need an exception handling mechanism? If yes, please return only 'yes' and the code in completion. If not, return only 'no'."
    )
    return final_text

def prompt_few_shot(function, num_shots=2):
    examples = [
        (
            "open('file.txt', 'r')",
            "yes\ntry:\n    open('file.txt', 'r')\nexcept FileNotFoundError:\n    print('File not found')"
        ),
        (
            "value = int('not_an_int')",
            "yes\ntry:\n    value = int('not_an_int')\nexcept ValueError:\n    print('Invalid integer')"
        ),
        (
            "print('Hello, world!')",
            "no"
        )
    ]

    prompt = "Here are some examples of code snippets and their outputs:\n"
    for example_code, example_result in examples[:num_shots]:
        prompt += f"<code>\n{example_code}\n</code>\nOutput: {example_result}\n\n"
    
    prompt += (
        "Now, analyze the following code:\n"
        f"<code>\n{function}\n</code>\n"
        "Does this code need an exception handling mechanism? If yes, please return only 'yes' and the code in completion. If not, return only 'no'."
    )
    return prompt

def prompt_cot(function):
    prompt = (
        "Analyze the code snippet below and think step-by-step to determine if it needs an exception handling mechanism:\n"
        f"<code>\n{function}\n</code>\n"
        "First, check if there are any operations that might raise exceptions (e.g., file handling, division, type conversion).\n"
        "Then, consider if these operations are currently protected by try-except blocks. If they are not, an exception handling mechanism may be needed.\n"
        "Finally, provide your answer as 'yes' with the modified code or 'no' if no if an exception handling mechanism is required."
    )
    return prompt

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
    #return pd.concat([pos_samples, neg_samples], ignore_index=True).sample(frac=1)
    return pd.concat([pos_samples.sample(n=1), neg_samples.sample(n=1)], ignore_index=True)

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


PROMPT_FUNCTIONS = {
    "style-default": prompt_default,
    "style-1-shot": prompt_1_shot,
    "style-few-shot": prompt_few_shot,
    "style-cot": prompt_cot,
}

df_result = pd.DataFrame()
count=0
for prompt_type, prompt_func in PROMPT_FUNCTIONS.items():
    output = []
    for i, row in df.iterrows():
        count+= 1
        print(f"Calling {count} of ... {len(df)} rows for {prompt_type} prompt")
        if row['n_try_except'] == 1:
            prompt = prompt_func(row['str_code_without_try_except'])
        else:
            prompt = prompt_func(row['func_body'])

        response = call_llama(prompt=prompt)
        logger.info(response.json())
        logger.info(f'Generated {len(response.json())} tokens in {(time.time() - start):.2f} seconds')
        output.append(response.json()['response'])

    df_style = df.copy() 
    df_style['prompt_type'] = prompt_type
    df_style['llm_response'] = output

    df_result = pd.concat([df_result, df_style], ignore_index=True)

df_result.to_csv(f"{os.getcwd()}/new_flask_llm.csv", index=False)