#!/bin/bash

python3 train.py \
    -read "data/SWaT2015-Attack-Files-v0.4-minmax/train/2015-12-28_113021_98.log.part12_sorted-labeled.csv" \
    -wrapLayerSize 16 \
    -dropoutLayer true \
    -relu true \
    -coreLayerSize 64 \
    -numCoreLayers 3 \
    -optimizer adam \
    -epoch 20 \
    -features 16 \
    -lstm true \
    -drop modbus_value

# EVAL
python3 score.py \
    -read "data/SWaT2015-Attack-Files-v0.4-minmax/train/2015-12-28_113021_98.log.part13_sorted-labeled.csv" \
    -wrapLayerSize 16 \
    -dropoutLayer true \
    -relu true \
    -coreLayerSize 64 \
    -numCoreLayers 3 \
    -optimizer adam \
    -features 16 \
    -lstm true \
    -drop modbus_value