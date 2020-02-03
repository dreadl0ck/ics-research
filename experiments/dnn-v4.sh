#!/bin/bash

# dropout layer, corelayer: 50, wrap: 10, 30 epochs

python3 train.py \
    -read "data/SWaT2015-Attack-Files-v0.2/train/*-labeled.csv" \
    -wrapLayerSize 10 \
    -optimizer sgd \
    -dropoutLayer true \
    -coreLayerSize 50 \
    -epoch 30 \
    -features 15 \
    -drop modbus_value

# EVAL
python3 score.py \
    -read "data/SWaT2015-Attack-Files-v0.2/eval/*-labeled.csv" \
    -wrapLayerSize 10 \
    -optimizer sgd \
    -dropoutLayer true \
    -coreLayerSize 50 \
    -features 15 \
    -drop modbus_value
