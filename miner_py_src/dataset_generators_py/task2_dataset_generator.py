import ast
from collections import namedtuple
import io
from typing import List
import astunparse
import token
import tokenize

from numpy.random import default_rng

rng = default_rng()

Slices = namedtuple('Slices', [
    'try_lineno',
    'handlers_lineno',
    'end_lineno',
])


class ExceptDatasetGenerator():

    def __init__(self, func_defs: List[ast.FunctionDef]) -> None:
        self.func_defs = func_defs
        self.reset()

    def reset(self):
        self.front_lines = []
        self.except_lines = []

        self.slices = None
        self.current_lineno = None
        self.indentation_counter = 0
        self.token_buffer = []

    def generate(self):
        generated = []

        for f in self.func_defs:
            try:
                # remove lint formatting
                tree = ast.parse(astunparse.unparse(f))
                tree = tree.body[0]

                tokenized_function_def = self.tokenize_function_def(tree)

                if tokenized_function_def is not None:
                    generated += tokenized_function_def
            except SyntaxError as e:
                print(
                    f"###### SyntaxError Error!!! in ast.FunctionDef {f}.\n{str(e)}")
                continue

        return generated

    def clear_line_buffer(self):
        if len(self.token_buffer) == 0:
            return

        indentation = self.indentation_counter * '\t'

        tokenized_line = indentation + ' '.join(self.token_buffer)
        self.token_buffer = []

        if self.current_lineno < self.slices.handlers_lineno[0]:
            self.front_lines.append(tokenized_line)
        else:
            current_except_slice = max(
                [i for i, x in enumerate(self.slices.handlers_lineno) if x <= self.current_lineno])
            self.except_lines[current_except_slice].append(tokenized_line)

    def end_of_generation(self):
        res = []
        for except_line in self.except_lines:
            res.append({
                'try': self.front_lines,
                'except': except_line,
            })

        self.reset()

        return res

    def check_pass(self, node: ast.ExceptHandler):
        return len(node.body) > 0 and not isinstance(node.body[0], ast.Pass)

    def get_slices(self, node: ast.FunctionDef):
        try_index = next(index for index, child in enumerate(
            node.body) if isinstance(child, ast.Try))
        try_ast: ast.Try = node.body[try_index]

        except_handlers_line_numbers = [
            child.lineno for child in try_ast.handlers]

        end_lineno = None
        if len(try_ast.orelse) != 0:
            end_lineno = try_ast.orelse[0].lineno - 1
        elif len(try_ast.finalbody) != 0:
            end_lineno = try_ast.finalbody[0].lineno - 1
        elif len(node.body) > try_index + 1:
            end_lineno = node.body[try_index + 1].lineno

        self.except_lines = [[]
                             for _ in range(len(except_handlers_line_numbers))]
        return Slices(try_lineno=try_ast.lineno,
                      handlers_lineno=except_handlers_line_numbers,
                      end_lineno=end_lineno)

    def handle_indentation(self, token_info: tokenize.TokenInfo):
        if (token_info.type == token.INDENT):
            self.indentation_counter += 1
            return True

        if (token_info.type == token.DEDENT):
            self.indentation_counter -= 1
            self.indentation_counter = max(self.indentation_counter, 0)
            return True
        return False

    def tokenize_function_def(self, node: ast.FunctionDef):
        assert node is not None

        self.slices = self.get_slices(node)

        unparsed_code = astunparse.unparse(node)

        for token_info in tokenize.generate_tokens(io.StringIO(unparsed_code).readline):
            if token_info.start[0] != self.current_lineno:
                self.clear_line_buffer()
                self.current_lineno = token_info.start[0]

                if (self.slices.end_lineno is not None
                        and self.slices.end_lineno <= self.current_lineno):
                    return self.end_of_generation()

            if (token_info.type in [token.COMMENT, token.NEWLINE, token.NL]):
                continue

            if (token_info.type == token.ENDMARKER):
                return self.end_of_generation()

            if not self.handle_indentation(token_info):
                self.token_buffer.append(token_info.string)
