#!/bin/bash

# tcpdump does not seem to like the pcaps without the correct file extension
# this script makes sure all files in the current dir have the .pcap extension

for f in *; do
	echo "$f"

	filename=$(basename -- "$f")
	if [[ "$filename" == "rename_pcaps.sh" ]]; then
		continue
	fi

	extension="${filename##*.}"
	filename="${filename%.*}"

#	echo $extension
	
	if [[ "$extension" != "pcap" ]]; then
		echo "mv $f $filename.pcap"
		mv "$f" "${filename}.pcap"
	fi

done