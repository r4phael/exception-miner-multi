import io
from typing import List, Any
import astunparse
import token
import tokenize
import pandas as pd
from .miner_py_utils import statement_couter, count_try
from .exceptions import TryNotFoundException, TreeSitterNodeException
import miner_py_src.miner_py_utils as mpu
from .stats import TBLDStats
from tqdm import tqdm
from tree_sitter.binding import Node

from numpy.random import default_rng

rng = default_rng()

INDENT_STR = f"<{token.tok_name[token.INDENT]}>"
DEDENT_STR = f"<{token.tok_name[token.DEDENT]}>"
NEWLINE_STR = f"<{token.tok_name[token.NEWLINE]}>"


class TryDatasetGenerator:

    def __init__(self, func_defs: List[Node], stats: TBLDStats) -> None:
        self.func_defs = func_defs
        self.stats = stats
        self.reset()

    def reset(self):
        self.indentation_counter = 0
        self.lines = []
        self.labels = []
        self.start_function_def = False
        self.try_reached = False

        self.current_lineno = None
        self.token_buffer = []

        self.stats.num_max_tokens = max(
            self.stats.num_max_tokens, self.stats.function_tokens_acc
        )
        self.stats.tokens_count += self.stats.function_tokens_acc
        self.stats.function_tokens_acc = 0

    def generate(self):
        generated = []

        pbar = tqdm(self.func_defs)
        for func_def in pbar:
            pbar.set_description(
                f"Function: {func_def.child_by_field_name('name').text[-40:].ljust(40)}")  # type: ignore
            try:
                tokenized_function_def = self.tokenize_function_def(func_def)

                if tokenized_function_def is not None:
                    self.stats.functions_count += 1
                    self.stats.increment_try_stats(count_try(func_def))
                    num_statements = statement_couter(func_def)
                    self.stats.statements_count += num_statements
                    self.stats.num_max_statement = max(
                        self.stats.num_max_statement, num_statements
                    )
                    generated.append(tokenized_function_def)
            except SyntaxError as e:
                print(
                    f"###### SyntaxError Error!!! in ast.FunctionDef {func_def}.\n{str(e)}")
                continue
            except tokenize.TokenError as e:
                print(
                    f"###### TokenError Error!!! in ast.FunctionDef {func_def}.\n{str(e)}")
                continue
            except ValueError as e:
                print(
                    f"###### ValueError Error!!! in ast.FunctionDef {func_def}.\n{str(e)}")
                continue
            except MemoryError as e:
                print(
                    f"###### MemoryError Error!!! in ast.FunctionDef {func_def}.\n{str(e)}")
                print(func_def.sexp())
                print(astunparse.unparse(func_def))
                continue

        return pd.DataFrame(generated)

    def clear_line_buffer(self):
        if len(self.token_buffer) == 0:
            return

        if self.try_reached:
            indentation = " ".join([INDENT_STR for _ in range(
                self.indentation_counter - 1)])
            self.stats.function_tokens_acc += self.indentation_counter - 1
        else:
            indentation = " ".join(
                [INDENT_STR for _ in range(self.indentation_counter)])
            self.stats.function_tokens_acc += self.indentation_counter

        if self.indentation_counter != 0:
            indentation += ' '

        tokenized_line = indentation + " ".join(self.token_buffer)

        self.stats.function_tokens_acc += len(self.token_buffer)
        self.stats.unique_tokens.update(self.token_buffer)

        self.token_buffer = []

        self.lines.append(tokenized_line)
        self.labels.append(1 if self.try_reached else 0)

    def end_of_generation(self):
        res = {
            "hasCatch": max(self.labels),
            "lines": self.lines,
            "labels": self.labels,
        }

        self.reset()

        return res

    def handle_indentation_and_newline(self, token_info: tokenize.TokenInfo):
        if token_info.type == token.STRING:
            self.token_buffer.append(token_info.string[0])
            self.token_buffer.append(
                "".join(token_info.string[1:-1].splitlines()).strip()
            )
            self.token_buffer.append(token_info.string[-1])
            return True
        return self.handle_indentation(token_info) or self.handle_new_line(token_info)

    def handle_new_line(self, token_info: tokenize.TokenInfo):
        if token_info.type == token.NEWLINE:
            self.token_buffer.append(NEWLINE_STR)
            return True
        return False

    def handle_indentation(self, token_info: tokenize.TokenInfo):
        if token_info.type == token.INDENT:
            self.indentation_counter += 1
            return True

        if token_info.type == token.DEDENT:
            self.indentation_counter -= 1
            assert self.indentation_counter >= 0
            return True
        return False

    def tokenize_function_def(self, node: Node):
        assert node is not None
        if not isinstance(node.text, bytes):
            raise TreeSitterNodeException("node.text is not bytes")

        try:
            try_slice = mpu.get_try_slices(node)
        except TryNotFoundException:
            try_slice = None

        for token_info in tokenize.generate_tokens(io.StringIO(node.text.decode('utf-8')).readline):
            if token_info.start[0] != self.current_lineno:
                self.clear_line_buffer()
                self.current_lineno = token_info.start[0]

            if try_slice is not None:
                self.try_reached = token_info.start[0] >= try_slice.try_block_start
                if token_info.start[0] == try_slice.try_block_start:  # ignore try
                    self.handle_indentation(token_info)
                    continue

                if len(try_slice.handlers) != 0 and token_info.start[0] >= try_slice.handlers[0][0]:
                    return self.end_of_generation()

            if token_info.type in [token.COMMENT, token.NL]:
                continue

            if token_info.type == token.ENDMARKER:
                return self.end_of_generation()

            if not self.handle_indentation_and_newline(token_info):
                self.token_buffer.append(token_info.string)
