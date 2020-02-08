#!/bin/bash

chmod +x experiments/*.sh

for f in experiments/*
do
    rm -rf checkpoints/
    rm -rf models/
    filename=$(basename -- "$f")
	file=${filename%.sh}
    echo "running $f"
    "./$f" "data/SWaT2015-Attack-Files-v0.4.3-minmax-text/train/*-labeled.csv" "data/SWaT2015-Attack-Files-v0.4.3-minmax-text/eval/*-labeled.csv" &> "experiment-logs/v0.4.3-multi-$file-minmax-text.log"
done