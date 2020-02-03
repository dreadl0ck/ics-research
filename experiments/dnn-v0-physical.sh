#!/bin/bash -e

# SGD optimizer, dropout layer, corelayer: 10, wrap: 5, 20 epochs

python3 -u train.py \
    -read "data/SWaT_Dataset_Attack_v0-fixed-zscore-train-test.csv" \
    -wrapLayerSize 10 \
    -dropoutLayer true \
    -coreLayerSize 50 \
    -epoch 10\
    -features 45 \
    -drop modbus_value \
    -resultColumn "Normal/Attack" -classes Normal,Attack 

# EVAL
python3 -u score.py \
    -read "data/SWaT_Dataset_Attack_v0-fixed-zscore-eval.csv" \
    -wrapLayerSize 10 \
    -dropoutLayer true \
    -coreLayerSize 50 \
    -features 45 \
    -drop modbus_value \
    -resultColumn "Normal/Attack" \
    -classes Normal,Attack \
    -batchSize 500



