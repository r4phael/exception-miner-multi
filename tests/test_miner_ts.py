import unittest

from ..miner_py_src.typescript.miner_ts_utils import (Slices,
                                         check_function_has_catch_handler,
                                         check_function_has_nested_try,
                                         count_nested_try,
                                         count_lines_of_function_body,
                                         get_try_slices,
                                         count_untyped_throw,
                                         count_try_catch_throw,
                                         count_throw,
                                         count_non_generic_throw,
                                         count_not_recommended_throw,
                                         count_try_return,
                                         count_finally,
                                         get_throw_identifiers,
                                         get_catch_statements,
                                         get_function_defs,
                                         count_empty_catch,
                                         count_useless_catch,
                                         count_catch_reassigning_identifier,
                                         )

from miner_py_src.typescript.tree_sitter_ts import QUERY_FUNCTION_DEF, parser


class TestCheckFunctionHasExceptionHandler(unittest.TestCase):
    def test_exception_handler(self):
        actual_check = check_function_has_catch_handler(parser.parse(b"""
function test() {
    try {
        console.log('try')
    } catch(e) {
        console.log('catch')
    }
}
""").root_node)

        self.assertTrue(actual_check)

    def test_function_without_exception_handler(self):

        actual_check = check_function_has_catch_handler(parser.parse(b"""
function test() {
    console.log('try')
}""").root_node)

        self.assertFalse(actual_check)

class TestFuncionHasNestedTry(unittest.TestCase):
    def test_nested_try(self):
        actual_check = check_function_has_nested_try(parser.parse(b"""
function test() {
    try {
        console.log('try')
        try {
            console.log('second try')
        } catch(e) {
            console.log('first catch')
        }
    } catch(e) {
        console.log('catch')
    }
}""").root_node)
        self.assertFalse(actual_check)

    def test_function_without_nested_try(self):
        actual_check = check_function_has_nested_try(parser.parse(b"""
function test() {
    try {
        console.log('try')
    } catch(e) {
        console.log('catch')
    }
}""").root_node)
        self.assertFalse(actual_check)

    def test_function_nested_try_count(self):
        actual_check = count_nested_try(parser.parse(b"""
function test() {
    try {
        console.log('try')
        try {
            console.log('second try')
            try {
                console.log('third try')
            } catch(e) {
                console.log('first catch')
            }
        } catch(e) {
            console.log('second catch')
        }
    } catch(e) {
        console.log('third catch')
    }
}
""").root_node)

        self.assertEquals(actual_check, 1)

class TestCountLines(unittest.TestCase):
    def test_count_lines_multiple_function_defs(self):
        tree = parser.parse(b'''
function test() {
    console.log('test1')
    return 0
}

function test2() {
    console.log('test2')
    console.log('test3')
    return 0
}
''')
        captures = QUERY_FUNCTION_DEF.captures(tree.root_node)
        second_function = captures[1][0]

        expected = 4
        actual = count_lines_of_function_body(second_function)

        self.assertEqual(actual, expected)

    def test_count_lines_with_string(self):
        tree = parser.parse(b'''function test() {
    const string = `Lorem ipsum dolor sit amet, 
    consectetur adipiscing elit, sed do eiusmod tempor incididunt
     ut labore et dolore magna aliqua.`
    try {
        console.log('test')
    } catch {
        console.log('catch')
    }
    return 0
}''')

        captures = QUERY_FUNCTION_DEF.captures(tree.root_node)
        function_definition = captures[0][0]

        actual_count = count_lines_of_function_body(function_definition)
        expected = 10

        self.assertEqual(actual_count, expected)

    def test_empty_function(self):
        actual_count = count_lines_of_function_body(parser.parse(b'''
function test() {
}''').root_node)

        self.assertEqual(actual_count, 1)
##Por que?
#     def test_not_utf8_function(self):

