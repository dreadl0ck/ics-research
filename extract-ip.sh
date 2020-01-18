
#!/bin/bash

for f in *.pcap
do
	mkdir -p ips
	filename=$(basename -- "$f")
	file=${filename%.pcap}
	tcpdump -r "$f" -w "ips/$file-ip-$1.pcap" host $1
done