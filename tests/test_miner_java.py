import unittest

from miner_py_src.java.miner_java_utils import ( Slices, check_cause_in_catch, check_destructive_wrapping, check_function_has_catch_handler, check_function_has_nested_try, check_instanceof_in_catch, check_throw_within_finally, check_throwing_null_pointer_exception, count_finally, count_get_cause_in_catch, count_instanceof_in_catch, count_lines_of_function_body, count_nested_try, count_throw, count_try_catch_throw, count_try_return, count_untyped_throw, get_try_slices, identify_generic_exception_handling)


from miner_py_src.java.tree_sitter_java import QUERY_METHOD_DEF, parser


class TestCheckFunctionHasExceptionHandler(unittest.TestCase):
    def test_exception_handler(self): 
        actual_check = check_function_has_catch_handler(parser.parse(b"""
static void test() {
    try {
        System.out.println("try");
    } catch (Exception e) {
        System.out.println("catch");
    }
}""").root_node)
        self.assertTrue(actual_check)

    def test_function_without_exception_handler(self):
        actual_check = check_function_has_catch_handler(parser.parse(b"""
static void test() {
    System.out.println("try");
}""").root_node)
        self.assertFalse(actual_check)

class TestCountLines(unittest.TestCase):
    def test_count_lines_multiple_function_def(self):
        tree = parser.parse(b"""
public class Main {
    
    static int test() {
        System.out.println("test1");
        return 0;
    }

    static int test2() {
        System.out.println("test2");
        System.out.println("test3");
        return 0;
    }
}
""")
        captures = QUERY_METHOD_DEF.captures(tree.root_node)
        second_function = captures[1][0]

        expected = 4
        actual = count_lines_of_function_body(second_function)

        self.assertEqual(actual, expected)

    def test_count_lines_with_string(self):
        tree = parser.parse(b"""
public class Main {
    static int test() {
        String string = "Lorem ipsum dolor sit amet,
        consectetur adipiscing elit, sed do eiusmod tempor incididunt
        ut labore et dolore magna aliqua.";
        try {
            System.out.println("test");
        } catch (Exception e) {
            System.out.println("catch");
        }
        return 0;
    }
}
""")
        captures = QUERY_METHOD_DEF.captures(tree.root_node)
        function_defnition = captures[0][0]

        actual_count = count_lines_of_function_body(function_defnition)
        expected_count = 10

        self.assertEqual(actual_count, expected_count)

    def test_empty_function(self):
        actual_count = count_lines_of_function_body(parser.parse(b"""
    static int test() {
    }""").root_node)

        self.assertEqual(actual_count, 1)
        
class TestGetTrySlices(unittest.TestCase):
    def test_get_try_slices(self):
        code = b"""
static int test() {
    try {
        System.out.println("try");
    } catch (Exception e) {
        System.out.println("catch");
    } finally {
        System.out.println("catch");
    }
}
"""                   
        actual = get_try_slices(parser.parse(code).root_node)   
        excepted = Slices(try_block_start=2,catch_handlers=[(4,6)],finally_handler=(6,8))

        self.assertEqual(actual, excepted)

    def test_get_try_slices_when_a_file_has_multiple_functions(self):
        code = b"""
static int test() {
    return 0;
}

static int test() {
    try {
        System.out.println("try");
    } catch (Exception e) {
        System.out.println("catch");
    } finally {
        System.out.println("catch");
    }

    try {
        System.out.println("try");
    } catch (Exception e) {
        System.out.println("catch");
    }
}"""
        captures = QUERY_METHOD_DEF.captures(parser.parse(code).root_node)
        second_function, _ = captures[1]

        actual = get_try_slices(second_function)
        excepted = Slices(try_block_start=2,catch_handlers=[(4,6),(12,14)],finally_handler=(6,8))

        self.assertEqual(actual, excepted)

