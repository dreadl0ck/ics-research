#!/bin/bash

echo -e "CAPINFOS:\n" > capinfos.txt

echo "Files:" >> capinfos.txt
for f in *.pcap
do
	echo "- $f" >> capinfos.txt
done

echo "INFOS:" >> capinfos.txt
for f in *.pcap
do
	echo "generating capinfos for $f"
	capinfos "$f" >> capinfos.txt
	echo "" >> capinfos.txt
done
