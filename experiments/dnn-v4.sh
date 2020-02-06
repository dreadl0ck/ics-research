#!/bin/bash

python3 train.py \
    -read "data/SWaT2015-Attack-Files-v0.4/train/2015-12-28_113021_98.log.part12_sorted-labeled.csv" \
    -wrapLayerSize 8 \
    -dropoutLayer true \
    -relu false \
    -coreLayerSize 32 \
    -numCoreLayers 1 \
    -optimizer adam \
    -epoch 10 \
    -features 15 \
    -drop modbus_value

# EVAL
python3 score.py \
    -read "data/SWaT2015-Attack-Files-v0.4/train/2015-12-28_113021_98.log.part13_sorted-labeled.csv" \
    -wrapLayerSize 8 \
    -dropoutLayer true \
    -relu false \
    -coreLayerSize 32 \
    -numCoreLayers 1 \
    -optimizer adam \
    -features 15 \
    -drop modbus_value