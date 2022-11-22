from collections import Counter
import ast
from miner_py_src.miner_py_utils import count_except, statement_couter, is_try_except_pass, is_generic_except


class FileStats:
    num_files = 0
    num_functions = 0
    files_try_except = set()
    files_try_pass = set()
    func_try_except = set()
    func_try_pass = set()
    func_generic_except = set()

    def metrics(self, f: ast.FunctionDef, file: str):
        for child in ast.walk(f):
            if isinstance(child, ast.Try):
                self.files_try_except.add(file)
            elif isinstance(child, ast.ExceptHandler):
                self.func_try_except.add(f"{file}:{f.name}")
                if is_try_except_pass(child):
                    self.func_try_pass.add(f"{file}:{f.name}")
                    self.files_try_pass.add(file)
                if is_generic_except(child):
                    print(f"{file}:{f.name}")
                    self.func_generic_except.add(f"{file}:{f.name}")

    def __str__(self) -> str:
        return (f"\n---------------- try-except STATS -----------------\n"
                f"# try-except found:                   {len(self.func_try_except)}\n"
                f"% try-except per file:                {(len(self.files_try_except) / self.num_files) * 100:.2f}%\n"
                f"% try-except per function definition: {(len(self.func_try_except) / max(self.num_functions, 1)) * 100:.2f}%\n"
                f"\n--------------- bad practice STATS ----------------\n"
                f"% try-pass per file:                  {(len(self.files_try_pass) / self.num_files) * 100:.2f}%\n"
                f"% try-pass per function definition:   {(len(self.func_try_pass) / max(self.num_functions, 1)) * 100:.2f}%\n"
                f"# try-pass:                           {len(self.func_try_pass)}\n"
                f"# generic exception handling:         {len(self.func_generic_except)}\n"
                )


class TBLDStats:
    functions_count = 0
    try_num_eq_1 = 0
    try_num_lt_eq_2 = 0
    tokens_count = 0
    num_max_tokens = 0
    statements_count = 0
    num_max_statement = 0
    unique_tokens = Counter()
    function_tokens_acc = 0

    def increment_try_stats(self, try_count):
        if try_count == 1:
            self.try_num_eq_1 += 1
        elif try_count >= 2:
            self.try_num_lt_eq_2 += 1

    def __str__(self) -> str:
        stats_str = ('-------- TBLD STATS --------\n'
                     f'#Python methods   {self.functions_count}\n'
                     f'#TryNum=1         {self.try_num_eq_1}\n'
                     f'#TryNum≥2         {self.try_num_lt_eq_2}\n'
                     f'#MaxTokens        {self.num_max_tokens}\n'
                     f'#AverageTokens    {self.tokens_count / self.functions_count if self.functions_count != 0 else 0:.2f}\n'
                     f'#MaxStatements    {self.num_max_statement}\n'
                     f'#AverageStatement {(self.statements_count / self.functions_count) if self.functions_count != 0 else 0:.2f}\n'
                     f'#UniqueTokens     {len(self.unique_tokens)}\n'
                     '-------- Top 10 Unique Tokens Ranking --------\n')

        unique_ranking_str = ''.join(
            [f"{key} - {value}" + "\n" for key, value in self.unique_tokens.most_common()[:10]])
        return stats_str + unique_ranking_str


class CBGDStats:
    functions_count = 0
    except_num_eq_1 = 0
    except_num_lt_eq_2 = 0
    tokens_count_source = 0
    tokens_count_target = 0
    num_max_tokens_source = 0
    num_max_tokens_target = 0
    statements_count = 0
    num_max_statement = 0
    unique_tokens = Counter()
    function_tokens_source_acc = 0
    function_tokens_target_acc = 0

    current_num_tokens = 0

    def reset(self):
        self.num_max_tokens_source = max(
            self.num_max_tokens_source, self.function_tokens_source_acc)
        self.tokens_count_source += self.function_tokens_source_acc
        self.function_tokens_source_acc = 0

        self.num_max_tokens_target = max(
            self.num_max_tokens_target, self.function_tokens_target_acc)
        self.tokens_count_target += self.function_tokens_target_acc
        self.function_tokens_target_acc = 0

    def increment_except_stats(self, function_def: ast.FunctionDef):
        except_count = count_except(function_def)
        if except_count == 1:
            self.except_num_eq_1 += 1
        elif except_count >= 2:
            self.except_num_lt_eq_2 += 1

    def increment_function_counter(self):
        self.functions_count += 1

    def increment_statements_counter(self, function_def: ast.FunctionDef):
        num_statements = statement_couter(function_def)
        self.statements_count += num_statements
        self.num_max_statement = max(self.num_max_statement, num_statements)

    def increment_current_num_tokens(self, num_tokens):
        self.current_num_tokens = num_tokens

    def move_current_num_tokens_source(self):
        self.function_tokens_source_acc += self.current_num_tokens
        self.current_num_tokens = 0

    def move_current_num_tokens_target(self):
        self.function_tokens_target_acc += self.current_num_tokens
        self.current_num_tokens = 0

    def __str__(self) -> str:
        stats_str = ('-------- CBGD STATS --------\n'
                     f'#Try-catch pairs         {self.functions_count}\n'
                     f'#ExceptNum=1             {self.except_num_eq_1}\n'
                     f'#ExceptNum≥2             {self.except_num_lt_eq_2}\n'
                     f'#MaxTokens of Source     {self.num_max_tokens_source}\n'
                     f'#AverageTokens of Source {self.tokens_count_source / self.functions_count if self.functions_count != 0 else 0:.2f}\n'
                     f'#MaxTokens of Target     {self.num_max_tokens_target}\n'
                     f'#AverageTokens of Target {self.tokens_count_target / self.functions_count if self.functions_count != 0 else 0:.2f}\n'
                     f'#UniqueTokens            {len(self.unique_tokens)}\n'
                     '-------- Top 10 Unique Tokens Ranking --------\n')

        unique_ranking_str = ''.join(
            [f"{key} - {value}" + "\n" for key, value in self.unique_tokens.most_common()[:10]])
        return stats_str + unique_ranking_str
