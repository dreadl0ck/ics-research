#!/bin/bash

for f in *.pcap
do
	tcpdump -r "$f" -nn -q ip -l | awk '{match($3,/[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+/); ip = substr($3,RSTART,RLENGTH); if (!seen[ip]++) print ip }'
done


