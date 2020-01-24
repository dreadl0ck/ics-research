#!/bin/bash

# extracts a subset of packets in the given time interval
# usage:
# $ extract-time-interval.sh <file> <startUnix> <endUnix>
# example:
# $ extract-time-interval.sh Dec2019_00010_20191206123000.pcap 1420197422 1420197890

filename=$(basename -- "$1")
file=${filename%.pcap}
editcap -A "$(date -r ${2} +'%Y-%m-%d %T')" -B "$(date -r ${3} +'%Y-%m-%d %T')" "${1}" "${file}_${2}-${3}.pcap"
