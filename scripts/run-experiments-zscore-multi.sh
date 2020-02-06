#!/bin/bash

chmod +x experiments/*.sh

for f in experiments/*
do
    rm -rf checkpoints/
    rm -rf models/
    filename=$(basename -- "$f")
	file=${filename%.sh}
    echo "running $f"
    "./$f" "data/SWaT2015-Attack-Files-v0.4-zscore/train/*-labeled.csv" "data/SWaT2015-Attack-Files-v0.4-zscore/eval/*-labeled.csv" &> "experiment-logs/multi-$file-zscore.log"
done