#!/usr/bin/python3

# Run LSTM, locally:
# $ ./readcsv.py -read data/TCP_labeled.csv -dimensionality 22 -class_amount 2 -sample 0.5 -lstm true
# on server, 2019 SWaT dataset:
# $ ./readcsv.py -read */TCP_labeled.csv -dimensionality 22 -class_amount 2 -sample 0.5 -lstm true
# on server, 2015 SWaT dataset:
# $ ./readcsv.py -read */*_labeled.csv -dimensionality XX -class_amount 2 -sample 0.5 -lstm true

from tfUtils import * 
from glob import glob
import argparse

import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn import metrics

import keras
from keras.models import Sequential
from keras.layers.core import Dense, Activation
from keras.callbacks import EarlyStopping
from termcolor import colored
import traceback

import sys
import time

monitor = EarlyStopping(
    monitor='val_loss', 
    min_delta=1e-3, 
    patience=5, 
    verbose=1, 
    mode='auto'
)

cf_total = None

BATCH_SIZE = 2048

# TODO make configurable via argument
# hardcoded these are the labeltypes that can be found in the dataset
#labeltypes = ["normal", "Single Stage Single Point", "Single Stage Multi Point", "Multi Stage Single Point", "Multi Stage Multi Point"]
labeltypes = ["Normal", "Attack"]

# cf_total is for summing up all of the confusion matrices from all of the seperate files
labeltypes_length = len(labeltypes)
cf_total = np.zeros((labeltypes_length, labeltypes_length),dtype=np.int)

def readCSV(f):
    print("[INFO] reading file", f)
    return pd.read_csv(f, delimiter=',', engine='c', encoding="utf-8-sig")

def run():
    leftover = None

    for file_name in files:
        df = readCSV(file_name)

        print("[INFO] process dataset, shape:", df.shape)

        if arguments.drop is not None:
            for col in arguments.drop.split(","):
                drop_col(col, df)


        if not arguments.lstm:
            print("dropping all time related columns...")
            drop_col('unixtime',df)

        drop_col('SessionID', df)

        print("[INFO] columns:", df.columns)

        print("[INFO] analyze dataset:", df.shape)
        analyze(df)

        print("[INFO] encoding dataset:", df.shape)
#        encode_columns(df, arguments.result_column, arguments.lstm, arguments.debug)
        print("[INFO] AFTER encoding dataset:", df.shape)

        # lstmBatchSize = arguments.lstmBatchSize
        # if arguments.lstm:
        #     #for batch_index in range(0, df.shape[0], lstmBatchSize):
        #         print("[INFO] processing batch {}-{}/{} for LSTM".format(batch_index, batch_index+lstmBatchSize, df.shape[0]))
        #         dfCopy = df[batch_index:batch_index+lstmBatchSize]

        #         # skip leftover that does not reach batch size
        #         if len(dfCopy.index) != lstmBatchSize:
        #             leftover = dfCopy
        #             continue

        #         eval_dnn(dfCopy)
        #         leftover = None
        # else:
        eval_dnn(df)

import sys

def eval_dnn(df):
    global cf_total

    x_test, y_test = to_xy(df, arguments.result_column, labeltypes)
    print("x_test", x_test, "shape", x_test.shape)
    
    #np.set_printoptions(threshold=sys.maxsize)
    print("y_test", y_test, "shape", y_test.shape)
    #np.set_printoptions(threshold=10)

    # Create a new model instance

    # Load the previously saved weights
    model.load_weights(arguments.model)
    print(colored("[INFO] measuring accuracy...", 'yellow'))
    print("x_test.shape:", x_test.shape)

    print(colored("[INFO] model summary:", 'yellow'))
    model.summary()

    y_eval = np.argmax(y_test,axis=1)
    print("y_eval", y_eval, y_eval.shape)

    if arguments.debug:
        print("--------SHAPES--------")
        print("x_test.shape", x_test.shape)
        print("y_test.shape", y_test.shape)

    if arguments.lstm:

        print("[INFO] reshape for using LSTM layers")
        x_test = x_test.reshape(16, int(x_test.shape[0]/16), x_test.shape[1])
        y_test = y_test.reshape(16, int(y_test.shape[0]/16), y_test.shape[1])

        if arguments.debug:
            print("--------RESHAPED--------")
            print("x_test.shape", x_test.shape)
            print("y_test.shape", y_test.shape)
    
    pred = model.predict(x_test)
    print("pred 1", pred, pred.shape)

    if arguments.lstm:         
        pred = pred.reshape(16*y_test.shape[1], y_test.shape[2])
        print("pred 2", pred, pred.shape)

    pred = np.argmax(pred,axis=1)
    print("pred 3 (argmax)", pred, pred.shape)

    if not arguments.lstm:
        score = metrics.accuracy_score(y_eval, pred)
        print("[INFO] Validation score: {}".format(colored(score, 'yellow')))
    
    print(colored("[INFO] metrics:", 'yellow'))
    baseline_results = model.evaluate(
        x_test,
        y_test,
        batch_size=BATCH_SIZE,
        verbose=0
    )
    print("---- for loop ----") 
    for name, value in zip(model.metrics_names, baseline_results):
        print(name, ': ', value)
    print()
    
    unique, counts = np.unique(y_eval, return_counts=True)
    print("y_eval",dict(zip(unique, counts)))
