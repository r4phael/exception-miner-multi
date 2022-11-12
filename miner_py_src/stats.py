from collections import Counter


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
                     f'#TryNum>=2        {self.try_num_lt_eq_2}\n'
                     f'#MaxTokens        {self.num_max_tokens}\n'
                     f'#AverageTokens    {self.tokens_count / self.functions_count if self.functions_count != 0 else 0}\n'
                     f'#MaxStatements    {self.num_max_statement}\n'
                     f'#AverageStatement {(self.statements_count / self.functions_count) if self.functions_count != 0 else 0}\n'
                     f'#UniqueTokens     {len(self.unique_tokens)}\n'
                     '-------- Top 10 Unique Tokens Ranking --------\n')

        unique_ranking_str = ''.join(
            [f"{key} - {value}" + "\n" for key, value in self.unique_tokens.most_common()[:10]])
        return stats_str + unique_ranking_str
