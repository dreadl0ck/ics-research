#!/bin/bash

for f in $(find . -name *.pcap); do
	echo "$f"
	tcpdump -r "$f" -w "$f-modbus.pcap" tcp port 502
done