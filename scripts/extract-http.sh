#!/bin/bash

for f in *.pcap
do
	mkdir -p http
	filename=$(basename -- "$f")
	file=${filename%.pcap}
	tcpdump -r "$f" -w "http/$file-http.pcap" tcp port 80
done