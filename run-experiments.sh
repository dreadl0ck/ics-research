#!/bin/bash -e

# # TRAIN
# python3 train.py \
#     -read "data/SWaT2015-Attack-Files-v0.2/2015-12-28_113021_98.log.part12_sorted-labeled.csv" \
#     -features 15 \
#     -optimizer sgd \
#     -drop modbus_value \
#     -saveModel true
#     #-lstm true \

# # EVAL
# python3 score.py \
#     -read "data/SWaT2015-Attack-Files-v0.2/2015-12-28_113021_98.log.part13_sorted-labeled.csv" \
#     -features 15 \
#     -optimizer sgd \
#     -weights data/SWaT2015-Attack-Files-v0.2/checkpoints/dnn-epoch-1-files-0-1  \
#     -drop modbus_value  \
#     -debug true
#     #-lstm true  \

# save model

# TRAIN
# python3 train.py \
#     -read "data/SWaT2015-Attack-Files-v0.2/2015-12-28_113021_98.log.part12_sorted-labeled.csv" \
#     -wrapLayerSize 5 \
#     -dropoutLayer true \
#     -coreLayerSize 10 \
#     -epoch 3 \
#     -zscoreUnixtime true \
#     -lstm true \
#     -features 16 \
#     -drop modbus_value \
#     -debug true
#     #-saveModel true

# # EVAL
# python3 score.py \
#     -read "data/SWaT2015-Attack-Files-v0.2/2015-12-28_113021_98.log.part13_sorted-labeled.csv" \
#     -wrapLayerSize 5 \
#     -dropoutLayer true \
#     -coreLayerSize 10 \
#     -features 16 \
#     -weights checkpoints/lstm-epoch-3-files-0-1-batch-375000-500000 \
#     -drop modbus_value  \
#     -lstm true  \
#     -zscoreUnixtime true \
#     -debug true

# Using too large a batch size can have a negative effect on the accuracy of your network during training since it reduces the stochasticity of the gradient descent.

python3 train.py \
    -read "data/SWaT2015-Attack-Files-v0.2/2015-12-28_113021_98.log.part12_sorted-labeled.csv" \
    -wrapLayerSize 5 \
    -dropoutLayer true \
    -coreLayerSize 10 \
    -epoch 1 \
    -zscoreUnixtime true \
    -lstm true \
    -features 16 \
    -drop modbus_value \
    -lstmBatchSize 1000 \
    -debug true
    #-saveModel true

# EVAL
python3 score.py \
    -read "data/SWaT2015-Attack-Files-v0.2/2015-12-28_113021_98.log.part13_sorted-labeled.csv" \
    -wrapLayerSize 5 \
    -dropoutLayer true \
    -coreLayerSize 10 \
    -features 16 \
    -weights checkpoints/lstm-epoch-1-files-0-1-batch-499000-500000 \
    -drop modbus_value  \
    -lstm true  \
    -zscoreUnixtime true \
    -lstmBatchSize 1000 \
    -debug true

#alternative: 1200