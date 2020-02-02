#!/bin/bash

# SGD optimizer, corelayer: 10, wrap: 5, 10 epochs

python3 train.py \
    -read "data/SWaT2015-Attack-Files-v0.2/train/2015-12-28_113021_98.log.part12_sorted-labeled.csv" \
    -wrapLayerSize 5 \
    -dropoutLayer true \
    -coreLayerSize 10 \
    -epoch 10 \
    -zscoreUnixtime true \
    -lstm true \
    -features 16 \
    -drop modbus_value \
    -batchSize 100000

# EVAL
python3 score.py \
    -read "data/SWaT2015-Attack-Files-v0.2/train/2015-12-28_113021_98.log.part13_sorted-labeled.csv" \
    -wrapLayerSize 5 \
    -dropoutLayer true \
    -coreLayerSize 10 \
    -features 16 \
    -drop modbus_value  \
    -lstm true  \
    -zscoreUnixtime true \
    -batchSize 100000