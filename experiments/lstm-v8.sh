#!/bin/bash

python3 train.py \
    -read "$1" \
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
    -read "$2" \
    -wrapLayerSize 16 \
    -dropoutLayer true \
    -relu true \
    -coreLayerSize 64 \
    -numCoreLayers 3 \
    -optimizer adam \
    -features 16 \
    -lstm true \
    -drop modbus_value