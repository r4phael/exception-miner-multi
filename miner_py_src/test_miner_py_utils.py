import unittest

from miner_py_src.miner_py_utils import (Slices,
                                         check_function_has_except_handler,
                                         check_function_has_nested_try,
                                         count_lines_of_function_body, get_try_slices)
from miner_py_src.tree_sitter_lang import QUERY_FUNCTION_DEF, parser


class TestCheckFunctionHasExceptionHandler(unittest.TestCase):
    def test_exception_handler_one_indent_level(self):
        actual_check = check_function_has_except_handler(parser.parse(b"""
def teste():
    try:
        print(a)
    except:
        pass
""").root_node)

        self.assertTrue(actual_check)

    def test_function_without_exception_handler(self):

        actual_check = check_function_has_except_handler(parser.parse(b"""
def teste():
    print(a)""").root_node)

        self.assertFalse(actual_check)


class TestFuncionHasNestedTry(unittest.TestCase):
    def test_nested_try_one_indent_level(self):
        actual_check = check_function_has_nested_try(parser.parse(b"""
def teste():
    try:
        print(a)
        try:
            print(a)
        except:
            pass
    except:
        pass""").root_node)
        self.assertTrue(actual_check)

    def test_function_without_nested_try(self):
        actual_check = check_function_has_nested_try(parser.parse(b"""
def teste():
    try:
        print(a)
    except:
        pass""").root_node)
        self.assertFalse(actual_check)

    def test_nested_try_two_indentation_levels(self):
        actual_check = check_function_has_nested_try(parser.parse(b"""
def teste_nested_try_except():
    a = 1
    b = 2
    b = a
    print(b)
    try:
        c = b
        print(c)
        if True:
            try:
                print('nested')
            except Exception:
                print('falhou')
    except Exception:
        print('falhou')

    print(b)""").root_node)
        self.assertTrue(actual_check)

    def test_function_try_same_indentation(self):
        actual_check = check_function_has_nested_try(parser.parse(b"""
def teste_nested_try_except():
    a = 1
    b = 2
    b = a
    print(b)
    try:
        c = b
        print(c)
    except Exception:
        print('falhou')
    try:
        print('nested')
    except Exception:
        print('falhou')

    print(b)""").root_node)

        self.assertFalse(actual_check)


class TestCountLines(unittest.TestCase):
    def test_count_lines_multiple_function_defs(self):
        tree = parser.parse(b'''
def funct1():
    print("teste")
    return 0

def funct2():
    print("teste1")
    print("teste2")
    return 0
''')
        captures = QUERY_FUNCTION_DEF.captures(tree.root_node)
        second_function = captures[1][0]

        expected = 3
        actual = count_lines_of_function_body(second_function)

        self.assertEqual(actual, expected)

    def test_count_lines_with_string(self):
        tree = parser.parse(b'''def teste_nested_try_except():
    multiline_string = """
    :param n_classes: number of classes
    :param vocab_size: number of words in the vocabulary of the model
    """
    a = 1
    try:
        c = b
        print(c)
    except Exception:
        print('falhou')
    try:
        print('nested')
    except Exception:
        print('falhou')

    print(b)''')

        captures = QUERY_FUNCTION_DEF.captures(tree.root_node)
        function_definition = captures[0][0]

        actual_count = count_lines_of_function_body(function_definition)

        self.assertEqual(actual_count, 16)

    def test_empty_function(self):
        actual_count = count_lines_of_function_body(parser.parse(b'''
def empty():
    pass''').root_node)

        self.assertEqual(actual_count, 1)

    def test_not_utf8_function(self):

        code = r'''
def not_utf8():
    """
    multiline string
    """
    print(f"\x1b]8;id={self._link_id};{self._link}\x1b\\{rendered}\x1b]8;;\x1b\\")'''

        actual_count = count_lines_of_function_body(
            parser.parse(bytes(code, 'utf-8')).root_node)
        self.assertEqual(actual_count, 4)


class TestGetTrySlices(unittest.TestCase):
    def test_get_try_slices(self):
        code = b'''
def teste_nested_try_except():
    print(b)
    try:
        c = b
        print(c)
    except Exception:
        print('falhou')
    try:
        print('nested')
    except Exception:
        print('falhou')

    print(b)'''

        actual = get_try_slices(parser.parse(code).root_node)
        expected = Slices(try_block_start=3, handlers=[(6, 7), (10, 11)])

        self.assertEqual(actual, expected)

    def test_get_try_slices_when_a_file_has_multiple_functions(self):
        code = b'''
def ignore_function_same_file():
    return

def teste_nested_try_except():
    print(b)
    try:
        c = b
        print(c)
    except Exception:
        print('falhou')
    try:
        print('nested')
        print('nested')
    except Exception:
        print('falhou')

    print(b)'''

        captures = QUERY_FUNCTION_DEF.captures(parser.parse(code).root_node)
        second_function, _ = captures[1]

        actual = get_try_slices(second_function)
        expected = Slices(try_block_start=3, handlers=[(6, 7), (11, 12)])

        self.assertEqual(actual, expected)

    def test_get_try_slices_multi_catch(self):
        code = b'''
def teste_nested_try_except():
    print(b)
    try:
        c = b
        print(c)
    except ValueError:
        print('falhou 1')
    except ZeroDivision:
        print('falhou 2')
        print('falhou 2')
    except Exception:
        print('falhou 3')
    print(b)'''

        captures = QUERY_FUNCTION_DEF.captures(parser.parse(code).root_node)
        func_def, _ = captures[0]

        actual = get_try_slices(func_def)
        expected = Slices(try_block_start=3, handlers=[
                          (6, 7), (8, 10), (11, 12)])

        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
