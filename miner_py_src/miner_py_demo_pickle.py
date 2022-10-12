import time
import miner_py_utils as mpu
df = mpu.get_dataframe_from_pickle('../output/py/data/task1.pkl')
print('\n' * 2)
print('print task1')
print('\n' * 5)
time.sleep(1)
mpu.print_pair_task1(df[:10], delay=.09)
print('\n' * 2)
print('print task2')
print('\n' * 5)
time.sleep(1)
df = mpu.get_dataframe_from_pickle('../output/py/data/task2.pkl')
mpu.print_pair_task2(df[:10], delay=.09)
