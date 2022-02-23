import matplotlib.pyplot as plt
import numpy as np
# workload a with zipfian

def read_tsv(filename):
    with open(filename) as f:
        return [line.strip().split('\t') for line in f.readlines()]

def prep_data(data):
    redis_ops, redis_read, redis_update = [], [], []
    rocks_ops, rocks_read, rocks_update = [], [], []
    for i in range(2, len(data)):
        if data[i][1] != '':
            redis_ops.append(float(data[i][1]))
            redis_read.append(float(data[i][2]))
            redis_update.append(float(data[i][3]))
        if data[i][4] != '':
            rocks_ops.append(float(data[i][4]))
            rocks_read.append(float(data[i][5]))
            rocks_update.append(float(data[i][6]))
    return redis_ops, redis_read, redis_update, rocks_ops, rocks_read, rocks_update

def plot_stuff(data, ax, read_data=True):
    redis_y = data[1] if read_data else data[2]
    rocks_y = data[4] if read_data else data[5]
    ylabel = 'Read latency (μs)' if read_data else 'Update latency (μs)'

    ax.plot(data[0], redis_y, label='Redis', marker='s')
    ax.plot(data[3], rocks_y, label='RocksDB', marker='o')
    ax.set_ylabel(ylabel)
    ax.set_xlabel('Throughput (ops/sec)')
    xticks = [i * 2000 for i in range(1,8)]
    yticks = [i * 10 for i in range(13)]

    ax.set_yticks(yticks)
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticks, rotation=45)
    ax.grid()

    ax.legend()


data = read_tsv('data/workloada_zipfian.tsv')
prepped_data = prep_data(data)

fig, axs = plt.subplots(1, 2, figsize=(8, 4))
#fig.suptitle('Workload A, regular Zipfian distribution')

plot_stuff(prepped_data, axs[0], read_data=True)
plot_stuff(prepped_data, axs[1], read_data=False)

#plt.xticks(rotation=90)
plt.tight_layout()
plt.show()
