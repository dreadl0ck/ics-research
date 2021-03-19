# README

This repository contains code and configuration notes for Intrusion Detection in Industrial Control Systems, in the context of the SWaT testbed maintained by the University of Singapore.

Created by Philipp Mieden and Rutger Beltman as part of their RP1 at the Security and Network Engineering programme at the University of Amsterdam.

- Paper: https://delaat.net/rp/2019-2020/p52/report.pdf
- Presentation: https://delaat.net/rp/2019-2020/p52/presentation.pdf

## Dataset download

Infos about the dataset and procedure to obtain access can be found here: https://itrust.sutd.edu.sg/itrust-labs_datasets/dataset_info

We used the drive tool to download the files: https://github.com/odeke-em/drive

```
go get -u github.com/odeke-em/drive/cmd/drive
mkdir -p /mnt/storage/gdrive
drive init /mnt/storage/gdrive
cd /mnt/storage/gdrive
drive list
```

In order to be able to download the shared files, we first had to import them into our own drive, as described here: https://webapps.stackexchange.com/a/141694

Afterwards pull with:

```
cd /mnt/storage/gdrive
drive pull SWaT-Dataset
```

## Setup scripts

The [zeus](http://github.com/dreadl0ck/zeus) build system is used to compile all the go tools and deploy them to the experiment server.

You will need to export two environment variables to indicate your user account name and the server host, in order to connect via SSH:

    export ICS_RESEARCH_USER="..." 
    export ICS_RESEARCH_EXPERIMENT_SERVER="..."

Afterwards, compile the tools and deploy to your server:

    $ zeus deploy-tools

To install the required python toolchain and tensorflow on a debian linux system, use:

    $ zeus setup-server

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

If you are using a recent CPU on your experiment server, you can simply install the latest version of tensorflow from the standard package mirrors of your distribution.

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
    
## Label 2015 Dataset

### Physical Data

We did analyze and experiment with the physical data, but did not use it for our experiments and evaluation,
since we scoped the research to the analysis of network events only.

During analysis, we noticed that there were some typos in the classification columns, and created a small tool to automate fixing them:

    $ GOOS=linux go build -o bin/fix-swat-dataset cmd/fix-dataset/fix-swat-dataset.go
    $ fix-swat-dataset SWaT_Dataset_Attack_v0.csv

### Network Data

Convert Attack .xlsx Spreadsheet to CSV:

    apt install -y gnumeric
    cd '/mnt/storage/gdrive/SWaT-Dataset/SWaT.A1 & A2_Dec 2015'
    ssconvert List_of_attacks_Final.xlsx List_of_attacks_Final.csv > /dev/null 2>&1

Next we need to prepare the list of attacks to be usable for labeling the network data.
We convert the timestamps to Unix, calculate attack durations and add the information about the attack type to every row of the data.
The attack types have been previously marked by colorization of a row, we have manually mapped each attack number to the corresponding attack type,
the logic for this can be found in the _cmd/prepare-labels_ tool.
Finally, the IP addresses associated with the attacked devices are added to each column.
The timeframe of an attack in combination with the affected device IPs will be used to label the provided network data later on. 

We ignore all attacks that are listed as 'No Physical Impact',
since there is no further information provided for those and we are only interested in attacks that caused changes to the physical environment.

Prepare label information for 2015 Network Data using the _cmd/prepare-labels_ tool:

	GOOS=linux go build -o bin/prepare-labels cmd/prepare-labels/prepare-labels.go
	scp bin/prepare-labels user@someserver.net:/home/user
    $ prepare-labels -input List_of_attacks_Final.csv
    skipping attack number 5
    skipping attack number 9
    skipping attack number 12
    skipping attack number 15
    skipping attack number 18
    36 attacks written to List_of_attacks_Final-fixed.csv
    header: [AttackNumber AttackNumberOriginal StartTime EndTime AttackDuration AttackPoints Addresses AttackName AttackType Intent ActualChange Notes]

Now we can apply label information to the provided network data.

The first tool we created for this purpose can be found in _cmd/label-dataset_. 
During our experiments however, we found that in order to encode the chunked data properly, 
the normalization needs to be calculated based on the entire available data.

An additional tool for processing has been created, that can be found in _cmd/analyze_.
It supports not only labeling the network events based on the previously generated attack information,
but also handles encoding and normalization, based on standard deviation over the entire dataset.  

#### Label 2015 dataset attack files

In order to encode and normalize the data, a summary for all values that appear in a column over the entire dataset needs to be created.
Due to performance reasons, we ported this functionality from python (encode_columns.py) to Go. 

We named this summary structure column summaries, it is sometimes referred to as colsums in our documentation and code.

The file _data/attack-files.txt_ contains the names of all files that contained attacks,
the analyze tool offers a flag to filter the files selected for processing based on this list. 

Build analyze tool:

```
GOOS=linux go build -o bin/analyze cmd/analyze/*.go
```

You can either:

1) Generate column summaries only:

