#!/bin/bash

for f in *.pcap
do
	echo "scanning $f with suricata"
	mkdir -p "$f-logs"
	suricata -r "$f" -l "$f-logs"
done
