from collections import namedtuple
from enum import Enum

from tqdm import tqdm
from tree_sitter import Node, Tree

from .tree_sitter_java import (
    QUERY_CATCH_ASSIGNMENT_EXPRESSION_LEFT,
    QUERY_FIND_IDENTIFIERS_THROW,
    QUERY_METHOD_DEF,
    QUERY_METHOD_IDENTIFIER,
    QUERY_EXPRESSION_STATEMENT,
    QUERY_METHOD_INVOCATION,
    QUERY_RETURN,
    QUERY_TRY_STMT,
    QUERY_TRY_CATCH,
    QUERY_CATCH_CLAUSE,
    QUERY_CATCH_IDENTIFIER_BODY,
    QUERY_CATCH_BLOCK,
    QUERY_CATCH_STATEMENTS,
    QUERY_FIND_IDENTIFIERS,
    QUERY_THROW_STATEMENT,
    QUERY_THROW_STATEMENT_IDENTIFIER,
    QUERY_FINALLY_BLOCK, 
)

from .exception import (
    CatchClauseExpectedException,
    FunctionDefNotFoundException,
    TryNotFoundException,
)

Slices = namedtuple(
    "Slices",
    [
        "try_block_start",
        "catch_handlers",
        "finally_handler",
    ],
)


class bcolors(Enum):
    WARNING = "yellow"
    HEADER = "blue"
    OKGREEN = "green"
    FAIL = "red"


def get_try_slices(node: Node):
    function_start = node.start_point[0] - 1
    captures = QUERY_TRY_CATCH.captures(node) + QUERY_FINALLY_BLOCK.captures(node)
    if len(captures) == 0:
        raise TryNotFoundException("try-catch slices not found")
    try_block_start, catch_handlers, finally_handler = None, [], None

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
            catch_handlers.append(
                (
                    capture.start_point[0] - function_start,
                    capture.end_point[0] - function_start,
                )
            )
        elif capture_name == "finally.clause":
            finally_handler = (
                capture.start_point[0] - function_start,
                capture.end_point[0] - function_start,
            )

    return Slices(try_block_start, catch_handlers, finally_handler)


def count_lines_of_function_body(f: Node, filename=None):
    try:
        return f.end_point[0] - f.start_point[0]
    except Exception as e:
        tqdm.write(f"Arquivo: {filename}" if filename is not None else "")
        tqdm.write(str(e))
    return 0

def get_function_def(node: Node):
    captures = QUERY_METHOD_DEF.captures(node)
    if len(captures) == 0:
        return captures[0][0]
    else: 
        raise FunctionDefNotFoundException("Function definition not found")
    
def get_function_defs(tree: Tree): 
    captures = QUERY_METHOD_DEF.captures(tree.root_node)
    return [c for c, _ in captures]

def get_function_literal(node: Node):
    captures = QUERY_METHOD_IDENTIFIER.captures(node)
    if len(captures) == 0: 
        raise FunctionDefNotFoundException("Not Found")
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
    if len(node.children)>3: 
        return False
    #if node.children[1].type == 'throw_statement': 
    if len(node.children) > 1 and node.children[1].type == 'throw_statement':
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
        if captures[index][1]=='catch.identifier':
            if check_useless_throw_in_catch(captures[index+1][0], captures[index][0].text.decode('utf-8')):
                result += 1
            index += 2
        else:
            index += 1
    return result

def is_generic_catch(catch_clause: Node):
    if catch_clause.type != "catch_clause":
        return CatchClauseExpectedException("Catch clause expected")
    captures = QUERY_CATCH_BLOCK.captures(catch_clause)
    if len(captures) == 0:
        return False
    
    for c, _ in captures:
        if c.type == 'catch_formal_parameter':
            identifiers = QUERY_FIND_IDENTIFIERS.captures(c)
            for identifier, _ in identifiers:
                if identifier.text == b"Exception" or identifier.text == b"Throwable":
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

def count_generic_throw(node: Node):
    return len(
        list(filter(
            lambda x: x[0].text.decode('utf-8') in ['Exception', 'Throwable'],
            QUERY_THROW_STATEMENT_IDENTIFIER.captures(node))))

def count_untyped_throw(node: Node):
    return len(
        list(filter(
            lambda x: x[0].text == b'Error',
            QUERY_THROW_STATEMENT_IDENTIFIER.captures(node))))

def is_generic_throw(node: Node, catchParameter=None):
    identifiers = QUERY_FIND_IDENTIFIERS_THROW.captures(node)
    for identifier, _ in identifiers:
        text = identifier.text.decode('utf-8')
        if catchParameter is not None:
            catchParameter = catchParameter.decode('utf-8')
        if text not in ['Exception', 'Throwable'] and text != catchParameter:
            return False
    return True

def count_non_generic_throw(node: Node):
    return len(list(filter(
        lambda x: not is_generic_throw(x[0], None),
        QUERY_THROW_STATEMENT_IDENTIFIER.captures(node)
    )))

def count_generic_throws(node: Node): 
    captures = QUERY_THROW_STATEMENT.captures(node)
    return len([c for c, _ in captures if is_generic_throw(c)])