```
analyze -attacks List_of_attacks_Final-fixed.csv -file-filter attack-files.txt -analyze-only
```

2) Generate column summaries and use them to generate labeled files with numeric value encoding and normalization:

```
$ screen -L analyze -attacks List_of_attacks_Final-fixed.csv -file-filter attack-files.txt -out SWaT2015-Attack-Files
```

To label using a specific column summary version, use the _-colsums_ flag.

The analyze tool will search recursively in the current directory for files that end on '_sorted.csv', you can pass a specific location via _-in_.

All flags available for the _analyze_ tool:

    $ analyze -h
    Usage of analyze:
      -analyze-only
        analyze only
      -attacks string
        attack list CSV
      -colsums string
        column summary JSON file for loading
      -count-attacks
        count attacks
      -debug
        toggle debug mode
      -encode
        encode the values to numeric format (default true)
      -encodeCategoricals
        encode the categorical values to numeric format (default true)
      -file-filter string
        supply a text file with newline separated filenames to process
      -in string
        input directory (default is current directory) (default ".")
      -max int
        max number of processed files
      -normalizeCategoricals
        normalize the categorical values after encoding them to numeric format (default true)
      -offset int
        index offset from which file to start
      -out string
        output path (default ".")
      -reuse
        reuse CSV line buffer (default true)
      -skip-incomplete
        skip lines that contain empty values
      -suffix string
        suffix for all csv files to be parsed (default "_sorted.csv")
      -version
        print version
      -workers int
        number of parallel processed files (default 100)
      -zero-incomplete
        skip lines that contain empty values (default true)
      -zscore
        use zscore for normalization

> TODO: Dump the tool configuration and a short summary into the output directory. 

## Label 2019 Dataset

We experimented also with the 2019 captures of the dataset, created tooling to analyze them using netcap and label the resulting audit records.

However, we had to stop this effort due to time constraints.   

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
    cd /home/user/labeled-SWaT-2015-network
    screen -L ../ics-research/train.py -read "*-labeled.csv" -dimensionality 19 -lstm true -lstmBatchSize 250000

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

    user@brussels:/home/user/labeled-SWaT-2015-network# ../ics-research/train.py -read "*-labeled.csv" -dimensionality 19 -lstm true -lstmBatchSize 10000 -epochs 3
    
> commit version: 8fd1f38e275303bca1ae861a21b91720e4856bd2

## Command Log

### Regular DNN on 2015 labeled dataset

run 1: 27/1

command:
   
    python3 train.py -read "/mnt/terradrive/labeled-SW015-network/*.csv" -dimensionality 19 -epochs 10

commit version:
    
    user@someserver.net:~/ics-research$ git rev-parse HEAD  
    4f5ed93d439ca30cf82654f77f0186447327b9e0

run 2: 28/1

command:

   python3 train.py -read "/mnt/terradrive/labeled-SW015-network/*.csv" -dimensionality 19 -epochs 10

commit version:

    user@someserver.net:~/ics-research$ git rev-parse HEAD
    f54739686d56ae45d7d0eeb9c2bbfaa3fcb7d10a


