#!/bin/bash

# searches for packets matching the supplied bpf (default empty)
# in all pcap files in the current directory

for f in $(find . -name *.pcap); do
	echo "$f"
	tcpdump -r "$f" $@
done