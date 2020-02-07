#!/bin/bash

files=""
if [[ "$1" != "" ]]; then
	echo "searching for logs in $1"
	files=$(find "$1" -name "*.log")
else
	echo "searching for logs in experiment-logs/"
	files=$(find experiment-logs -name "*.log")
fi

echo $files
for file in $files
do
	python3 scripts/create_stats.py $file
done