#         code = r'''
# def not_utf8():
#     """
#     multiline string
#     """
#     print(f"\x1b]8;id={self._link_id};{self._link}\x1b\\{rendered}\x1b]8;;\x1b\\")'''

#         actual_count = count_lines_of_function_body(
#             parser.parse(bytes(code, 'utf-8')).root_node)
#         self.assertEqual(actual_count, 4)

class TestGetTrySlices(unittest.TestCase):
    def test_get_try_slices(self):
        code = b'''
function test() {
    console.log('b')
    try {
        console.log('test')
    } catch {
        console.log('failed')
    }

    try {
        console.log('nested')
    } catch {
        console.log('failed')
    }
}
'''

        actual = get_try_slices(parser.parse(code).root_node)
        expected = Slices(try_block_start=3, handlers=[(5, 7), (11, 13)])

        self.assertEqual(actual, expected)

    def test_get_try_slices_when_a_file_has_multiple_functions(self):
        code = b'''
function ignore_function_same_file() {
    return
}

function test() {
    console.log('b')
    try {
        console.log('test')
    } catch {
        console.log('failed')
    }

    try {
        console.log('nested')
    } catch {
        console.log('failed')
    }
}'''

        captures = QUERY_FUNCTION_DEF.captures(parser.parse(code).root_node)
        second_function, _ = captures[1]

        actual = get_try_slices(second_function)
        expected = Slices(try_block_start=3, handlers=[(5, 7), (11, 13)])

        self.assertEqual(actual, expected)

class TestCounters(unittest.TestCase):
    def test_count_untyped_throw_OK(self):
        code = b'''
function test() {
    console.log('b')
    throw new TestError()
}'''
        captures = QUERY_FUNCTION_DEF.captures(parser.parse(code).root_node)
        func_def, _ = captures[0]

        actual = count_untyped_throw(func_def)
        expected = 0

        self.assertEqual(actual, expected)

    def test_count_untyped_throw_found(self):
        code = b'''
function test() {
    if(3 > 2) {
        throw new Error('Test')
    }
    if(4 > 3) {
        throw new Error('Test2')
    }
}'''

        captures = QUERY_FUNCTION_DEF.captures(parser.parse(code).root_node)
        func_def, _ = captures[0]

        actual = count_untyped_throw(func_def)
        expected = 2

        self.assertEqual(actual, expected)

    def test_count_try_catch_throw_OK(self):
        code = b'''
function test() {
    try {
        const a = 1/0
    } catch (e) {
        if(e instanceof ZeroDivisionError) {
            throw new ValueError('division by 0')
        }
    }
}'''

        captures = QUERY_FUNCTION_DEF.captures(parser.parse(code).root_node)
        func_def, _ = captures[0]

        actual = count_try_catch_throw(func_def)
        expected = 0

        self.assertEqual(actual, expected)

    def test_count_try_catch_throw_found(self):
        code = b'''
function test() {
    try {
        const a = 1/0
    } catch (e) {
        if(3>2) {
            throw new ValueError("blabla")
        }
        throw new Error("a")
    }
}'''

        captures = QUERY_FUNCTION_DEF.captures(parser.parse(code).root_node)
        func_def, _ = captures[0]

        actual = count_try_catch_throw(func_def)
        expected = 0

        self.assertEqual(actual, expected)

    def test_count_throw(self):
        code = b'''
function test() {
    if(3 < 2) {
        throw new Error('error')
    }

    try {
        const a = 1/0
    } catch (e) {
        throw new Error('try error')
    }
}'''

        captures = QUERY_FUNCTION_DEF.captures(parser.parse(code).root_node)
        func_def, _ = captures[0]

        actual = count_throw(func_def)
        expected = 2

        self.assertEqual(actual, expected)

    def test_count_try_return(self):
        code = b'''
function test() {
    try {
        if(3 > 2) {
            if(true) {
                return
            }
        }
    } catch (e) {
        throw new Error('try error')
    }
}'''

        captures = QUERY_FUNCTION_DEF.captures(parser.parse(code).root_node)
        func_def, _ = captures[0]

        actual = count_try_return(func_def)
        expected = 1

        self.assertEqual(actual, expected)

