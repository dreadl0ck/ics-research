#!/bin/bash

chmod +x experiments/*.sh

for f in experiments/*
do
    rm -rf checkpoints/
    rm -rf models/
    filename=$(basename -- "$f")
	file=${filename%.sh}
    echo "running $f"
    "./$f" "data/SWaT2015-Attack-Files-v0.4-zscore/train/2015-12-28_113021_98.log.part12_sorted-labeled.csv" "data/SWaT2015-Attack-Files-v0.4-zscore/train/2015-12-28_113021_98.log.part13_sorted-labeled.csv" &> "experiment-logs/single-$file-zscore.log"
done