#!/bin/bash -e

# SGD optimizer, dropout layer, corelayer: 10, wrap: 5, 20 epochs

python3 train.py \
    -read "data/SWaT2015-Attack-Files-v0.2/train/2015-12-28_113021_98.log.part12_sorted-labeled.csv" \
    -wrapLayerSize 32 \
    -dropoutLayer true \
    -coreLayerSize 128 \
    -numCoreLayers 3 \
    -optimizer sgd \
    -epoch 10 \
    -features 15 \
    -drop modbus_value

# EVAL
python3 score.py \
    -read "data/SWaT2015-Attack-Files-v0.2/train/2015-12-28_113021_98.log.part13_sorted-labeled.csv" \
    -wrapLayerSize 32 \
    -dropoutLayer true \
    -coreLayerSize 128 \
    -numCoreLayers 3 \
    -optimizer sgd \
    -features 15 \
    -drop modbus_value
