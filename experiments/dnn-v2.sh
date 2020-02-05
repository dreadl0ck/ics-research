#!/bin/bash

# no sgd, dropoutlayer, corelayer: 50, wrap: 10, 20 epochs

python3 train.py \
    -read "data/SWaT2015-Attack-Files-v0.4/train/*-labeled.csv" \
    -wrapLayerSize 10 \
    -dropoutLayer true \
    -coreLayerSize 50 \
    -epoch 20 \
    -features 15 \
    -drop modbus_value

# EVAL
python3 score.py \
    -read "data/SWaT2015-Attack-Files-v0.4/eval/*-labeled.csv" \
    -wrapLayerSize 10 \
    -dropoutLayer true \
    -coreLayerSize 50 \
    -features 15 \
    -drop modbus_value
