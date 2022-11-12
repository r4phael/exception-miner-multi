import ast
import pandas as pd
import time
from enum import Enum
from .exceptions import TryNotFoundException, FunctionDefNotFoundException


class bcolors(Enum):
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# TODO criar testes
def get_try_slices_recursive(node: ast.FunctionDef):
    for child in ast.walk(node):
        for name, fields in ast.iter_fields(child):
            if type(fields) == list:
                nodes_list = [index for index, child_body in enumerate(
                    fields) if isinstance(child_body, ast.Try)]
                for try_index in nodes_list:
                    try_node = child.__getattribute__(name)[try_index]
                    if isinstance(try_node, ast.Try) and len(try_node.handlers) != 0:
                        return child, name, try_index
            elif isinstance(fields, ast.Try) and len(fields.handlers) != 0:
                try_index = None
                return child, name, try_index

    raise TryNotFoundException('Not found')


def get_function_def(node: ast.Module):
    for child in ast.walk(node):
        if isinstance(child, ast.FunctionDef):
            return child
    raise FunctionDefNotFoundException('Not found')


def check_function_has_try(node: ast.FunctionDef):
    for child in ast.walk(node):
        if isinstance(child, ast.Try):
            return True
    return False


def count_try(node: ast.FunctionDef):
    count = 0
    for child in ast.walk(node):
        if isinstance(child, ast.Try):
            count += 1
    return count


def check_function_has_except_handler(node: ast.FunctionDef):
    for child in ast.walk(node):
        if isinstance(child, ast.ExceptHandler):
            return True
    return False


def statement_couter(node: ast.FunctionDef):
    counter = 0
    for child in ast.walk(node):
        if isinstance(child, ast.stmt):
            counter += 1
    return counter


def check_function_has_nested_try(node: ast.AST, has_try_parent=False):
    for child in ast.iter_child_nodes(node):
        is_try = isinstance(child, ast.Try)
        if is_try and has_try_parent:
            return True
        elif is_try:
            has_nested = check_function_has_nested_try(child, True)
            if has_nested:
                return True
        else:
            has_try = check_function_has_nested_try(child, has_try_parent)
            if has_try and has_try_parent:
                return True
    return False


def get_dataframe_from_pickle(path: str):
    return pd.read_pickle(path)


def print_pair_task1(df, delay=0):
    if df.size == 0:
        print("[Task 1] Empty Dataframe")
        return
    df_lines: list[str] = df['lines']
    for labels, lines in zip(df['labels'], df_lines):
        print('\n'.join([get_color_string(bcolors.WARNING if label == 1 else bcolors.HEADER, f"{label} {decode_indent(line)}") for label,
              line in zip(labels, lines)]), end='\n\n')
        time.sleep(delay)


def print_pair_task2(df: pd.DataFrame, delay=False):
    if df.size == 0:
        print("[Task 2] Empty Dataframe")
        return
    for try_lines, except_lines in zip(df['try'], df['except']):
        print(get_color_string(bcolors.OKGREEN,
              decode_indent('\n'.join(try_lines))))
        print(get_color_string(bcolors.FAIL, decode_indent('\n'.join(except_lines))))
        print()
        time.sleep(delay)


def decode_indent(line: str):
    return line.replace('<INDENT>', '    ').replace('<NEWLINE>', '')


def get_color_string(color: bcolors, string: str):
    return f"{color}{string}{bcolors.ENDC}"
