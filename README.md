# README

## Server

The datasets are stored on a partition that needs to be mounted:

	mount /dev/sdb1 /datasets/

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

## Netcap

Find all netcap DNS log files, select the Questions field and print all unique values:

    find . -name DNS* -exec net.dump -select Questions -r "{}" \; | uniq
    
## Tensorflow build from source

Older CPUs do not support the AVX instruction that all recent TF releases are compiled to use.
This results in an 'Invalid instruction' error when using TF.
TF needs to be recompiled from source on the system.

Download bazel 0.29.1 installer and run it: https://github.com/bazelbuild/bazel/releases

Grab TF source and build: https://www.tensorflow.org/install/source

    pip install future
    apt-get install python-future
    bazel build //tensorflow/tools/pip_package:build_pip_package
    ./bazel-bin/tensorflow/tools/pip_package/build_pip_package /tmp/tensorflow_pkg
    pip install /tmp/tensorflow_pkg/tensorflow-version-tags.whl
    
## Label 2015 dataset

Build tool for linux:

	GOOS=linux go build -o bin/label-2015-dataset label-2015-dataset.go
	scp bin/label-2015-dataset ***REMOVED***@***REMOVED***:/home/***REMOVED***

On server: 
	
	sudo mv /home/***REMOVED***/label-2015-dataset /usr/local/bin
	cd /datasets/SWaT/01_SWaT_Dataset_Dec\ 2015/Network
	screen -L label-2015-dataset -attacks List_of_attacks_Final-fixed.csv -out /home/***REMOVED***/labeled-SWaT-2015-network

Compress data:

	screen -L zip -r /home/***REMOVED***/labeled-SWaT-2015-network.zip /home/***REMOVED***/labeled-SWaT-2015-network

## Label 2019 dataset

On server:

	screen -L net.label -custom SWaT2019-attacks.csv

## Tricks

Remove labeled CSV files inside the current directory to free up storage space:

	find . -iname *_labeled.csv -exec rm "{}" \;
