#!/bin/bash

# searches for packets matching the supplied bpf (default empty)
# in all pcap files in the current directory

for f in *.{pcap,pcapng}; do
	tcpdump -r $f $@
done
