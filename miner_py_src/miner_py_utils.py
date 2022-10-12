import ast
import pandas as pd
import time


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def has_except(node: ast.FunctionDef):
    for node in ast.walk(node):
        if isinstance(node, ast.ExceptHandler):
            return True
    return False


def get_dataframe_from_pickle(path: str):
    return pd.read_pickle(path)


def print_pair_task1(df, delay=0):
    for labels, lines in zip(df['labels'], df['lines']):
        print('\n'.join([get_color_string(bcolors.OKGREEN if label == 1 else bcolors.OKBLUE, f"{label} {line}") for label,
              line in zip(labels, lines)]), end='\n\n')
        time.sleep(delay)


def print_pair_task2(df, delay=False):
    for try_lines, except_lines in zip(df['try'], df['except']):
        print(get_color_string(bcolors.OKBLUE, '\n'.join(try_lines)))
        print(get_color_string(bcolors.OKGREEN, '\n'.join(except_lines)))
        print()
        time.sleep(delay)


def get_color_string(color: bcolors, string: str):
    return f"{color}{string}{bcolors.ENDC}"
