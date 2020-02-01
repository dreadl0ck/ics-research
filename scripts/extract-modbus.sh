#!/bin/bash

for f in *.pcap
do
	mkdir -p modbus
	filename=$(basename -- "$f")
	file=${filename%.pcap}
	tcpdump -r "$f" -w "modbus/$file-modbus.pcap" tcp port 502
done