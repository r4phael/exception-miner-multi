import unittest

from call_graph import CFG


cfg_mock = {
    "teste/teste.py:raise_exception": {
        "called_by": {
            "teste/teste.py:except_caller": 1
        }
    },
    "teste/teste.py:except_caller": {
        "calls": {
            "teste/teste.py:raise_exception": 1
        },
        "called_by": {
            "teste/teste.py:except_caught": 1
        }
    }
}


class TestCFG(unittest.TestCase):
    def test_flow_exception_handled(self):
        graph = CFG(cfg_mock,
                    {'teste/teste.py:except_caller': ["ValueError"]})

        actual = graph.get_uncaught_exceptions('teste/teste.py:raise_exception',
                                               ['ValueError'])
        expected = {}

        self.assertEqual(actual, expected)

    def test_flow_exception_unhandled(self):
        graph = CFG(cfg_mock,
                    {'teste/teste.py:except_caller': ["ValueError"]})

        actual = graph.get_uncaught_exceptions('teste/teste.py:raise_exception',
                                               ['ValueError', 'NewException'])

        expected = {'teste/teste.py:except_caller': ['NewException']}

        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
