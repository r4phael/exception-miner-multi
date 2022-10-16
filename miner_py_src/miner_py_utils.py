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
    for child in ast.walk(node):
        if isinstance(child, ast.ExceptHandler):
            return True
    return False


assert (has_except(ast.parse("""
def teste():
    try:
        print(a)
    except:
        pass""")) == True)

assert (has_except(ast.parse("""
def teste():
    print(a)""")) == False)

print("has_except test OK")


def has_nested_catch(node: ast.FunctionDef):
    depth = 0
    for child in ast.walk(node):
        if not isinstance(child, ast.Try):
            continue

        if depth >= 1:
            return True

        depth += 1
    return False


assert (has_nested_catch(ast.parse("""
def teste():
    try:
        print(a)
        try:
            print(a)
        except:
            pass
    except:
        pass""")) == True)

assert (has_nested_catch(ast.parse("""
def teste():
    try:
        print(a)
    except:
        pass""")) == False)

assert (has_nested_catch(ast.parse("""
def teste_nested_try_except():
    a = 1
    b = 2
    b = a
    print(b)
    try:
        c = b
        print(c)
        try:
            print('nested')
        except Exception:
            print('falhou')
    except Exception:
        print('falhou')

    print(b)""")) == True)

print("has_nested_catch test OK")


def get_dataframe_from_pickle(path: str):
    return pd.read_pickle(path)


def print_pair_task1(df, delay=0):
    if df.size == 0:
        print("[Task 1] Empty Dataframe")
        return
    for labels, lines in zip(df['labels'], df['lines']):
        print('\n'.join([get_color_string(bcolors.WARNING if label == 1 else bcolors.HEADER, f"{label} {line}") for label,
              line in zip(labels, lines)]), end='\n\n')
        time.sleep(delay)


def print_pair_task2(df: pd.DataFrame, delay=False):
    if df.size == 0:
        print("[Task 2] Empty Dataframe")
        return
    for try_lines, except_lines in zip(df['try'], df['except']):
        print(get_color_string(bcolors.OKGREEN, '\n'.join(try_lines)))
        print(get_color_string(bcolors.FAIL, '\n'.join(except_lines)))
        print()
        time.sleep(delay)


def get_color_string(color: bcolors, string: str):
    return f"{color}{string}{bcolors.ENDC}"
