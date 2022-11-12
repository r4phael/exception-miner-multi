import unittest
import ast
from miner_py_src.miner_py_utils import check_function_has_except_handler, check_function_has_nested_try, get_function_def


class TestCheckFunctionHasExceptionHandler(unittest.TestCase):
    def test_exception_handler_one_indent_level(self):

        actual_check = check_function_has_except_handler(get_function_def(ast.parse("""
def teste():
    try:
        print(a)
    except:
        pass
""")))

        self.assertTrue(actual_check)

    def test_function_without_exception_handler(self):

        actual_check = check_function_has_except_handler(get_function_def(ast.parse("""
def teste():
    print(a)""")))

        self.assertFalse(actual_check)


class TestFuncionHasNestedTry(unittest.TestCase):
    def test_nested_try_one_indent_level(self):
        actual_check = check_function_has_nested_try(get_function_def(ast.parse("""
def teste():
    try:
        print(a)
        try:
            print(a)
        except:
            pass
    except:
        pass""")))
        self.assertTrue(actual_check)

    def test_function_without_nested_try(self):
        actual_check = check_function_has_nested_try(get_function_def(ast.parse("""
def teste():
    try:
        print(a)
    except:
        pass""")))
        self.assertFalse(actual_check)

    def test_nested_try_two_indentation_levels(self):
        actual_check = check_function_has_nested_try(get_function_def(ast.parse("""
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

    print(b)""")))
        self.assertTrue(actual_check)

    def test_function_try_same_indentation(self):
        actual_check = check_function_has_nested_try(get_function_def(ast.parse("""
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

    print(b)""")))

        self.assertFalse(actual_check)


if __name__ == '__main__':
    unittest.main()