class TestThrowQueries(unittest.TestCase):
    def test_count_recommended_throw_statement(self):
        code = b'''
function test() {
    if(3 > 2) {
        throw Error('first')
    } else if (2 > 3) {
        throw ({ 'value': 'Error' })
    } else if ( 4 < 2 ) {
        throw new Error('third')
    }
    throw 'error'
}'''
        node = parser.parse(code).root_node
        result = count_not_recommended_throw(node)
        expected = 3
        self.assertEqual(result, expected)
    
    def test_count_non_generic_throw(self):
        code = b'''
function test() {
    if(3 > 2) {
        throw Error('first')
    } else if (2 > 3) {
        throw "second"
    } else if ( 4 < 2 ) {
        throw new Error('third')
    }
    throw 'error'
}'''
        funcNode = parser.parse(code).root_node
        result = count_non_generic_throw(funcNode)
        expected = 0
        self.assertEqual(result, expected)

    def test_count_non_generic_throw_match(self):
        code = b'''
function test() {
    if(3 > 2) {
        throw Error('first')
    } else if (2 > 3) {
        throw "second"
    } else if ( 4 < 2 ) {
        throw new MyErrorType('third')
    }
    throw 'error'
}'''
        funcNode = parser.parse(code).root_node
        result = count_non_generic_throw(funcNode)
        expected = 1
        self.assertEqual(result, expected)

    def test_get_throw_str_identifiers(self):
        code = b'''
function test() {
    if(3 > 2) {
        throw new ValueError('first')
    } else if (4 > 3) {
        throw new Value2Error('second')
    }
    throw 'error'
}'''

        captures = QUERY_FUNCTION_DEF.captures(parser.parse(code).root_node)
        func_def, _ = captures[0]

        actual = get_throw_identifiers(func_def)
        print(f"############### actual ################: {actual}")
        expected = ['ValueError', 'Value2Error']

        self.assertEqual(actual, expected)

    def test_count_try_finally(self):
        code = b'''
function test() {
    try {
        const a = 4/2
    } catch {
        console.log('erro')
    } finally {
        console.log('cleanup')
    }
}'''

        captures = QUERY_FUNCTION_DEF.captures(parser.parse(code).root_node)
        func_def, _ = captures[0]

        actual = count_finally(func_def)
        expected = 1

        self.assertEqual(actual, expected)

class TestCatchQueries(unittest.TestCase):
    def test_count_catch_reassigning(self):
        actual_check = count_catch_reassigning_identifier(parser.parse(b'''
function badCatchExamplethree() {
  try {
  	const a = JSON.parse("value")
  } catch (error) {
    value = { 'value': 2 }
    teste = value
    error = teste
    console.error(error)
  }
}''').root_node)
        expected = 1
        self.assertEqual(actual_check, expected)

    def test_count_useless_catch(self):
        actual_check = count_useless_catch(parser.parse(b'''
function test() {
    try {
        const a = 4/2
    } catch(err) {
        throw err                                    
    }
}''').root_node)
        expected = 1
        self.assertEqual(actual_check, expected)

    def test_count_empty_catch(self):
        actual_check = count_empty_catch(parser.parse(b"""
function test() {
    try {
        const a = 4/2
    } catch(err) {}
}""").root_node)
        expected = 1
        self.assertEqual(actual_check, expected)
        
    def test_get_catch_block(self):
        code = b'''
function test() {
    try {
        const a = 4/2
    } catch(err) {
        console.log('erro')
    }
}'''
        captures = parser.parse(code)
        captures = get_function_defs(captures)

        child = captures[0]
        actual = list(map(lambda x: x[0].text.decode('utf-8'), get_catch_statements(child)))
        expected = ["console.log('erro')"]
        
        self.assertEqual(actual, expected)