class TestCounters(unittest.TestCase):
    def test_count_untyped_throw_OK(self):
        code = b"""
static void test() {
    throw new TestException();
}"""
        captures = QUERY_METHOD_DEF.captures(parser.parse(code).root_node)
        function_def, _ = captures[0]

        actual = count_untyped_throw(function_def)
        excepted = 0

        self.assertEqual(actual, excepted)

    def test_count_untyped_throw_found(self):
        code = b"""
static void test() {
    throw new Error();
}"""
        captures = QUERY_METHOD_DEF.captures(parser.parse(code).root_node)
        function_def, _ = captures[0]

        actual = count_untyped_throw(function_def)
        excepted = 1

        self.assertEqual(actual, excepted)

    def test_count_try_catch_throw_OK(self):
        code = b'''
    public void test() {
        try {
            int a = 1 / 0;
        } catch (ArithmeticException e) {
            throw new IllegalArgumentException("division by 0");
        }
    }'''

        captures = QUERY_METHOD_DEF.captures(parser.parse(code).root_node)
        method_def, _ = captures[0]

        actual = count_try_catch_throw(method_def)
        expected = 0

        self.assertEqual(actual, expected)

    def test_count_try_catch_throw_found(self):
        code = b'''
    public void test() {
        try {
            int a = 1 / 0;
        } catch (ArithmeticException e) {
            throw new Exception("division by 0");
        }'''

        captures = QUERY_METHOD_DEF.captures(parser.parse(code).root_node)
        method_def, _ = captures[0]
        actual = count_try_catch_throw(method_def)
        expected = 1
        self.assertEqual(actual, expected)

    def test_count_throw(self):
        code = b'''
    public void test() {
        if(true) {
            throw new Exception();
        }

        try {
            int i=0;
        } catch (Exception e) {
            throw new Exception();
        }'''

        captures = QUERY_METHOD_DEF.captures(parser.parse(code).root_node)
        method_def, _ = captures[0]
        actual = count_throw(method_def)
        expected = 2
        self.assertEqual(actual, expected)

        def test_count_count_try_return(self):
            code = b'''
    public void test() {
        try {
            return;
        } catch (Exception e) {
            throw new Exception();
        }'''

            captures = QUERY_METHOD_DEF.captures(parser.parse(code).root_node)
            method_def, _ = captures[0]
            actual = count_try_return(method_def)
            expected = 1
            self.assertEqual(actual, expected)

class TestThrowQueries(unittest.TestCase):
    def test_count_non_generic_throw(self):
        code = b'''
    public void test() {
        try {
            return;
        } catch (Exception e) {
            throw new Exception();
        }'''

        captures = QUERY_METHOD_DEF.captures(parser.parse(code).root_node)
        method_def, _ = captures[0]
        actual = count_throw(method_def)
        expected = 1
        self.assertEqual(actual, expected)

    def test_count_try_finally(self):
        code = b'''
    public void test() {
        try { 
            int a = 0;
        } catch {
            throw new Exception();
        } finally {
            return;
        }'''

        captures = QUERY_METHOD_DEF.captures(parser.parse(code).root_node)
        method_def, _ = captures[0]
        actual = count_finally(method_def)
        expected = 1

        self.assertEqual(actual, expected)


class TestCheckThrowWithinFinally(unittest.TestCase):
    def test_throw_within_finally(self):
        code = b"""
        public void test() {
            try {
                System.out.println("try");
            } catch (Exception e) {
                System.out.println("catch");
            } finally {
                throw new Exception();
            }
        }"""
        captures = QUERY_METHOD_DEF.captures(parser.parse(code).root_node)
        method_def, _ = captures[0]
        actual = check_throw_within_finally(method_def)
        self.assertTrue(actual)

    def test_no_throw_within_finally(self):
        code = b"""
        public void test() {
            try {
                System.out.println("try");
            } catch (Exception e) {
                System.out.println("catch");
            } finally {
                System.out.println("finally");
            }
        }"""
        captures = QUERY_METHOD_DEF.captures(parser.parse(code).root_node)
        method_def, _ = captures[0]
        actual = check_throw_within_finally(method_def)
        self.assertFalse(actual)

