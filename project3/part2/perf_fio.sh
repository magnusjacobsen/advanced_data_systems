#!/bin/bash

for exp in "sync" "libaio" "io_uring"; do
    for bs in "4K" "8K" "32K" "256K"; do
        cmd="perf stat -o ./stat/$exp-$bs.out fio --name=randread --ioengine=$exp --iodepth=1 --rw=randread --bs=$bs --direct=1 --size=1GB --runtime=60 --lat_percentiles=1 > ./fio/$exp-$bs.out"
        echo $cmd
        eval $cmd

        if [ "$exp" = "io_uring" ]; then
            engine="io_uring_polling"
            cmd2="perf stat -o ./stat/$engine-$bs.out fio --name=randread --ioengine=$exp --iodepth=1 --rw=randread --bs=$bs --direct=1 --size=1GB --runtime=60 --lat_percentiles=1 --sqthread_poll=1 > ./fio/$engine-$bs.out"
            echo $cmd2
            eval $cmd2
        fi 
    done
done