run 3: 28/1 14:55

command:

    screen -L python3 train.py -read "/mnt/terradrive/labeled-SWaT-2015-network/2015-12-26_121116_89.log.part03_sorted-labeled.csv" -dimensionality 14 -epochs 10 -debug true -drop service,Modbus_Function_Code

commit version:

    user@someserver.net:~/ics-research$ git rev-parse HEAD
    20fd6a5fb6239627eb4e7d791496368861e0e3f0

run 4: 28/1 16:16

command:

    screen -L python3 -u train.py -read "/mnt/terradrive/labeled-SWaT-2015-network/*csv" -dimensionality 14 -epochs 10 -debug true -drop service,Modbus_Function_Cod

commit version:

    user@someserver.net:/home/user/ics-research# git rev-parse HEAD
    20fd6a5fb6239627eb4e7d791496368861e0e3f0


run 5: 28/1 23:55

command:

    (reverse-i-search)`-L': screen -L python3 -u train.py -read "/mnt/terradrive/labeled-SWaT-2015-network/*csv" -dimensionality 15 -epochs 10 -debug true -drop service,Modbus_Function_Cod


commit version:

    user@someserver.net:/home/user/ics-research# git rev-parse HEAD
    322ee5783702a582b86dd7dd015ccb84be3d54e2


run 6: 29-1 16:40 - prepared, but not ran

    screen -L python3 -u train.py -read "/mnt/terradrive/labeled-SWaT-2015-network/*csv" -dimensionality 15 -epochs 10 -debug true -drop service,Modbus_Function_Code

## Dataset analyzer

Tool is located in _cmd/analyzer_.

### Analysis

- which files contain attacks
- unique strings for each row
- mean, stddev, min and max for numbers

### Preprocessing

- drop columns that only contain a single value
- fix typos: ip, log and loe, Responqe etc
- merge num, date and time to UNIX timestamps

### Encoding

- zscore numbers
- encode strings to numbers

### Labeling

- use attack types

### Dataset split

- dataset split: 50% train, 25% test, 25% validation, LSTM batch size: 125000

- IMPORTANT: preserve order when using LSTM
- add code to run evaluation and print results

- DROP columns: Tag, date, num and time

### TODOs

- add progress indicator
- fix checkpoint naming for lstm: 'files' wrong

Generate colsums:

    go run ../../analyze -analyze
    # output: colSums-29Jan2020-170358.json

Build:

    GOOS=linux go build -o bin/analyze ./analyze
	scp bin/analyze user@someserver.net:/home/user

Start analysis and labeling on oslo:

    cd "/datasets/SWaT/01_SWaT_Dataset_Dec 2015/Network"

Local:

    cd Network
    go run ../../analyze -attacks List_of_attacks_Final-fixed.csv -file-filter attack-files.txt -suffix "_sorted.csv" -colsums colSums-29Jan2020-221001.json -workers 25

Oslo:

    screen -L /home/user/analyze -attacks List_of_attacks_Final-fixed.csv -suffix "_sorted.csv" -out /home/user/labeled-SWaT-2015-network -colsums /home/user/colSums-29Jan2020-221001.json -workers 25

Brussels:

    screen -L /home/user/analyze -attacks List_of_attacks_Final-fixed.csv -suffix "_sorted.csv" -colsums /home/user/colSums-29Jan2020-221001.json -workers 25 -offset 392

# Push dataset to all servers

    scp -r -P 9876 data/Network user@someserver.net:/home/user
    scp -r -P 9876 data/Network user@someserver.net:/home/user
    scp -r data/Network user@someserver.net:/home/user

Push labeling tool:

    GOOS=linux go build -o bin/analyze ./analyze
    scp -P 9876 bin/analyze user@someserver.net:/home/user
    scp -P 9876 bin/analyze user@someserver.net:/home/user
    scp bin/analyze user@someserver.net:/home/user

Start:

    cd Network

Brussels (1/4 Train)

    ../analyze -attacks List_of_attacks_Final-fixed.csv -suffix _sorted.csv -colsums colSums-29Jan2020-221001.json -workers 25 -offset 0 -max 196 -out SWaT2015-Network-Labeled-Pt1

Oslo (2/4 Train)

    ../analyze -attacks List_of_attacks_Final-fixed.csv -suffix _sorted.csv -colsums colSums-29Jan2020-221001.json -workers 25 -offset 196 -max 392 -out SWaT2015-Network-Labeled-Pt2

Mac (3/4 Test)

    go run ../../analyze -attacks List_of_attacks_Final-fixed.csv -suffix _sorted.csv -colsums colSums-29Jan2020-221001.json -workers 25 -offset 392 -max 588 -out SWaT2015-Network-Labeled-Pt3

    screen -L /home/user/analyze -attacks /home/user/Network/List_of_attacks_Final-fixed.csv -suffix _sorted.csv -colsums /home/user/Network/colSums-29Jan2020-221001.json -workers 25 -offset 392 -max 588 -out /home/user/Network/SWaT2015-Network-Labeled

Bastia (4/4 Eval)

    ../analyze -attacks List_of_attacks_Final-fixed.csv -suffix _sorted.csv -colsums colSums-29Jan2020-221001.json -workers 25 -offset 588 -out SWaT2015-Network-Labeled-Pt4

    screen -L /home/user/analyze -attacks /home/user/Network/List_of_attacks_Final-fixed.csv -suffix _sorted.csv -colsums /home/user/Network/colSums-29Jan2020-221001.json -workers 25 -offset 392 -max 588 -out /home/user/Network/SWaT2015-Network-Labeled

## LSTM Evaluation

    cd data/SwaT2015-Attack-Files-v0.2

Train

    python3 ../../train.py -read "*-labeled.csv" -dimensionality 16 -lstm true -optimizer sgd -drop modbus_value

    python3 ../../train.py -read "*-labeled.csv" -dimensionality 17 -lstm true -optimizer sgd

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

## TODOs

- normalize values for strings and rerun experiments
- zscore timestamps
- amount of neurons / layers?
- vary lstm batch size
- sgd / non-sgd
- lstm / normal

- layer configuration !! single layers VS multiple
- save and load entire model configuration:

> Call model.save to save the a model's architecture, weights, and training configuration in a single file/folder. This allows you to export a model so it can be used without access to the original Python code*. Since the optimizer-state is recovered, you can resume training from exactly where you left off.

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

### DNN

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

### LSTM

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

## Evaluation

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

## Report

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
    user@brussels:/home/user# uname -a
    Linux brussels 4.15.0-74-generic #84-Ubuntu SMP Thu Dec 19 08:06:28 UTC 2019 x86_64 x86_64 x86_64 GNU/Linux
    user@brussels:/home/user# python3 -c 'import tensorflow as tf; print(tf.__version__)'
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
    user@someserver.net:/home/user# uname -a
    Linux bastia 4.15.0-66-generic #75-Ubuntu SMP Tue Oct 1 05:24:09 UTC 2019 x86_64 x86_64 x86_64 GNU/Linux
    user@someserver.net:/home/user#     python3 -c 'import tensorflow as tf; print(tf.__version__)'
    2020-02-09 21:58:02.454559: W tensorflow/stream_executor/platform/default/dso_loader.cc:55] Could not load dynamic library 'libnvinfer.so.6'; dlerror: libnvinfer.so.6: cannot open shared object file: No such file or directory
    2020-02-09 21:58:02.454784: W tensorflow/stream_executor/platform/default/dso_loader.cc:55] Could not load dynamic library 'libnvinfer_plugin.so.6'; dlerror: libnvinfer_plugin.so.6: cannot open shared object file: No such file or directory
    2020-02-09 21:58:02.454820: W tensorflow/compiler/tf2tensorrt/utils/py_utils.cc:30] Cannot dlopen some TensorRT libraries. If you would like to use Nvidia GPU with TensorRT, please make sure the missing libraries mentioned above are installed properly.
    2.1.0