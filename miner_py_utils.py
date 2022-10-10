import ast
import pandas as pd


def has_except(node: ast.FunctionDef):
    for node in ast.walk(node):
        if isinstance(node, ast.ExceptHandler):
            return True
    return False


def get_dataframe_from_pickle(path: str):
    return pd.read_pickle(path)


def print_pair_label_line(df):
    for labels, lines in zip(df['labels'], df['lines']):
        print('\n'.join([f"{label} {line}" for label,
              line in zip(labels, lines)]), end='\n\n')
