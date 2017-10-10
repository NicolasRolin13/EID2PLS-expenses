from collections import defaultdict
import time


tic = time.time()

random_dict = defaultdict(lambda: None)

for integer in range(1000):
    random_dict[integer**2] = integer
print('sqare root of 5 is {}'.format(random_dict[5]))

print('that was hella slow, it took {time} second'.format(time=time.time() - tic))




