#!/bin/bash

chmod +x experiments/*.sh

files=(experiments/*)
for ((i=${#files[@]}-1; i>=0; i--)); do
    rm -rf checkpoints/
    rm -rf models/
    path="${files[$i]}"
    filename=$(basename -- "$path")
	file=${filename%.sh}
    echo "running $f"
    "./$f" &> "experiment-logs/$file.log"
done
