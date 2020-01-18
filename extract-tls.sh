
#!/bin/bash

for f in *.pcap
do
	mkdir -p tls
	filename=$(basename -- "$f")
	file=${filename%.pcap}
	tcpdump -r "$f" -w "tls/$file-tls.pcap" tcp port 443
done