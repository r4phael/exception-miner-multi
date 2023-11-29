import time
from collections import namedtuple
from enum import Enum
from typing import List

import pandas as pd
from termcolor import colored
from tqdm import tqdm
from tree_sitter.binding import Node, Tree

from .tree_sitter_ts import (
    QUERY_TRY_CATCH,
    QUERY_FUNCTION_DEF,
    QUERY_FUNCTION_IDENTIFIER,
    QUERY_TRY_STMT,
    QUERY_CATCH_CLAUSE,
    QUERY_CATCH_IDENTIFIER_BODY,
    QUERY_CATCH_STATEMENTS,
    QUERY_FIND_IDENTIFIERS,
    QUERY_EXPRESSION_STATEMENT,
    QUERY_THROW_STATEMENT,
    QUERY_THROW_STATEMENT_CHILDREN,
    QUERY_THROW_STATEMENT_IDENTIFIER,
    QUERY_RETURN,
    QUERY_FINALLY_BLOCK,
    QUERY_CATCH_BLOCK,
    QUERY_CATCH_ASSIGNMENT_EXPRESSION_LEFT,
)

from .exceptions import (
    CatchClauseExpectedException,
    FunctionDefNotFoundException,
    TryNotFoundException,
)

Slices = namedtuple(
    "Slices",
    [
        "try_block_start",
        "handlers",
    ],
)


class bcolors(Enum):
    WARNING = "yellow"
    HEADER = "blue"
    OKGREEN = "green"
    FAIL = "red"


# TODO multi except tuple eg.: 'except (Error1, Error2): ...'
def get_try_slices(node: Node):
    function_start = node.start_point[0] - 1
    captures = QUERY_TRY_CATCH.captures(node)
    if len(captures) == 0:
        raise TryNotFoundException("try-catch slices not found")
    try_block_start, handlers = None, []

    # remove try.stmt after handlers
    filtered = [captures[0]]
    filtered.extend(
        [
            (capture, capture_name)
            for capture, capture_name in captures[1:]
            if capture_name != "try.stmt"
        ]
    )

    for capture, capture_name in filtered:
        if capture_name == "try.stmt":
            try_block_start = capture.start_point[0] - function_start
        elif capture_name == "catch.clause":
            handlers.append(
                (
                    capture.start_point[0] - function_start,
                    capture.end_point[0] - function_start,
                )
            )

    return Slices(try_block_start, handlers)

def count_lines_of_function_body(f: Node, filename=None):
    try:
        return f.end_point[0] - f.start_point[0]
    except Exception as e:
        tqdm.write(f"Arquivo: {filename}" if filename is not None else "")
        tqdm.write(str(e))
    return 0

def get_function_def(node: Node) -> Node:
    captures = QUERY_FUNCTION_DEF.captures(node)
    if len(captures) == 0:
        raise FunctionDefNotFoundException("Not found")
    return captures[0][0]

def get_function_defs(tree: Tree) -> List[Node]:
    captures = QUERY_FUNCTION_DEF.captures(tree.root_node)
    return [c for c, _ in captures]

def get_function_literal(node: Node):
    captures = QUERY_FUNCTION_IDENTIFIER.captures(node)
    if len(captures) == 0:
        raise FunctionDefNotFoundException("Not found")
    return captures[0][0]

def check_function_has_try(node: Node):
    captures = QUERY_TRY_STMT.captures(node)
    return len(captures) != 0

def count_empty_catch(node: Node):
    return len(list(filter(
        lambda x: len(x[0].children) > 0,
        QUERY_CATCH_BLOCK.captures(node)
    )))

def check_useless_throw_in_catch(node: Node, catchParam):
    if len(node.children) > 3:
        return False
    if node.children[1].type == 'throw_statement':
        captures = QUERY_FIND_IDENTIFIERS.captures(node.children[1])
        for c, _ in captures:
            if c.text.decode('utf-8') == catchParam:
                return True
    return False

def count_catch_reassigning_identifier(node: Node):
    captures = QUERY_CATCH_ASSIGNMENT_EXPRESSION_LEFT.captures(node)
    index, result = 0, 0
    current_catch_identifier = ''

    while index < len(captures):
        identifier = captures[index][0].text.decode('utf-8')
        if captures[index][1] == 'catch.identifier':
            current_catch_identifier = identifier
        elif captures[index][1] == 'left.assignment.identifier':
            if identifier == current_catch_identifier:
                result += 1
        index += 1
    return result

def count_useless_catch(node: Node):
    captures = QUERY_CATCH_IDENTIFIER_BODY.captures(node)
    index, result = 0, 0

    while index < len(captures):
        if captures[index][1] == 'catch.identifier':
            if check_useless_throw_in_catch(captures[index+1][0], captures[index][0].text.decode('utf-8')):
                result += 1
            index += 2
        else:
            index += 1
    return result

def is_generic_catch(catch_clause: Node):
    if catch_clause.type != "catch_clause":
        raise CatchClauseExpectedException("Parameter must be catch_clause")

    # captures = QUERY_EXCEPT_EXPRESSION.captures(catch_clause)
    captures = QUERY_CATCH_BLOCK.captures(catch_clause)
    if len(captures) == 0:
        return False

    for c, _ in captures:
        identifiers = QUERY_FIND_IDENTIFIERS.captures(c)
        for ident, _ in identifiers:
            if ident.text == b"Error":
                return True

    return False

