#!/bin/bash

python3 train.py \
    -read "$1" \
    -wrapLayerSize 8 \
    -dropoutLayer true \
    -relu true \
    -coreLayerSize 32 \
    -numCoreLayers 1 \
    -optimizer sgd \
    -epoch 3 \
    -features 16 \
    -lstm true \
    -drop modbus_value

# EVAL
python3 score.py \
    -read "$2" \
    -wrapLayerSize 8 \
    -dropoutLayer true \
    -relu true \
    -coreLayerSize 32 \
    -numCoreLayers 1 \
    -optimizer sgd \
    -features 16 \
    -lstm true \
    -drop modbus_value