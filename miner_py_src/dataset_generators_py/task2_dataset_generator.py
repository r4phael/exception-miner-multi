import ast
import io
from typing import List
import astunparse
import token
import tokenize

from numpy.random import default_rng

rng = default_rng()


class ExceptDatasetGenerator():

    def __init__(self, func_defs: List[ast.FunctionDef]) -> None:
        self.func_defs = func_defs
        self.reset()

    def reset(self):
        self.front_lines = []
        self.except_lines = []

        self.current_line = None
        self.indentation_counter = 0
        self.token_buffer = []

    def generate(self):
        generated = []

        for f in self.func_defs:
            try:
                # remove lint formatting
                tree = ast.parse(astunparse.unparse(f))

                tokenized_function_def = self.tokenize_function_def(tree)

                if tokenized_function_def is not None:
                    generated.append(self.tokenize_function_def(tree))
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

        if self.except_reached:
            self.except_lines.append(tokenized_line)
        else:
            self.front_lines.append(tokenized_line)

    def end_of_generation(self):
        res = {
            'try': self.front_lines,
            'except': self.except_lines,
        }

        self.reset()

        return res

    def get_except_slice(self, node: ast.FunctionDef):
        for n in ast.walk(node):
            if isinstance(n, ast.ExceptHandler):
                tokens = list(tokenize.generate_tokens(
                    io.StringIO(astunparse.unparse(n)).readline))
                for tok in reversed(tokens):
                    if tok.type not in [token.NEWLINE, token.DEDENT, token.NL, token.ENDMARKER]:
                        return [n.lineno, n.lineno + tok.start[0] - 1]

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

        except_slice = self.get_except_slice(node)
        assert except_slice is not None

        unparsed_code = astunparse.unparse(node)

        for token_info in tokenize.generate_tokens(io.StringIO(unparsed_code).readline):
            if token_info.line != self.current_line:
                self.clear_line_buffer()
                self.current_line = token_info.line

            self.except_reached = token_info.start[0] >= except_slice[0]

            if token_info.start[0] >= except_slice[1]:
                return self.end_of_generation()

            if (token_info.type in [token.COMMENT, token.NEWLINE, token.NL]):
                continue

            if (token_info.type == token.ENDMARKER):
                return self.end_of_generation()

            if not self.handle_indentation(token_info):
                self.token_buffer.append(token_info.string)