def count_try_catch_throw(node: Node):
    captures = QUERY_CATCH_CLAUSE.captures(node)
    count = 0
    for i in range(0, len(captures), 2): 
        throwList = QUERY_THROW_STATEMENT.captures(captures[i][0])
        catchIdentifier = None if i+1 >= len(captures) or captures[i+1][1] != 'catch.identifier' else captures[i+1][0].text.decode('utf-8')
        for throw, _ in throwList: 
            is_generic = is_generic_throw(throw, catchIdentifier)
            if not is_generic: 
                break
            count += 1
    return count

def n_wrapped_catch(node: Node):
    captures = QUERY_CATCH_IDENTIFIER_BODY.captures(node)
    if len(captures) == 0:
        return 0
    count = 0
    catch_id = ''
    for c, t in captures:
        if t == 'catch.identifier':
            catch_id = c.text.decode('utf-8')
        if t == 'catch.body':
            is_used = False
            body_ids = QUERY_FIND_IDENTIFIERS.captures(c)
            for body_id, _ in body_ids:
                is_used = is_used or body_id.text.decode('utf-8') == catch_id
            if not is_used:
                count += 1
    return count

# def check_throwing_raw_exception(node: Node):
#     captures = QUERY_THROW_STATEMENT.captures(node)
#     for capture, _ in captures:
#         if is_generic_throw(capture):
#             return True
#     return False

def check_throw_within_finally(node: Node):
    # Captura todos os blocos finally
    finally_blocks = QUERY_FINALLY_BLOCK.captures(node)
    
    for finally_block, _ in finally_blocks:
        # Verifica se há uma declaração throw dentro do bloco finally
        throw_statements = QUERY_THROW_STATEMENT.captures(finally_block)
        if len(throw_statements) > 0:
            return True
    return False

def check_throwing_null_pointer_exception(node: Node):
    captures = QUERY_THROW_STATEMENT.captures(node)
    for capture, _ in captures:
        identifiers = QUERY_FIND_IDENTIFIERS_THROW.captures(capture)
        for identifier, _ in identifiers:
            if identifier.text.decode('utf-8') == 'NullPointerException':
                return True
    return False

def identify_generic_exception_handling(node: Node):
    catch_clauses = get_catch_clause(node)
    for catch_clause in catch_clauses:
        if is_generic_catch(catch_clause[0]):
            return True
    return False

def check_instanceof_in_catch(node: Node):
    captures = QUERY_CATCH_BLOCK.captures(node)
    for capture, _ in captures:
        if 'instanceof' in capture.text.decode('utf-8'):
            return True
    return False

def count_instanceof_in_catch(node: Node):
    captures = QUERY_CATCH_BLOCK.captures(node)
    count = 0
    for capture, _ in captures:
        if 'instanceof' in capture.text.decode('utf-8'):
            count += 1
    return count


def check_destructive_wrapping(node: Node):
    # Verifica se o nó tem um bloco catch
    catch_clauses = QUERY_CATCH_CLAUSE.captures(node)
    if len(catch_clauses) == 0:
        return False

    for catch_clause in catch_clauses:
        # Obtém o identificador do bloco catch
        catch_identifier = QUERY_CATCH_IDENTIFIER_BODY.captures(catch_clause[0])
        if len(catch_identifier) == 0:
            continue

        catch_identifier = catch_identifier[0][0].text.decode('utf-8')

        # Verifica se o bloco catch tem um throw statement
        throw_statements = QUERY_THROW_STATEMENT_IDENTIFIER.captures(catch_clause[0])
        for throw_statement in throw_statements:
            if 'throw.new.identifier' in throw_statement[1]:
                # Se o throw statement é uma nova instância de uma exceção,
                # então o code smell "Destructive Wrapping" está presente
                return True
            elif 'throw.existing.identifier' in throw_statement[1]:
                throw_identifier = throw_statement[0].text.decode('utf-8')

                # Se o identificador do throw statement é o mesmo do bloco catch
                # e a exceção original não é passada para o construtor da nova exceção
                # então o code smell "Destructive Wrapping" está presente
                if throw_identifier == catch_identifier and not is_generic_throw(throw_statement[0], catch_identifier):
                    return True

    return False

def check_cause_in_catch(node: Node):
    captures = QUERY_CATCH_BLOCK.captures(node)
    for capture, _ in captures:
        for n in capture.named_children:
            method_invocations = QUERY_METHOD_INVOCATION.captures(n)
            for method_invocation, _ in method_invocations:
                if 'getCause' in method_invocation.text.decode('utf-8'):
                    return True
    return False

def count_get_cause_in_catch(node: Node):
    captures = QUERY_CATCH_BLOCK.captures(node)
    count = 0
    for capture, _ in captures:
        for n in capture.named_children:
            method_invocations = QUERY_METHOD_INVOCATION.captures(n)
            for method_invocation, _ in method_invocations:
                if 'getCause' in method_invocation.text.decode('utf-8'):
                    count += 1
    return count
