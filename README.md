# README

## Dataset exploration

Filter traffic for modbus proto

	tcpdump -r packet_00173_20170622150408.pcap tcp port 502

Split into smaller pcap files:

	editcap -F pcap -i 120 packet_00173_20170622150408.pcap 2min.pcap

## Protocols

- MODBUS: TCP port 502
- EtherNet/IP makes use of TCP port number 44818 for explicit messaging and UDP port number 2222 for implicit messaging
- CIP is an application layer proto transported over etherip

## Tensorflow setup

### MacOS

Install tensorflow on macOS:

	brew install libtensorflow
	unset PYTHONPATH
	pip3 install requests pandas keras numpy matplotlib
	pip3 install tensorflow sklearn

### Linux

Install tensorflow on linux:

	apt install python3-pip
	pip3 install requests pandas keras numpy matplotlib
	pip3 install tensorflow sklearn

