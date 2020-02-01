#!/bin/bash

chmod +x experiments/*.sh

for f in experiments/*
do
    rm -rf checkpoints/
    rm -rf models/
    filename=$(basename -- "$f")
	file=${filename%.sh}
    echo "running $f"
    "./$f" &> "experiment-logs/$file.log"
done