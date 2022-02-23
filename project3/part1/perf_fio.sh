#!/bin/bash

for exp in "sync" "libaio" "io_uring"; do
    cmd="perf record -F 99 -ag fio --name=randread --ioengine=$exp --iodepth=1 --rw=randread --bs=4k --direct=1 --size=1GB --runtime=60"
    echo $cmd
    eval $cmd
    eval "mv perf.data data/$exp.data"

    if [ "$exp" = "io_uring" ]; then
        poll=" --sqthread_poll=1"
        echo $cmd$poll
        eval $cmd$poll
        eval "mv perf.data data/io_uring_poll.data"
    fi
done
