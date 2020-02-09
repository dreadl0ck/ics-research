#!/bin/bash

chmod +x experiments/*.sh

# TODO: generate better output file names, and includ version number of python script automatically
for f in experiments/*
do
    rm -rf checkpoints/
    rm -rf models/
    filename=$(basename -- "$f")
	file=${filename%.sh}
    echo "running $f"
    "./$f" "data/SWaT2015-Attack-Files-v0.4.3-minmax-text/train/2015-12-28_113021_98.log.part12_sorted-labeled.csv" "data/SWaT2015-Attack-Files-v0.4.3-minmax-text/train/2015-12-28_113021_98.log.part13_sorted-labeled.csv" &> "experiment-logs/v0.4.5-binary-single-$file-minmax-text.log"
done