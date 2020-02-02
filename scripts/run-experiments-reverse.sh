#!/bin/bash

chmod +x experiments/*.sh

files=(experiments/*.sh)
for (( i=${#files[@]}-1; i>=0; i-- ))
do
    rm -rf checkpoints/
    rm -rf models/
    
    path="${files[$i]}"
    filename=$(basename -- "$path")
	file=${filename%.sh}
    
    echo "running $path"
    "./$path" &> "experiment-logs/$file.log"
done
