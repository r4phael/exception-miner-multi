from tree_sitter_lang import QUERY_FUNCTION_DEF, QUERY_FUNCTION_NAME, parser
from tree_sitter.binding import Node, Tree


def get_function_def(node: Node):
    captures = QUERY_FUNCTION_NAME.captures(node)
    # if len(captures) == 0:
    #     raise FunctionDefNotFoundException("Not found")
    return captures


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


asd = get_function_def(func)
print(asd)