class TestCheckThrowingNullPointerException(unittest.TestCase):
    def test_throwing_null_pointer_exception(self):
        code = b"""
        public void test() {
            throw new NullPointerException();
        }"""
        captures = QUERY_METHOD_DEF.captures(parser.parse(code).root_node)
        method_def, _ = captures[0]
        actual = check_throwing_null_pointer_exception(method_def)
        self.assertTrue(actual)

    def test_not_throwing_null_pointer_exception(self):
        code = b"""
        public void test() {
            throw new Exception();
        }"""
        captures = QUERY_METHOD_DEF.captures(parser.parse(code).root_node)
        method_def, _ = captures[0]
        actual = check_throwing_null_pointer_exception(method_def)
        self.assertFalse(actual)

class TestIdentifyGenericExceptionHandling(unittest.TestCase):
    def test_generic_exception_handling(self):
        code = b"""
        public void test() {
            try {
                // code
            } catch (Exception e) {
                // handle exception
            }
        }"""
        captures = QUERY_METHOD_DEF.captures(parser.parse(code).root_node)
        method_def, _ = captures[0]
        actual = identify_generic_exception_handling(method_def)
        self.assertTrue(actual)

    def test_specific_exception_handling(self):
        code = b"""
        public void test() {
            try {
                // code
            } catch (NullPointerException e) {
                // handle exception
            }
        }"""
        captures = QUERY_METHOD_DEF.captures(parser.parse(code).root_node)
        method_def, _ = captures[0]
        actual = identify_generic_exception_handling(method_def)
        self.assertFalse(actual)


class TestCheckInstanceOfInCatch(unittest.TestCase):
    def test_instanceof_in_catch(self):
        code = b"""
        public void test() {
            try {
                // some code
            } catch (Exception e) {
                if (e instanceof IOException) {
                    // handle IOException
                }
            }
        }"""
        captures = QUERY_METHOD_DEF.captures(parser.parse(code).root_node)
        method_def, _ = captures[0]
        actual = check_instanceof_in_catch(method_def)
        self.assertTrue(actual)

    def test_no_instanceof_in_catch(self):
        code = b"""
        public void test() {
            try {
                // some code
            } catch (Exception e) {
                // handle exception
            }
        }"""
        captures = QUERY_METHOD_DEF.captures(parser.parse(code).root_node)
        method_def, _ = captures[0]
        actual = check_instanceof_in_catch(method_def)
        self.assertFalse(actual)

class TestCountInstanceOfInCatch(unittest.TestCase):
    def test_instanceof_in_catch(self):
        code = b"""
        public void test() {
            try {
                // some code
            } catch (Exception e) {
                if (e instanceof IOException) {
                    // handle IOException
                }
            }
        }"""
        captures = QUERY_METHOD_DEF.captures(parser.parse(code).root_node)
        method_def, _ = captures[0]
        actual = count_instanceof_in_catch(method_def)
        self.assertEqual(actual, 1)

    def test_no_instanceof_in_catch(self):
        code = b"""
        public void test() {
            try {
                // some code
            } catch (Exception e) {
                // handle exception
            }
        }"""
        captures = QUERY_METHOD_DEF.captures(parser.parse(code).root_node)
        method_def, _ = captures[0]
        actual = count_instanceof_in_catch(method_def)
        self.assertEqual(actual, 0)

class TestCheckFunctionHasNestedTry(unittest.TestCase):
    def test_function_has_no_nested_try(self):
        code = b"""
        public void test() {
            try {
                System.out.println("Try");
            } catch (Exception e) {
                System.out.println("Catch");
            }
        }"""
        captures = QUERY_METHOD_DEF.captures(parser.parse(code).root_node)
        method_def, _ = captures[0]
        actual = check_function_has_nested_try(method_def)
        self.assertFalse(actual)

    def test_function_has_nested_try(self):
        code = b"""
        public void test() {
            try {
                try {
                    try {
                        System.out.println("Nested try");
                    } catch (Exception e) {
                        System.out.println("Nested catch");
                    }
                } catch (Exception e) {
                    System.out.println("Nested catch");
                }
            } catch (Exception e) {
                System.out.println("Outer catch");
            }
        }"""
        captures = QUERY_METHOD_DEF.captures(parser.parse(code).root_node)
        method_def, _ = captures[0]
        actual = check_function_has_nested_try(method_def)
        self.assertTrue(actual)

