import ast


def has_except(node: ast.FunctionDef):
    for node in ast.walk(node):
        if isinstance(node, ast.ExceptHandler):
            return True
    return False
