from tree_sitter import Language, Parser
from tree_sitter.binding import Query

if __name__ == '__main__':
    root = '../'
else:
    root = ''

Language.build_library(
    root + 'build/my-languages.so',
    [
        root + 'tree-sitter-python'
    ]
)

PY_LANGUAGE = Language(root + 'build/my-languages.so', 'python')

parser = Parser()
parser.set_language(PY_LANGUAGE)

QUERY_FUNCTION_DEF: Query = PY_LANGUAGE.query(
    "(function_definition) @function.def")

QUERY_EXPRESSION_STATEMENT: Query = PY_LANGUAGE.query(
    """(expression_statement) @expression.stmt""")

QUERY_TRY_STMT: Query = PY_LANGUAGE.query(
    """(try_statement) @try.statement""")

QUERY_TRY_EXCEPT: Query = PY_LANGUAGE.query(
    """(try_statement
        (except_clause)* @except.clause) @try.stmt""")

QUERY_EXCEPT_CLAUSE: Query = PY_LANGUAGE.query(
    """(except_clause) @except.clause""")

QUERY_EXCEPT_EXPRESSION: Query = PY_LANGUAGE.query(
    """(except_clause (_) @except.expression (block))""")

QUERY_PASS_BLOCK: Query = PY_LANGUAGE.query(
    """(block 
	(pass_statement) @pass.stmt )""")

QUERY_FIND_IDENTIFIERS: Query = PY_LANGUAGE.query(
    """(identifier) @identifier""")


tree = parser.parse(bytes("""
try:
    print('teste')
except Exception:
    pass
""", "utf8"))

root_node = tree.root_node
captures = QUERY_EXCEPT_EXPRESSION.captures(tree.root_node)
cap = captures[0][0]
if cap.is_named:
    print(captures[0][0].text == b'Exception')  # type: ignore
