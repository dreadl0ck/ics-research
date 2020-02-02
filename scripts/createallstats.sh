#!/bin/bash
files=$(find ../experiment-logs -name "*.log")
echo $files
for file in $files
do
	python3 ./create_stats.py $file
done
