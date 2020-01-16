#!/bin/bash

tcpdump -r *.pcap -nn -q ip -l | \
    awk '{match($3,/[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+/); \
    ip = substr($3,RSTART,RLENGTH); \
    if (!seen[ip]++) print ip }'

