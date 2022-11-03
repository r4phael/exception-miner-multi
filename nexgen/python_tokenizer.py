import sys
from tokenize import generate_tokens
import pandas as pd
import io
import token as pytoken

string_code_task1 = '''def delete(self, session_key=None):
    if session_key is None:
        if self.session_key is None:
            return
        session_key = self.session_key
        os.unlink(self._key_to_file(session_key))'''

string_code_task2 = '''def delete(self, session_key=None):
    if session_key is None:
        if self.session_key is None:
            return
        session_key = self.session_key
    try:
        os.unlink(self._key_to_file(session_key))'''
string_catch_task2 = '''except OSError:
    pass'''


def create_task1():
    lines = []
    curr_line = None
    readline = io.StringIO(string_code_task1).readline

    line = ''
    for token in generate_tokens(readline):
        if curr_line is None: curr_line = token.line
        if token.line != curr_line:
            lines.append(line)
            line = ''
            curr_line = token.line
        
        if token.type in ['(INDENT)', '(DEDENT)']:
            line += ' ' + token.type
        else:
            line += ' ' + token.string

    df = pd.DataFrame([{'hasCatch': 1, 'id': 0, 'labels': [0,0,0,0,0,1], 'lines': lines}])
    df.to_pickle('task1/data/train.pkl')
    df.to_pickle('task1/data/test.pkl')
    df.to_pickle('task1/data/valid.pkl')

def create_task2():
    codeline = io.StringIO(string_code_task2).readline
    catchline = io.StringIO(string_catch_task2).readline

    line = ''
    for token in generate_tokens(codeline):        
        if token.type in [pytoken.INDENT, pytoken.DEDENT, pytoken.NEWLINE]:
            line += ' ' + pytoken.tok_name[token.type]
        else:
            line += ' ' + token.string

    line = line.strip()

    with open('task2/data/baseline/src-test.txt', 'w') as f:
        f.write(line)
    with open('task2/data/baseline/src-train.txt', 'w') as f:
        f.write(line)
    with open('task2/data/baseline/src-valid.txt', 'w') as f:
        f.write(line)

    line = ''
    for token in generate_tokens(catchline):
        if token.type in [pytoken.INDENT, pytoken.DEDENT, pytoken.NEWLINE]:
            line += ' ' + pytoken.tok_name[token.type]
        else:
            line += ' ' + token.string

    line = line.strip()

    with open('task2/data/baseline/tgt-test.txt', 'w') as f:
        f.write(line)
    with open('task2/data/baseline/tgt-train.txt', 'w') as f:
        f.write(line)
    with open('task2/data/baseline/tgt-valid.txt', 'w') as f:
        f.write(line)

if __name__ == '__main__':
    mode = sys.argv[1]
    assert mode in {'task1', 'task2'}

    if mode == 'task1':
        create_task1()
    if mode == 'task2':
        create_task2()