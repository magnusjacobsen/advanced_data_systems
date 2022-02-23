import re
import matplotlib.pyplot as plt
import numpy as np

############################
#  Helper... becuz fio...  #
############################
def to_f(s):
    s = s.replace(',', '')
    if s.lower()[-1] == 'k':
        return float(s[:-1]) * 1000
    return float(s)

#########################
#      Collect data     #
#########################
engines = ['sync', 'libaio', 'io_uring', 'io_uring_polling']
blocksizes = [4, 8, 32, 256]
blocksizes = [str(b) for b in blocksizes]
data = {engine: {blocksize: {} for blocksize in blocksizes} for engine in engines}
pp_titles = {'latavg': 'Latency (avg)', 'lat99': 'Latency (99%)', 'throughput': 'Throughput', 'iops': 'IOPS', 'switches': 'Context switches', 'migrations': 'CPU migrations', 'faults': 'Page faults'}

for engine in engines:
    for bs in blocksizes:
        with open(f'fio/{engine}-{bs}K.out', encoding='utf-8') as f:
            lines = [re.sub(' +', ' ', line.strip()) for line in f.readlines()]   
            for line in lines:
                # avg latency
                if line.startswith('lat (usec): '):
                    data[engine][bs]['latavg'] = to_f(line.split(' ')[4].split('=')[1])
                # 99 percentile
                if line.startswith('| 99.0'):
                    data[engine][bs]['lat99'] = to_f(line.split(' ')[2].split(']')[0])
                # iops and throughput
                if line.startswith('read:'):
                    data[engine][bs]['iops'] = to_f(line.split(' ')[1].split('=')[1])
                    data[engine][bs]['throughput'] = to_f(line.split(' ')[3].split(')')[0].replace('(', '').split('M')[0])
        total_ops = data[engine][bs]['iops'] * 60
        with open(f'stat/{engine}-{bs}K.out', encoding='utf-8') as f:
            lines = [re.sub(' +', ' ', line.strip()) for line in f.readlines()]
            # context switces
            data[engine][bs]['switches'] = float(lines[6].split(' ')[0].replace(',', '')) / total_ops
            # cpu migrations
            data[engine][bs]['migrations'] = float(lines[7].split(' ')[0].replace(',', '')) / total_ops
            # page-faults
            data[engine][bs]['faults'] = float(lines[8].split(' ')[0].replace(',', '')) / total_ops

colors = ["#FF1F5B", "#00CD6C", "#009ADE", "#AF58BA", "#FFC61E", "#F28522"]
fio_keys = ['latavg', 'lat99', 'iops', 'throughput']
fio_units = ['μs', 'μs', 'IO operations/s', 'MB/s']
perf_keys = ['switches', 'migrations', 'faults']
perf_units = ['per operation']*3
markers = ['+', 'x', '.', '*']
bar_adjustments = np.array([-0.3, -0.1, 0.1, 0.3])
placements = np.array([1,2,3,4])

def plot_ax(ax, data, key, yunit):
    for i, engine in enumerate(engines):
        ys = [data[engine][bs][key] for bs in blocksizes]
        ax.bar(placements + bar_adjustments[i], ys, 0.2, label=engine, color=colors[i])
    ax.title.set_text(pp_titles[key])
    ax.set_xticks(placements)
    ax.set_ylabel(yunit)
    ax.set_xlabel('Blocksize (KB)')
    ax.set_ylim(ymin=0)
    ax.set_xticklabels(blocksizes)#[f'{bs}KB' for bs in blocksizes])
    
#####################
#    FIO RESULTS    #
#####################
fig, axs = plt.subplots(1, 4, figsize=(10, 3))
[plot_ax(ax, data, key, yunit) for yunit, (ax, key) in zip(fio_units, zip(axs, fio_keys))]

plt.subplots_adjust(top=0.9)
fig.legend(engines, ncol=4, loc="upper center")
plt.tight_layout(rect=[0,0,1,0.9])
plt.show()
'''
######################
#     PERF RESULTS   #
######################
fig, axs = plt.subplots(1, 3, figsize=(7.5, 3))
[plot_ax(ax, data, key, yunit) for yunit, (ax, key) in zip(perf_units, zip(axs, perf_keys))]

plt.subplots_adjust(top=0.9)
fig.legend(engines, ncol=4, loc="upper center")
plt.tight_layout(rect=[0,0,1,0.9])
plt.show()
'''
