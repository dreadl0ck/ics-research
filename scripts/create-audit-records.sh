#!/bin/bash

for f in *.pcap
do
	filename=$(basename -- "$f")
	file=${filename%.pcap}
	net.capture -r "$f" -out "/home/user/2019-SWaT-auditrecords/$file" -opts datagrams -payload false
done