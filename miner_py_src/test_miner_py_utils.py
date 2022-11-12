import unittest
import ast
import codecs
from miner_py_src.miner_py_utils import check_function_has_except_handler, check_function_has_nested_try, count_lines, get_function_def


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


class TestCountLines(unittest.TestCase):
    def test_count_lines_with_string(self):
        actual_count = count_lines(get_function_def(ast.parse('''
def teste_nested_try_except():
    multiline_string = """
    :param n_classes: number of classes
    :param vocab_size: number of words in the vocabulary of the model
    :param emb_size: size of word embeddings
    :param word_rnn_size: size of (bidirectional) word-level RNN
    :param sentence_rnn_size: size of (bidirectional) sentence-level RNN
    :param word_rnn_layers: number of layers in word-level RNN
    :param sentence_rnn_layers: number of layers in sentence-level RNN
    :param word_att_size: size of word-level attention layer
    :param sentence_att_size: size of sentence-level attention layer
    :param dropout: dropout
    """
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

    print(b)''')))

        self.assertEqual(actual_count, 16)

    def test_empty_function(self):
        actual_count = count_lines(get_function_def(ast.parse('''
def empty():
    pass''')))

        self.assertEqual(actual_count, 2)

#     def test_not_utf8_function(self):

#         code = r'''
# def not_utf8():
#     """
#     multiline string
#     """
#     print(f"\x1b]8;id={self._link_id};{self._link}\x1b\\{rendered}\x1b]8;;\x1b\\")'''

#         actual_count = count_lines(get_function_def(ast.parse(codecs.decode(code, 'unicode_escape'))))
#         self.assertEqual(actual_count, 3)

if __name__ == '__main__':
    unittest.main()
