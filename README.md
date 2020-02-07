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

Download:

	scp ***REMOVED***@***REMOVED***:/home/***REMOVED***/labeled-SWaT-2015-network.zip .

## Label 2015 dataset attack files

Generate colsums:

    datenwolf -attacks data/List_of_attacks_Final-fixed.csv -file-filter data/Network/attack-files.txt -out data/SWaT2015-Attack-Files-v0.4

Use colSums to label:

    $ mkdir data/SWaT2015-Attack-Files-v0.4
    $ go run ./datenwolf -attacks data/List_of_attacks_Final-fixed.csv -file-filter data/Network/attack-files.txt -out data/SWaT2015-Attack-Files-v0.4 -in data/Network -colsums colSums-5Feb2020-194133.json

## Label 2019 dataset

On server, test by moving into a directory that contains audit records:

	screen -L net.label -custom ../SWaT2019-attacks.csv

To process all files, use the script:

	screen -L label-audit-records.sh

## Tricks

Remove labeled CSV files inside the current directory to free up storage space:

	find . -iname *_labeled.csv -exec rm "{}" \;

## Eval Datasets

### 2015

Connect brussels
        
    sudo su
    cd /home/***REMOVED***/labeled-SWaT-2015-network
    screen -L ../ics-research/readcsv.py -read "*-labeled.csv" -dimensionality 19 -lstm true -lstmBatchSize 250000

Dimension Problems:
    
    df.columns Index(['num', 'date', 'time', 'orig', 'type', 'i/f_name', 'i/f_dir', 'src',
           'dst', 'proto', 'appi_name', 'proxy_src_ip', 'Modbus_Function_Code',
           'Modbus_Function_Description', 'Modbus_Transaction_ID', 'SCADA_Tag',
           'Modbus_Value', 'service', 's_port', 'Tag', 'Normal/Attack'],
          dtype='object') 21
      
    df.columns Index(['num', 'date', 'time', 'orig', 'type', 'i/f_name', 'i/f_dir', 'src',
         'dst', 'proto', 'appi_name', 'proxy_src_ip',
         'Modbus_Function_Description', 'Modbus_Transaction_ID', 'SCADA_Tag',
         'Modbus_Value', 's_port', 'Normal/Attack'],
        dtype='object') 18
    
> Modbus_F_Code, service, Tag

Start experiments on Brussels:

    ***REMOVED***@brussels:/home/***REMOVED***/labeled-SWaT-2015-network# ../ics-research/readcsv.py -read "*-labeled.csv" -dimensionality 19 -lstm true -lstmBatchSize 10000 -epochs 3
    
> commit version: 8fd1f38e275303bca1ae861a21b91720e4856bd2

## commands ran
### for normal dnn on 2015 labeled dataset:

run 1: 27/1
command:
   python3 readcsv.py -read "/mnt/terradrive/labeled-SW015-network/*.csv" -dimensionality 19 -epochs 10

commit version:
    
    ***REMOVED***@***REMOVED***:~/ics-research$ git rev-parse HEAD  
    4f5ed93d439ca30cf82654f77f0186447327b9e0


run 2: 28/1

command:
   python3 readcsv.py -read "/mnt/terradrive/labeled-SW015-network/*.csv" -dimensionality 19 -epochs 10

commit version:
   ***REMOVED***@***REMOVED***:~/ics-research$ git rev-parse HEAD
f54739686d56ae45d7d0eeb9c2bbfaa3fcb7d10a


run 3: 28/1 14:55
command:
screen -L python3 readcsv.py -read "/mnt/terradrive/labeled-SWaT-2015-network/2015-12-26_121116_89.log.part03_sorted-labeled.csv" -dimensionality 14 -epochs 10 -debug true -drop service,Modbus_Function_Code

commit version:
***REMOVED***@***REMOVED***:~/ics-research$ git rev-parse HEAD
20fd6a5fb6239627eb4e7d791496368861e0e3f0

run 4: 28/1 16:16
command:
screen -L python3 -u readcsv.py -read "/mnt/terradrive/labeled-SWaT-2015-network/*csv" -dimensionality 14 -epochs 10 -debug true -drop service,Modbus_Function_Cod

commit version:
***REMOVED***@***REMOVED***:/home/***REMOVED***/ics-research# git rev-parse HEAD
20fd6a5fb6239627eb4e7d791496368861e0e3f0


