#!/bin/bash

python3 train.py \
    -read "$1" \
    -wrapLayerSize 16 \
    -dropoutLayer false \
    -relu true \
    -coreLayerSize 64 \
    -numCoreLayers 3 \
    -optimizer sgd \
    -epoch 10 \
    -features 16 \
    -lstm true \
    -drop modbus_value

# EVAL
python3 score.py \
    -read "$2" \
    -wrapLayerSize 16 \
    -dropoutLayer false \
    -relu true \
    -coreLayerSize 64 \
    -numCoreLayers 3 \
    -optimizer sgd \
    -features 16 \
    -lstm true \
    -drop modbus_value