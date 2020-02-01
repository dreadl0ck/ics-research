#!/bin/bash

for f in *.csv
do
	filename=$(basename -- "$f")
	file=${filename%.pcap}
	python3 tf-dnn.py -read "$f" &> $file.log
done