run 5: 28/1 23:55
command
(reverse-i-search)`-L': screen -L python3 -u readcsv.py -read "/mnt/terradrive/labeled-SWaT-2015-network/*csv" -dimensionality 15 -epochs 10 -debug true -drop service,Modbus_Function_Cod


commit version:
***REMOVED***@***REMOVED***:/home/***REMOVED***/ics-research# git rev-parse HEAD
322ee5783702a582b86dd7dd015ccb84be3d54e2


run 6: 29-1 16:40 - prepared, but not ran
screen -L python3 -u readcsv.py -read "/mnt/terradrive/labeled-SWaT-2015-network/*csv" -dimensionality 15 -epochs 10 -debug true -drop service,Modbus_Function_Code

## Dataset analyzer

### analysis
- which files contain attacks
- unique strings for each row
- mean, stddev, min and max for numbers

### preprocessing

- drop columns that only contain a single value
- fix typos: ip, log and loe, Responqe etc
- merge num, date and time to UNIX timestamps

### encoding

- zscore numbers
- encode strings to numbers

### labeling

- use attack types

### split

- dataset split: 50% train, 25% test, 25% validation, LSTM batch size: 125000

- IMPORTANT: preserve order when using LSTM
- add code to run evaluation and print results

- DROP columns: Tag, date, num and time

### TODO

- add progress indicator
- fix checkpoint naming for lstm: 'files' wrong

Generate colsums:

    go run ../../datenwolf -analyze
    # output: colSums-29Jan2020-170358.json

Build:

    GOOS=linux go build -o bin/datenwolf ./datenwolf
	scp bin/datenwolf ***REMOVED***@***REMOVED***:/home/***REMOVED***

Start analysis and labeling on oslo:

    cd "/datasets/SWaT/01_SWaT_Dataset_Dec 2015/Network"

Local:

    cd Network
    go run ../../datenwolf -attacks List_of_attacks_Final-fixed.csv -file-filter attack-files.txt -suffix "_sorted.csv" -colsums colSums-29Jan2020-221001.json -workers 25

Oslo:

    screen -L /home/***REMOVED***/datenwolf -attacks List_of_attacks_Final-fixed.csv -suffix "_sorted.csv" -out /home/***REMOVED***/labeled-SWaT-2015-network -colsums /home/***REMOVED***/colSums-29Jan2020-221001.json -workers 25

Brussels:

    screen -L /home/***REMOVED***/datenwolf -attacks List_of_attacks_Final-fixed.csv -suffix "_sorted.csv" -colsums /home/***REMOVED***/colSums-29Jan2020-221001.json -workers 25 -offset 392

# Push dataset to all servers

    scp -r -P 9876 data/Network ***REMOVED***@***REMOVED***:/home/***REMOVED***
    scp -r -P 9876 data/Network ***REMOVED***@***REMOVED***:/home/***REMOVED***
    scp -r data/Network ***REMOVED***@***REMOVED***:/home/***REMOVED***

Push labeling tool:

    GOOS=linux go build -o bin/datenwolf ./datenwolf
    scp -P 9876 bin/datenwolf ***REMOVED***@***REMOVED***:/home/***REMOVED***
    scp -P 9876 bin/datenwolf ***REMOVED***@***REMOVED***:/home/***REMOVED***
    scp bin/datenwolf ***REMOVED***@***REMOVED***:/home/***REMOVED***

Start:

    cd Network

Brussels (1/4 Train)

    ../datenwolf -attacks List_of_attacks_Final-fixed.csv -suffix _sorted.csv -colsums colSums-29Jan2020-221001.json -workers 25 -offset 0 -max 196 -out SWaT2015-Network-Labeled-Pt1

Oslo (2/4 Train)

    ../datenwolf -attacks List_of_attacks_Final-fixed.csv -suffix _sorted.csv -colsums colSums-29Jan2020-221001.json -workers 25 -offset 196 -max 392 -out SWaT2015-Network-Labeled-Pt2

Mac (3/4 Test)

    go run ../../datenwolf -attacks List_of_attacks_Final-fixed.csv -suffix _sorted.csv -colsums colSums-29Jan2020-221001.json -workers 25 -offset 392 -max 588 -out SWaT2015-Network-Labeled-Pt3

    screen -L /home/***REMOVED***/datenwolf -attacks /home/***REMOVED***/Network/List_of_attacks_Final-fixed.csv -suffix _sorted.csv -colsums /home/***REMOVED***/Network/colSums-29Jan2020-221001.json -workers 25 -offset 392 -max 588 -out /home/***REMOVED***/Network/SWaT2015-Network-Labeled

Bastia (4/4 Eval)

    ../datenwolf -attacks List_of_attacks_Final-fixed.csv -suffix _sorted.csv -colsums colSums-29Jan2020-221001.json -workers 25 -offset 588 -out SWaT2015-Network-Labeled-Pt4

    screen -L /home/***REMOVED***/datenwolf -attacks /home/***REMOVED***/Network/List_of_attacks_Final-fixed.csv -suffix _sorted.csv -colsums /home/***REMOVED***/Network/colSums-29Jan2020-221001.json -workers 25 -offset 392 -max 588 -out /home/***REMOVED***/Network/SWaT2015-Network-Labeled

## LSTM Evaluation

    cd data/SwaT2015-Attack-Files-v0.2

Train

    python3 ../../train.py -read "*-labeled.csv" -dimensionality 16 -lstm true -optimizer sgd -drop modbus_value

    python3 ../../readcsv.py -read "*-labeled.csv" -dimensionality 17 -lstm true -optimizer sgd

Score

    python3 ../../score_dataset.py -read "*-labeled.csv" -dimensionality 17 -optimizer sgd -model checkpoints/lstm-epoch-1-files-0-2-batch-500000-510000 -drop modbus_value -lstm true -debug true

    python3 ../../score_dataset.py -read "*-labeled.csv" -dimensionality 17 -optimizer sgd -model checkpoints/lstm-epoch-1-files-0-2-batch-500000-510000 -lstm true -debug true

    2015-12-28_113021_98.log.part12_sorted-labeled.csv : 103513 [Single Stage Single Point]
    2015-12-28_113021_98.log.part13_sorted-labeled.csv : 136049 [Single Stage Single Point]

    python3 ../../train.py -read "2015-12-28_113021_98.log.part12_sorted-labeled.csv" -dimensionality 16 -lstm true -optimizer sgd -drop modbus_value
    python3 ../../score.py -read "2015-12-28_113021_98.log.part13_sorted-labeled.csv" -dimensionality 16 -optimizer sgd -model checkpoints/lstm-epoch-1-files-0-2-batch-490000-500000 -drop modbus_value -lstm true -debug true

## Physical Data Evaluation

Normal DNN

    cd data
    python3 ../train.py -read "SWaT_Dataset_Attack_v0-fixed-train-test.csv" -dimensionality 52 -optimizer sgd -result_column Normal/Attack

    python3 ../score.py -read "SWaT_Dataset_Attack_v0-fixed-eval.csv" -dimensionality 52 -optimizer sgd -model checkpoints/dnn-epoch-1-files-0-1 -debug true -result_column Normal/Attack

LSTM

With test_size = 0.25 set lstmBatchSize to (numRows) * 0.25

    cd data
    python3 ../train.py -read "SWaT_Dataset_Attack_v0-fixed-train-test.csv" -dimensionality 52 -optimizer sgd -result_column Normal/Attack -lstm true -lstmBatchSize 87484

    python3 ../score.py -read "SWaT_Dataset_Attack_v0-fixed-eval.csv" -dimensionality 52 -optimizer sgd -model checkpoints/lstm-epoch-1-files-0-1-batch-262452-349936 -debug true -result_column Normal/Attack -lstm true -lstmBatchSize 87484

TODO

- normalize values for strings and rerun experiments
- zscore timestamps
- amount of neurons / layers?
- vary lstm batch size
- sgd / non-sgd
- lstm / normal

- layer configuration !! single layers VS multiple
- save and load entire model configuration:

> Call model.save to save the a model's architecture, weights, and training configuration in a single file/folder. This allows you to export a model so it can be used without access to the original Python code*. Since the optimizer-state is recovered, you can resume training from exactly where you left off.

## TODO

- fix eval of physical data
- read multiple files and increase amount of samples passed to tensorflow
- try smaller batchSizes
- make leakyrelu alpha configurable and try different settings
- make dropout rate configurable and try different settings
- test with and without final Dense(1) layer
- try leaky relu alpha of 0.2

- SYNC new 0.4 version with servers
- generate zscore versoin encoded data
- update experiments: add runs with multi class VS binary classes and zscore VS minmax
- bootstrap baseline experiments, run with increasing num of epochs, then replicate and update paths for zscore/minmax, replicate again and add flags for multi vs single class
- define vXX experiment types in a document, and adjust experiments scripts
    - <dnnType>-<classType>-<encodingType>-<experimentType>.sh
    - dnn-binary-minmax-vXX.sh
    - dnn-multi-zscore-vXX.sh
- add flags to switch activation func to tfUtils


- use smaller batch for training? with equal distribution of attack types?
- input_shape=(int(lstmBatchSize/10000),input_dim,) => adjust hspae, set to 128?
- one hot encoding