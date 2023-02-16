from tree_sitter.binding import Node
from tree_sitter_lang import QUERY_FUNCTION_DEF, QUERY_FUNCTION_LITERAL, parser


def get_function_literal(node: Node):
    captures =  QUERY_FUNCTION_LITERAL.captures(node)
    if len(captures) == 0:
        #raise FunctionDefNotFoundException("Not found")
        print("Not found")
    return captures[0][0], captures[0][1]


func = parser.parse(
    b"""
def teste():
    try:
        print(a)
        try:
            print(a)
        except:
            pass
    except:
        pass"""
).root_node


literal = get_function_literal(func)
print(literal)

