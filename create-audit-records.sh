#!/bin/bash

for f in *.pcap
do
	filename=$(basename -- "$f")
	file=${filename%.pcap}
	net.capture -r "$f" -out "/home/***REMOVED***/2019-SWaT-auditrecords/$file" -opts datagrams -payload false
done