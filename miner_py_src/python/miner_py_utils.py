import io
import token
import tokenize
from collections import namedtuple
from enum import Enum
from typing import List, Union
from .exceptions import TreeSitterNodeException

from tqdm import tqdm
from tree_sitter._binding import Node, Tree

from .tree_sitter_py import (
    QUERY_TRY_EXCEPT,
    QUERY_FUNCTION_DEF,
    QUERY_FUNCTION_DEF,
    QUERY_FUNCTION_IDENTIFIER,
    QUERY_TRY_STMT,
    QUERY_EXCEPT_CLAUSE,
    QUERY_PASS_BLOCK,
    QUERY_EXCEPT_EXPRESSION,
    QUERY_FIND_IDENTIFIERS,
    QUERY_TRY_STMT,
    QUERY_EXPRESSION_STATEMENT,
    QUERY_TRY_STMT,
    QUERY_TRY_STMT,
    QUERY_RAISE_STATEMENT_IDENTIFIER,
    QUERY_TRY_EXCEPT_RAISE,
    QUERY_RAISE_STATEMENT,
    QUERY_TRY_ELSE,
    QUERY_TRY_RETURN,
    QUERY_FINALLY_BLOCK,
    QUERY_EXCEPT_BLOCK,
)

from .exceptions import (
    ExceptClauseExpectedException,
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
    captures = QUERY_TRY_EXCEPT.captures(node)
    if len(captures) == 0:
        raise TryNotFoundException("try-except slices not found")
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
        elif capture_name == "except.clause":
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


def is_bad_exception_handling(node: Node):
    captures = QUERY_EXCEPT_CLAUSE.captures(node)
    except_clause = captures[0][0]
    return (
        except_clause.type != "except_clause"
        or is_try_except_pass(except_clause)
        or is_generic_except(except_clause)
    )


def is_try_except_pass(except_clause: Node):
    if except_clause.type != "except_clause":
        raise ExceptClauseExpectedException("Parameter must be except_clause")

    captures = QUERY_PASS_BLOCK.captures(except_clause)
    return len(captures) > 0


def is_generic_except(except_clause: Node):
    if except_clause.type != "except_clause":
        raise ExceptClauseExpectedException("Parameter must be except_clause")

    captures = QUERY_EXCEPT_EXPRESSION.captures(except_clause)
    if len(captures) == 0:
        return False

    for c, _ in captures:
        identifiers = QUERY_FIND_IDENTIFIERS.captures(c)
        for ident, _ in identifiers:
            if ident.text == b"Exception":
                return True

    return False


def check_function_has_generic_except(node: Node):
    captures = QUERY_EXCEPT_CLAUSE.captures(node)
    for c, _ in captures:
        if is_generic_except(c):
            return True

    return False

def is_bare_except(except_clause: Node):
    if except_clause.type != "except_clause":
        raise ExceptClauseExpectedException("Parameter must be except_clause")

    captures = QUERY_EXCEPT_EXPRESSION.captures(except_clause)
    if len(captures) == 0:
        return True
    
    return False


def check_function_has_bare_except(node: Node):
    captures = QUERY_EXCEPT_CLAUSE.captures(node)
    for c, _ in captures:
        if is_bare_except(c):
            return True

    return False


def count_try(node: Node):
    captures = QUERY_TRY_STMT.captures(node)
    return len(captures)


def count_except(node: Node):
    captures = QUERY_EXCEPT_CLAUSE.captures(node)
    return len(captures)


def check_function_has_except_handler(node: Node):
    captures = QUERY_EXCEPT_CLAUSE.captures(node)
    return len(captures) != 0

def get_except_clause(node: Node):
    captures = QUERY_EXCEPT_CLAUSE.captures(node)
    return captures


def get_except_block(node: Node):
    captures = QUERY_EXCEPT_BLOCK.captures(node)
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

def count_try_else(node: Node):
    captures = QUERY_TRY_ELSE.captures(node)
    return len(captures)


def count_try_return(node: Node):
    captures = QUERY_TRY_RETURN.captures(node)
    return len(captures)

def count_finally(node: Node):
    captures = QUERY_FINALLY_BLOCK.captures(node)
    return len(captures)

def count_raise(node: Node):
    captures = QUERY_RAISE_STATEMENT.captures(node)
    return len(captures)


def get_except_identifiers(node: Node):
    identifiers_str = []
    captures = QUERY_EXCEPT_CLAUSE.captures(node)
    for except_clause, _ in captures:
        except_expressions = QUERY_EXCEPT_EXPRESSION.captures(except_clause)

        for c, _ in except_expressions:
            identifiers = QUERY_FIND_IDENTIFIERS.captures(c)

            try:
                ignore_identifier = c.text.decode(
                    'utf-8').split('as')[1].strip()
            except IndexError:
                ignore_identifier = None

            for identifier, _ in identifiers:
                if (identifier.text.decode('utf-8') == ignore_identifier):
                    continue
                identifiers_str.append(identifier.text.decode('utf-8'))

    return identifiers_str


def get_raise_identifiers(node: Node):
    captures = QUERY_RAISE_STATEMENT_IDENTIFIER.captures(node)
    return list(map(
        lambda x: x[0].text.decode('utf-8'),
        filter(
                lambda x: (x[1] == 'raise.identifier'),
                captures)
    ))


def get_bare_raise(node: Node):
    return list(filter(
        lambda x: x[0].text == b'raise',
        QUERY_RAISE_STATEMENT.captures(node)))


def count_broad_exception_raised(node: Node):
    return len(
        list(filter(
            lambda x: x[0].text == b'Exception',
            QUERY_RAISE_STATEMENT_IDENTIFIER.captures(node))))


def count_try_except_raise(node: Node):
    return len(
        list(filter(
            lambda x: (x[1] == 'raise.identifier' and x[0].text == b'Exception') or
            (x[1] == 'raise.stmt' and x[0].text == b'raise'),
            QUERY_TRY_EXCEPT_RAISE.captures(node))))


def count_misplaced_bare_raise(node: Node):
    bare_raise_statements = get_bare_raise(node)
    counter = 0
    for node, _ in bare_raise_statements:
        if (has_misplaced_bare_raise(node)):
            counter += 1
    return counter


def has_misplaced_bare_raise(raise_stmt: Node):
    # scope = node.scope()
    # if (
    #     isinstance(scope, nodes.FunctionDef)
    #     and scope.is_method()
    #     and scope.name == "__exit__"
    # ):
    #     return

    current = raise_stmt
    # Stop when a new scope is generated or when the raise
    # statement is found inside a TryFinally.
    ignores = ('except_clause', 'function_definition')
    while current and current.type not in ignores:
        current = current.parent

    expected = ('except_clause', )
    return not current or current.type not in expected


def count_bare_raise_inside_finally(node: Node):
    bare_raise_statements = get_bare_raise(node)
    counter = 0
    for node, _ in bare_raise_statements:
        if (has_bare_raise_finally(node)):
            counter += 1
    return counter


def has_bare_raise_finally(raise_stmt: Node):
    current = raise_stmt

    ignores = ('finally_clause', 'function_definition')
    while current and current.type not in ignores:
        current = current.parent

    expected = ('finally_clause')
    return not current or current.type in expected

def get_code_without_try_except(node: Node, tree) -> Union[None, str]:
    # Traverse the function body and remove try-except blocks
    if check_function_has_try(node):
        captures = QUERY_TRY_EXCEPT.captures(node)
        new_code_lines = []
        source_code = tree.text
        
        current_position = node.start_byte
        
        for capture in captures:
            node_try_except = capture[0]            
            # Capture try body block
            if capture[1] == 'try.stmt':
                # Add code before the try block
                new_code_lines.append(source_code[current_position:node_try_except.start_byte])
                # Add the content of the try block, excluding the `try:` keyword
                # try_block = node_try_except.text.decode('utf8').strip()[4:-1]
                for child in node_try_except.children:
                    if child.type == 'block':
                        new_code_lines.append(child.text)
                    current_position = node_try_except.end_byte
            # Capture except clause block
            # elif capture[1] == 'except.clause':
            #     new_code_lines.append(source_code[current_position:start_byte])
            #     current_position = end_byte

            break

        # Add the remaining part of the code
        new_code_lines.append(source_code[current_position:node.end_byte])
        decoded_lines = [line.decode('utf-8') for line in new_code_lines]
    
        # Join and return the new code
        return ''.join(decoded_lines)
    
def get_try_statements_vector(node: Node, vector = []):
    assert node is not None

    if not isinstance(node.text, bytes):
        raise TreeSitterNodeException("node.text is not bytes")

    if not check_function_has_try(node):
        return [0] * len(node.children) # No try statements, all statements are 0

    try:
        try_slice = get_try_slices(node)
    except TryNotFoundException:
        return [0] * len(node.children)
    
    function_start = node.start_point[0] - 1

    if try_slice is not None:
        for child in node.children:
            if child.is_named:
                try_reached = (child.start_point[0] - function_start) >= try_slice.try_block_start
                #except_reached = 
                #finnaly_reached = 
                vector.append(1 if try_reached else 0)

                

                #if len(try_slice.handlers) != 0 and token_info.start[0] >= try_slice.handlers[0][0]:

    # for child in node.children:
    #     if child.is_named:
    #         for start, end in slices:
    #             enclosed_by_try = any(start <= child.start_byte < end for start, end in slices)
    #         vector.append(1 if enclosed_by_try else 0)
    
    return vector