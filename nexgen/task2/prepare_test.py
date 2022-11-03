from prepare import get_try_index, get_statements, slicing_mask
import re

code = 'def my_retry_op ( ) : <NEWLINE> <INDENT> try : <NEWLINE> <INDENT> <INDENT> result = flaky_operation ( ) <NEWLINE>'
# print(get_try_index(code))
# print(get_statements(code))

s = code.strip()
if not re.match(r'\w+', s):
    s = re.sub(r'^.*?(\w+)', r' \1', s)
s = re.sub(r'\\\\', ' ', s)
s = re.sub(r'\\ "', ' \\"', s)
try_idx = get_try_index(s)
if not try_idx:
    print('try not found: ', s)
    exit(-1)
s = s.split()
front = s[:try_idx]
back = s[try_idx:]
print('front')
print(front)
print('back')
print(back)
front, back, mask = slicing_mask(front, back)