# 
    unique, counts = np.unique(pred, return_counts=True)
    print("pred",dict(zip(unique, counts)))
# 
#             print("y_test", np.sum(y_test,axis=0), np.sum(y_test,axis=1))

    cf = confusion_matrix(y_eval,pred,labels=np.arange(len(labeltypes)))
    print("[INFO] confusion matrix for file ")
    print(cf)
    print("[INFO] confusion matrix after adding it to total:")
    cf_total += cf
    print(cf_total)

#             cf = np.zeros((5,5))
#             for i,j in zip(y_eval, pred):
#                 cf[i,j] += 1
#             print(cf)
                
# instantiate the parser
parser = argparse.ArgumentParser(description='NETCAP compatible implementation of Network Anomaly Detection with a Deep Neural Network and TensorFlow')

# add commandline flags
parser.add_argument('-read', required=True, type=str, help='Regex to find all labeled input CSV file to read from (required)')
parser.add_argument('-model', required=True, type=str, help='the path to the checkpoint to be tested on')
parser.add_argument('-drop', type=str, help='optionally drop specified columns, supply multiple with comma')
#parser.add_argument('-sample', type=float, default=1.0, help='optionally sample only a fraction of records')
#parser.add_argument('-dropna', default=False, action='store_true', help='drop rows with missing values')
#parser.add_argument('-test_size', type=float, default=0.5, help='specify size of the test data in percent (default: 0.25)')
parser.add_argument('-loss', type=str, default='categorical_crossentropy', help='set function (default: categorical_crossentropy)')
parser.add_argument('-optimizer', type=str, default='adam', help='set optimizer (default: adam)')
parser.add_argument('-result_column', type=str, default='classification', help='set name of the column with the prediction')
parser.add_argument('-dimensionality', type=int, required=True, help='The amount of columns in the csv')
#parser.add_argument('-class_amount', type=int, default=2, help='The amount of classes e.g. normal, attack1, attack3 is 3')
#parser.add_argument('-batch_size', type=int, default=2, help='The amount of files to be read in. (default: 1)')
#parser.add_argument('-epochs', type=int, default=1, help='The amount of epochs. (default: 1)')
parser.add_argument('-numCoreLayers', type=int, default=1, help='set number of core layers to use')
#parser.add_argument('-shuffle', default=False, help='shuffle data before feeding it to the DNN')
parser.add_argument('-dropoutLayer', default=False, help='insert a dropout layer at the end')
parser.add_argument('-coreLayerSize', type=int, default=4, help='size of an DNN core layer')
parser.add_argument('-wrapLayerSize', type=int, default=2, help='size of the first and last DNN layer')
parser.add_argument('-lstm', default=False, help='use a LSTM network')
parser.add_argument('-lstmBatchSize', type=int, default=125000, help='LSTM network input number of rows')
parser.add_argument('-debug', default=False, help='debug mode on off')

# parse commandline arguments
arguments = parser.parse_args()
if arguments.read is None:
    print("[INFO] need an input file / multi file regex. use the -read flag")
    exit(1)

# get all files
files = glob(arguments.read)
files.sort()

# create models
model = create_dnn(
    arguments.dimensionality,
    len(labeltypes),
    arguments.loss,
    arguments.optimizer,
    arguments.lstm,
    arguments.numCoreLayers,
    arguments.coreLayerSize,
    arguments.dropoutLayer,
    arguments.lstmBatchSize,
    arguments.wrapLayerSize
)
print("[INFO] created DNN")


# MAIN
try:
    run()
except: # catch *all* exceptions
    e = sys.exc_info()
    print("[EXCEPTION]", e)
    traceback.print_tb(e[2], None, None)

