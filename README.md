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
- one hot encoding

DNN

python3 train.py \
    -read data/SWaT2015-Attack-Files-v0.4.3-minmax-text/train/*2015-12-28_113021_98.log.part12_sorted*-labeled.csv \
    -wrapLayerSize 8 \
    -dropoutLayer false \
    -relu true \
    -coreLayerSize 16 \
    -numCoreLayers 2 \
    -optimizer adam \
    -epoch 10 \
    -features 81 \
    -drop modbus_value

python3 score.py \
    -read data/SWaT2015-Attack-Files-v0.4.3-minmax-text/train/2015-12-28_113021_98.log.part13_sorted-labeled.csv \
    -wrapLayerSize 8 \
    -dropoutLayer false \
    -relu true \
    -coreLayerSize 16 \
    -numCoreLayers 2 \
    -optimizer adam \
    -features 81 \
    -drop modbus_value

LSTM

python3 train.py \
    -read "data/SWaT2015-Attack-Files-v0.4.3-minmax-text/train/*-labeled.csv" \
    -wrapLayerSize 16 \
    -dropoutLayer true \
    -relu true \
    -coreLayerSize 32 \
    -numCoreLayers 2 \
    -optimizer adam \
    -epoch 3 \
    -lstm true \
    -features 107 \
    -binaryClasses true \
    -drop modbus_value

python3 score.py \
    -read "data/SWaT2015-Attack-Files-v0.4.3-minmax-text/eval/*-labeled.csv" \
    -wrapLayerSize 16 \
    -dropoutLayer true \
    -relu true \
    -coreLayerSize 32 \
    -numCoreLayers 2 \
    -optimizer adam \
    -lstm true \
    -features 107 \
    -binaryClasses true \
    -drop modbus_value

## eval

    $ grep attack logs/allstats-v0.4.3-binary.log | grep -v "set classes" | grep -v "zero"
    attack                             0.579    1.000      0.733
    attack                             0.579    1.000      0.733

    $ grep Single logs/allstats-v0.4.3-multi-class.log | grep -v "zero"
    Single Stage Single Point          0.579    1.000      0.733
    Single Stage Single Point          0.111    0.009      0.016
    Single Stage Single Point          0.060    0.583      0.108
    Multi Stage Single Point           0.013    0.441      0.025
    Single Stage Single Point          0.054    0.453      0.096
    Single Stage Multi Point           0.004    0.071      0.007
    Single Stage Single Point          0.047    0.355      0.083
    Single Stage Single Point          0.079    0.404      0.132
    Single Stage Single Point          0.080    1.000      0.148
    Single Stage Single Point          0.122    0.003      0.005
    Single Stage Single Point          0.092    0.191      0.124
    Single Stage Single Point          0.077    0.000      0.000
    Single Stage Single Point          0.036    0.267      0.063
    Single Stage Single Point          0.578    0.995      0.731
    Single Stage Single Point          0.080    1.000      0.148
    Single Stage Single Point          0.579    1.000      0.733

latest:

    $ grep Single logs/allstats.log | grep -v "zero"
    Single Stage Multi Point           0.003    0.033      0.005
    Single Stage Single Point          0.029    0.081      0.043
    Single Stage Single Point          0.053    0.415      0.094
    Single Stage Single Point          0.579    1.000      0.733
    Single Stage Single Point          0.080    1.000      0.148
    Single Stage Single Point          0.050    0.027      0.035
    Single Stage Single Point          0.111    0.009      0.016
    Single Stage Single Point          0.060    0.583      0.108
    Multi Stage Single Point           0.013    0.441      0.025
    Single Stage Single Point          0.579    1.000      0.733
    Single Stage Single Point          0.054    0.453      0.096
    Single Stage Multi Point           0.004    0.071      0.007
    Single Stage Single Point          0.047    0.355      0.083
    Single Stage Single Point          0.079    0.404      0.132
    Single Stage Single Point          0.080    1.000      0.148
    Single Stage Single Point          0.122    0.003      0.005
    Single Stage Single Point          0.092    0.191      0.124
    Single Stage Single Point          0.077    0.000      0.000
    Single Stage Single Point          0.036    0.267      0.063
    Single Stage Single Point          0.578    0.995      0.731
    Single Stage Single Point          0.080    1.000      0.148
    Multi Stage Single Point           0.006    1.000      0.011
    Single Stage Single Point          0.579    1.000      0.733
    Single Stage Single Point          0.143    0.334      0.200
    Single Stage Single Point          0.130    0.136      0.133
    Single Stage Single Point          0.087    0.646      0.153

=> 0.7 f1 score for ?-file multi class: dnn-v6
=> 0.7 f1 score for single-file zscore binary: dnn-v4, v6

=> 0.1 f1 score for multi class: lstm-v9

dnn v4:

    -wrapLayerSize 8 \
    -dropoutLayer true \
    -relu false \
    -coreLayerSize 32 \
    -numCoreLayers 1 \
    -optimizer adam \
    -epoch 3 \
    -drop modbus_value

dnn v6:

    -wrapLayerSize 16 \
    -dropoutLayer false \
    -relu true \
    -coreLayerSize 64 \
    -numCoreLayers 1 \
    -optimizer adam \
    -epoch 3 \
    -drop modbus_value

lstm v9:

    -wrapLayerSize 8 \
    -dropoutLayer true \
    -relu true \
    -coreLayerSize 32 \
    -numCoreLayers 3 \
    -optimizer sgd \
    -epoch 10 \
    -drop modbus_value

## report

system stats

    lshw -C system,memory,processor -short
    uname -a
    python3 -c 'import tensorflow as tf; print(tf.__version__)' 

Brussels:

    # lshw -C system,memory,processor -short
    H/W path            Device     Class          Description
    =========================================================
                                system         PowerEdge R240 (SKU=NotProvided;ModelName=PowerEdge R240)
    /0/0                           memory         64KiB BIOS
    /0/400                         processor      Intel(R) Xeon(R) E-2124 CPU @ 3.30GHz
    /0/400/700                     memory         256KiB L1 cache
    /0/400/701                     memory         1MiB L2 cache
    /0/400/702                     memory         8MiB L3 cache
    /0/1000                        memory         16GiB System Memory
    /0/1000/0                      memory         8GiB DIMM DDR4 Synchronous Unbuffered (Unregistered) 2666 MHz (0.4 ns)
    /0/1000/1                      memory         8GiB DIMM DDR4 Synchronous Unbuffered (Unregistered) 2666 MHz (0.4 ns)
    /0/1000/2                      memory         [empty]
    /0/1000/3                      memory         [empty]
    /0/100/14.2                    memory         RAM memory
    ***REMOVED***@brussels:/home/***REMOVED***# uname -a
    Linux brussels 4.15.0-74-generic #84-Ubuntu SMP Thu Dec 19 08:06:28 UTC 2019 x86_64 x86_64 x86_64 GNU/Linux
    ***REMOVED***@brussels:/home/***REMOVED***# python3 -c 'import tensorflow as tf; print(tf.__version__)'
    2020-02-09 21:57:08.780537: W tensorflow/stream_executor/platform/default/dso_loader.cc:55] Could not load dynamic library 'libnvinfer.so.6'; dlerror: libnvinfer.so.6: cannot open shared object file: No such file or directory
    2020-02-09 21:57:08.780594: W tensorflow/stream_executor/platform/default/dso_loader.cc:55] Could not load dynamic library 'libnvinfer_plugin.so.6'; dlerror: libnvinfer_plugin.so.6: cannot open shared object file: No such file or directory
    2020-02-09 21:57:08.780615: W tensorflow/compiler/tf2tensorrt/utils/py_utils.cc:30] Cannot dlopen some TensorRT libraries. If you would like to use Nvidia GPU with TensorRT, please make sure the missing libraries mentioned above are installed properly.
    2.1.0

Bastia:

    # lshw -C system,memory,processor -short
    H/W path             Device     Class          Description
    ==========================================================
                                    system         PowerEdge R230 (SKU=NotProvided;ModelName=PowerEdge R230)
    /0/0                            memory         64KiB BIOS
    /0/400                          processor      Intel(R) Xeon(R) CPU E3-1240L v5 @ 2.10GHz
    /0/400/700                      memory         256KiB L1 cache
    /0/400/701                      memory         1MiB L2 cache
    /0/400/702                      memory         8MiB L3 cache
    /0/1000                         memory         16GiB System Memory
    /0/1000/0                       memory         [empty]
    /0/1000/1                       memory         8GiB DIMM DDR4 Synchronous 2133 MHz (0.5 ns)
    /0/1000/2                       memory         [empty]
    /0/1000/3                       memory         8GiB DIMM DDR4 Synchronous 2133 MHz (0.5 ns)
    /0/100/1f.2                     memory         Memory controller
    ***REMOVED***@***REMOVED***:/home/***REMOVED***# uname -a
    Linux ***REMOVED*** 4.15.0-66-generic #75-Ubuntu SMP Tue Oct 1 05:24:09 UTC 2019 x86_64 x86_64 x86_64 GNU/Linux
    ***REMOVED***@***REMOVED***:/home/***REMOVED***#     python3 -c 'import tensorflow as tf; print(tf.__version__)'
    2020-02-09 21:58:02.454559: W tensorflow/stream_executor/platform/default/dso_loader.cc:55] Could not load dynamic library 'libnvinfer.so.6'; dlerror: libnvinfer.so.6: cannot open shared object file: No such file or directory
    2020-02-09 21:58:02.454784: W tensorflow/stream_executor/platform/default/dso_loader.cc:55] Could not load dynamic library 'libnvinfer_plugin.so.6'; dlerror: libnvinfer_plugin.so.6: cannot open shared object file: No such file or directory
    2020-02-09 21:58:02.454820: W tensorflow/compiler/tf2tensorrt/utils/py_utils.cc:30] Cannot dlopen some TensorRT libraries. If you would like to use Nvidia GPU with TensorRT, please make sure the missing libraries mentioned above are installed properly.
    2.1.0