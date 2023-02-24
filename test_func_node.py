from tree_sitter.binding import Node
from miner_py_src.tree_sitter_lang import QUERY_FUNCTION_DEF, QUERY_FUNCTION_IDENTIFIER, parser
#from miner_py_src.tree_sitter_lang import parser as tree_sitter_parser

from miner_py_src.miner_py_utils import get_function_defs


def get_function_literal(node: Node):
    captures =  QUERY_FUNCTION_IDENTIFIER.captures(node)
    if len(captures) == 0:
        #raise FunctionDefNotFoundException("Not found")
        print("Not found")
    return captures[0][0], captures[0][1]

def get_function_body(node: Node):
    return node.text.decode("utf-8")


def get_function_else(tree):
    queue = [tree.root_node]

    while not len(queue) == 0:
        node = queue.pop(0)
        print(node.type)

        #start = max(current.start_point[0], hunk_from);
        #end = min(current.end_point[0], hunk_to);

        #if (end >= start):
        # if current.type in language.get_elements_to_collect():
        #     element = CodeElement(current.type, current.start_point[0], current.end_point[0])
        #     element.set_body_preview(current.text)

        if node.type == "try_statement":
            print('Found try-except-else block:')
            print(node.children)
            try_node = node.children[0]
            except_nodes = node.children[1:-1]
            else_node = node.children(-1) if len(node.children) > len(except_nodes) else None
            
            print(f'Try Block: {try_node}')
            for except_node in except_nodes:
                print(f'Except Block: {except_node}')
            if else_node:
                print(f'Else Block: {else_node}')


        for child in node.children:
            queue.append(child)


func = parser.parse(
    b"""
    def teste():
        try:
            print(a)
        except Exception as e:
            pass	
    """
).root_node

func_else = parser.parse(
    b"""
    def divide(x, y):
    try:
        # Floor Division : Gives only Fractional
        # Part as Answer
        result = x // y
    except ZeroDivisionError:
        print("Sorry ! You are dividing by zero ")
    
    if x>y :
        print('x is greater than y')
    else:
        print("Nope, x is not greater than y")
    
    try:
        # Floor Division : Gives only Fractional
        # Part as Answer
        result = x // y
    except ZeroDivisionError:
        print("Sorry ! You are dividing by zero ")
    else:
        print("Yeah ! Your answer is :", result)
    finally: 
        # this block is always executed  
        # regardless of exception generation. 
        print('This is always executed')  
    """
)



if __name__ == '__main__':
    #body = get_function_body(func)
    #captures = get_function_defs(func_else)
    body = get_function_else(func_else)
    print(body)