class TestCountNestedTry(unittest.TestCase):
    def test_count_nested_try(self):
        code = b"""
        public void test() {
            try {
                try {
                    try {
                        System.out.println("Nested try");
                    } catch (Exception e) {
                        System.out.println("Nested catch");
                    }
                } catch (Exception e) {
                    System.out.println("Nested catch");
                }
            } catch (Exception e) {
                System.out.println("Outer catch");
            }
        }"""
        captures = QUERY_METHOD_DEF.captures(parser.parse(code).root_node)
        method_def, _ = captures[0]
        actual = count_nested_try(method_def)
        self.assertEqual(actual, 1)

    def test_no_nested_try(self):
        code = b"""
        public void test() {
            try {
                System.out.println("Try");
            } catch (Exception e) {
                System.out.println("Catch");
            }
        }"""
        captures = QUERY_METHOD_DEF.captures(parser.parse(code).root_node)
        method_def, _ = captures[0]
        actual = count_nested_try(method_def)
        self.assertEqual(actual, 0)

class TestCheckDestructiveWrapping(unittest.TestCase):
    def test_destructive_wrapping(self):
        code = b"""
        public void test() {
            try {
                // some code
            } catch (Exception e) {
                throw new Exception();
            }
        }"""
        captures = QUERY_METHOD_DEF.captures(parser.parse(code).root_node)
        method_def, _ = captures[0]
        actual = check_destructive_wrapping(method_def)
        self.assertTrue(actual)

    def test_no_destructive_wrapping(self):
        code = b"""
        public void test() {
            try {
                // some code
            } catch (Exception e) {
                throw e;
            }
        }"""
        captures = QUERY_METHOD_DEF.captures(parser.parse(code).root_node)
        method_def, _ = captures[0]
        actual = check_destructive_wrapping(method_def)
        self.assertFalse(actual) 

class TestCheckCauseInCatch(unittest.TestCase):
    def test_cause_in_catch(self):
        code = b"""
        public void test() {
            try {
                // some code
            } catch (Exception e) {
                e.getCause();
            }
        }"""
        captures = QUERY_METHOD_DEF.captures(parser.parse(code).root_node)
        method_def, _ = captures[0]
        actual = check_cause_in_catch(method_def)
        self.assertTrue(actual)

    def test_no_cause_in_catch(self):
        code = b"""
        public void test() {
            try {
                // some code
            } catch (Exception e) {
                // no getCause
            }
        }"""
        captures = QUERY_METHOD_DEF.captures(parser.parse(code).root_node)
        method_def, _ = captures[0]
        actual = check_cause_in_catch(method_def)
        self.assertFalse(actual)


class TestCountGetCauseInCatch(unittest.TestCase):
    def test_count_get_cause_in_catch(self):
        code = b"""
        public void test() {
            try {
                // some code
            } catch (Exception e) {
                e.getCause();
                e.getCause();
            }
        }"""
        captures = QUERY_METHOD_DEF.captures(parser.parse(code).root_node)
        method_def, _ = captures[0]
        actual = count_get_cause_in_catch(method_def)
        self.assertEqual(actual, 2)

    def test_no_get_cause_in_catch(self):
        code = b"""
        public void test() {
            try {
                // some code
            } catch (Exception e) {
                // no getCause
            }
        }"""
        captures = QUERY_METHOD_DEF.captures(parser.parse(code).root_node)
        method_def, _ = captures[0]
        actual = count_get_cause_in_catch(method_def)
        self.assertEqual(actual, 0)