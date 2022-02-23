from pathlib import Path
import os
import subprocess
from copy import deepcopy
import matplotlib.pyplot as plt
import numpy as np

paths = Path('.').glob('*.data')
os.makedirs('unfolded', exist_ok=True)
thisfolder = os.getcwd()

for p in paths:
    if os.path.isfile('./data/unfolded/' + p.name):
        continue
    print(f'processing {p.name}...')
    command = f'perf script -i ./data/{p.name} | ../FlameGraph/stackcollapse-perf.pl > ./data/unfolded/{p.name}'
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, error = process.communicate()

nthreads = [1,2,4,8,16]
types = [
    'WriteToWAL', 'InsertInto', 'AwaitState', 'PointLockManager', 'Misc RocksDB', 'Misc experiment']
keytypes = ['unique', 'same']
worktypes = ['txn', 'simple']

results = {
    worktype: {keytype: {threads: {t: 0 for t in types} for threads in nthreads} for keytype in keytypes} for worktype in worktypes}
relative_results = deepcopy(results)

for worktype in worktypes:
    for keytype in keytypes:
        for threads in nthreads:
            path = f'unfolded/{worktype}-{keytype}-{threads}-threads.data'
            with open(path, encoding='utf-8') as f:
                lines = f.readlines()
                lines = [line.strip() for line in lines]
                total = 0
                for line in lines:
                    count = int(line.split(';')[-1].split(' ')[-1])
                    total += count
                    for t in types:
                        if t in line:
                            results[worktype][keytype][threads][t] += count
                            break
                    else:
                        if 'rocksdb' in line:
                            results[worktype][keytype][threads]['Misc RocksDB'] += count
                        else:
                            results[worktype][keytype][threads]['Misc experiment'] += count

                #print(f'total: {total}')
                #for t, count in results[worktype][keytype][threads].items():
                #    print(f'{t}, count: {count}, relative: {(count / total) * 100:.2f}%')
            for t in types:
                relative_results[worktype][keytype][threads][t] = results[worktype][keytype][threads][t] / total

ncols = 4
fig, axs = plt.subplots(1, ncols, figsize=(9, 3))
#colors = ['#d73027', '#fc8d59', '#fee090', '#e0f3f8', '#91bfdb', '#4575b4']
colors = [
    "#FF1F5B",
	"#00CD6C",
	"#009ADE",
	"#AF58BA",
	"#FFC61E",
	"#F28522"
]
threads_str = [str(threads) for threads in nthreads]
pptypes = ['WAL write', 'Batch write to MemTable', 'AwaitState', 'PointLockManager', 'Other (RocksDB)', 'Other (Experiment)']
ppworktypes = ['Transaction', 'Simple put']
ppkeytypes = ['unique', 'all same']

lines = []

for col in range(ncols):
    ax = axs[col]
    if col == 0:
        ax.set_ylabel("Relative time")
    
    worktype = worktypes[(col // 2) % 2]
    keytype = keytypes[col % 2]
    datasets = [np.array([relative_results[worktype][keytype][threads][t] for threads in nthreads]) for t in types]

    bottom = None
    for i, dataset in enumerate(datasets):
        if i == 0:
            ax.bar(threads_str, dataset, label=pptypes[i],color=colors[i])
            bottom = dataset
        else:
            ax.bar(threads_str, dataset, label=pptypes[i], bottom=bottom, color=colors[i])
            bottom += dataset
    ax.set_xlabel("Threads")
    ax.title.set_text(f'{ppworktypes[(col // 2) % 2]} - {ppkeytypes[col % 2]}')

plt.subplots_adjust(top=0.8)
fig.legend(pptypes, ncol=3, loc="upper center")
plt.tight_layout(rect=[0,0,1,0.8])
plt.savefig('plot.pdf')
plt.show()
