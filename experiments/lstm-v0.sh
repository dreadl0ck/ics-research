#!/bin/bash

# SGD optimizer, corelayer: 10, wrap: 5, 10 epochs

python3 train.py \
    -read "data/SWaT2015-Attack-Files-v0.2/train/2015-12-28_113021_98.log.part12_sorted-labeled.csv" \
    -wrapLayerSize 32 \
    -coreLayerSize 128 \
    -epoch 10 \
    -lstm true \
    -features 17 \
    -batchSize 100000

# EVAL
python3 score.py \
    -read "data/SWaT2015-Attack-Files-v0.2/train/2015-12-28_113021_98.log.part13_sorted-labeled.csv" \
    -wrapLayerSize 32 \
    -dropoutLayer true \
    -coreLayerSize 128 \
    -features 17 \
    -lstm true  \
    -batchSize 100000