import matplotlib.pyplot as plt
import math
from random import random, gauss
import numpy as np

num_samples = 100000
rang = 20000

samples = list(map(int, open('data/unscrambled_zipfian_dist.txt').readlines()))

bins = np.arange(0, rang + 1.5) - 0.5

sample_count = [0] * rang
for s in samples:
    sample_count[s] += 1

sample_prob = [0 if sc == 0 else sc/num_samples for sc in sample_count]

print(max(sample_prob))

#exit(0)
plt.hist(samples, bins=bins, density=True)
plt.ylabel("Sample probability")

plt.xlabel("Index value")
plt.show()