def count_try(node: Node):
    captures = QUERY_TRY_STMT.captures(node)
    return len(captures)

def count_catch(node: Node):
    captures = QUERY_CATCH_CLAUSE.captures(node)
    return len(captures)

def check_function_has_catch_handler(node: Node):
    captures = QUERY_CATCH_CLAUSE.captures(node)
    return len(captures) != 0

def get_catch_clause(node: Node):
    captures = QUERY_CATCH_CLAUSE.captures(node)
    return captures

def get_catch_block(node: Node):
    captures = QUERY_CATCH_BLOCK.captures(node)
    return captures

def get_catch_statements(node: Node):
    captures = QUERY_CATCH_STATEMENTS.captures(node)
    return captures

def statement_couter(node: Node):
    captures = QUERY_EXPRESSION_STATEMENT.captures(node)
    return len(captures)

def check_function_has_nested_try(node: Node):
    captures = QUERY_TRY_STMT.captures(node)
    for c, _ in captures:
        if len(QUERY_TRY_STMT.captures(c)) > 2:
            return True

    return False

def count_nested_try(node: Node):
    n = 0
    captures = QUERY_TRY_STMT.captures(node)
    for c, _ in captures:
        if len(QUERY_TRY_STMT.captures(c)) > 2:
            n += 1

    return n

def count_try_return(node: Node):
    captures = QUERY_TRY_STMT.captures(node)
    result = []
    for capture, _ in captures:
        test = QUERY_RETURN.captures(capture)
        if len(test) > 0:
            result.append(test)
    return len(result)

def count_finally(node: Node):
    captures = QUERY_FINALLY_BLOCK.captures(node)
    return len(captures)

def count_throw(node: Node):
    captures = QUERY_THROW_STATEMENT.captures(node)
    return len(captures)

def get_throw_identifiers(node: Node):
    captures = QUERY_THROW_STATEMENT_IDENTIFIER.captures(node)
    return list(map(
        lambda x: x[0].text.decode('utf-8'),
        filter(
                lambda x: (x[1] == 'throw.identifier'),
                captures)
    ))

def get_catch_identifiers(node: Node):
    return list(map(
        lambda x: x[0].text.decode('utf-8'),
        filter(
                lambda x: (x[1] == 'catch.clause'),
                QUERY_CATCH_CLAUSE.captures(node))
    ))

def count_untyped_throw(node: Node):
    return len(
        list(filter(
            lambda x: x[0].text == b'Error',
            QUERY_THROW_STATEMENT_IDENTIFIER.captures(node))))

def is_generic_throw(node: Node, catchParameter=None):
    identifiers = QUERY_FIND_IDENTIFIERS.captures(node)
    for identifier, _ in identifiers:
        text = identifier.text.decode('utf-8')
        if text != 'Error' and text != catchParameter:
            return False
    return True

# throw ErrorObj()
# throw ""
# throw ({...})
def count_not_recommended_throw(node: Node):
    captures = QUERY_THROW_STATEMENT_CHILDREN.captures(node)
    count = 0
    for c, _ in captures:
        if c.type != 'new_expression':
            count += 1
    return count

# throw new MyErrorType(...)
def count_non_generic_throw(node: Node):
    return len(list(filter(
        lambda x: not is_generic_throw(x[0], None),
        QUERY_THROW_STATEMENT_IDENTIFIER.captures(node)
    )))
 

#Quantos throws em try catch que não tenham tratamentos especificos
def count_try_catch_throw(node: Node):
    captures = QUERY_CATCH_CLAUSE.captures(node)
    generic_catch_throw_number = 0
    for i in range(0, len(captures), 2):
        throwList = QUERY_THROW_STATEMENT.captures(captures[i][0])
        catchIdentifier = None if i+1 >= len(captures) or captures[i+1][1] != 'catch.identifier' else captures[i+1][0].text.decode('utf-8')
        for throw, _ in throwList:
            if not is_generic_throw(throw, catchIdentifier):
                break
            generic_catch_throw_number += 1
    return generic_catch_throw_number


# def count_misplaced_bare_raise(node: Node):
#     bare_raise_statements = get_bare_raise(node)
#     counter = 0
#     for node, _ in bare_raise_statements:
#         if (has_misplaced_bare_raise(node)):
#             counter += 1
#     return counter

## checar se o raise está dentro de um except

# def has_misplaced_bare_raise(raise_stmt: Node):
#     # scope = node.scope()
#     # if (
#     #     isinstance(scope, nodes.FunctionDef)
#     #     and scope.is_method()
#     #     and scope.name == "__exit__"
#     # ):
#     #     return

#     current = raise_stmt
#     # Stop when a new scope is generated or when the raise
#     # statement is found inside a TryFinally.
#     ignores = ('except_clause', 'function_definition')
#     while current and current.type not in ignores:
#         current = current.parent

#     expected = ('except_clause', )
#     return not current or current.type not in expected


# def count_bare_raise_inside_finally(node: Node):
#     bare_raise_statements = get_bare_raise(node)
#     counter = 0
#     for node, _ in bare_raise_statements:
#         if (has_bare_raise_finally(node)):
#             counter += 1
#     return counter

## checar se o raise está dentro de um finally

# def has_bare_raise_finally(raise_stmt: Node):
#     current = raise_stmt

#     ignores = ('finally_clause', 'function_definition')
#     while current and current.type not in ignores:
#         current = current.parent

#     expected = ('finally_clause')
#     return not current or current.type in expected
