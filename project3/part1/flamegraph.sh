#!/bin/bash

for exp in "sync" "libaio" "io_uring" "io_uring_poll"; do
    cmd="perf script -i ./data/$exp.data | ../../FlameGraph/stackcollapse-perf.pl | ../../FlameGraph/flamegraph.pl > ./svg/$exp.svg"
    echo $cmd
    eval $cmd
    printf "\n"
done
