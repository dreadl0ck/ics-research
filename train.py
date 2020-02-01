#!/usr/bin/python3

# Run LSTM, locally:
# $ ./readcsv.py -read data/TCP_labeled.csv -dimensionality 22 -class_amount 2 -sample 0.5 -lstm true
# on server, 2019 SWaT dataset:
# $ ./readcsv.py -read */TCP_labeled.csv -dimensionality 22 -class_amount 2 -sample 0.5 -lstm true
# on server, 2015 SWaT dataset:
# $ ./readcsv.py -read */*_labeled.csv -dimensionality XX -class_amount 2 -sample 0.5 -lstm true

import argparse
import pandas as pd
import keras
import traceback
import sys
import datetime

from tfUtils import * 
from glob import glob
from os import path
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from keras.models import Sequential
from keras.layers.core import Dense, Activation
from keras.callbacks import EarlyStopping
from termcolor import colored

monitor = EarlyStopping(
    monitor='val_loss', 
    min_delta=1e-3, 
    patience=5, 
    verbose=1, 
    mode='auto'
)

# hardcoded these are the labeltypes that can be found in the dataset
# can be overwritten via cmdline flags
classes = ["normal", "Single Stage Single Point", "Single Stage Multi Point", "Multi Stage Single Point", "Multi Stage Multi Point"]
#classes = ["Normal", "Attack"]

def train_dnn(df, i, epoch, batch_index=None):

    print("[INFO] breaking into predictors and prediction...")
    # Break into X (predictors) & y (prediction)
    x, y = to_xy(df, arguments.resultColumn, classes, arguments.debug)

    print("[INFO] creating train/test split:", arguments.testSize)

    # Create a test/train split.
    # by default, 25% of data is used for testing
    # it can be configured using the test_size commandline flag
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=arguments.testSize,
        random_state=42, # TODO
        shuffle=arguments.shuffle
    )

    if arguments.debug:
        print("--------SHAPES--------")
        print("x_train.shape", x_train.shape)
        print("x_test.shape", x_test.shape)
        print("y_train.shape", y_train.shape)
        print("y_test.shape", y_test.shape)

    if arguments.lstm:

        print("[INFO] using LSTM layers")
        x_train = x_train.reshape(8000, int(x_train.shape[0]/8000), x.shape[1])
        y_train = y_train.reshape(8000, int(y_train.shape[0]/8000), y.shape[1])

        x_test = x_test.reshape(2000, int(x_test.shape[0]/2000), x.shape[1])
        y_test = y_test.reshape(2000, int(y_test.shape[0]/2000), y.shape[1])

        if arguments.debug:
            print("--------RESHAPED--------")
            print("x_train.shape", x_train.shape)
            print("x_test.shape", x_test.shape)
            print("y_train.shape", y_train.shape)
            print("y_test.shape", y_test.shape)

    # TODO: using a timestep size of 1 and feeding numRows batches should also work
    #x_train = np.reshape(x_train, (x_train.shape[0], 1, x_train.shape[1]))
    #x_test = np.reshape(x_test, (x_test.shape[0], 1, x_test.shape[1]))

    print("[INFO] fitting model")
    model.fit(
        x_train,
        y_train,
        validation_data=(x_test, y_test),
        callbacks=[monitor],
        verbose=2,
        epochs=1,
        batch_size=32
    )

#    print('---------intermediate testing--------------')
#    
#    pred = model.predict(x_test)
#    pred = np.argmax(pred,axis=1)
#    y_eval = np.argmax(y_test,axis=1)
#    unique, counts = np.unique(y_eval, return_counts=True)
#    print("y_eval",dict(zip(unique, counts)))
# 
#    unique, counts = np.unique(pred, return_counts=True)
#    print("pred",dict(zip(unique, counts)))
#
#    cf = confusion_matrix(y_eval,pred,labels=np.arange(len(labeltypes)))
#    print("[info] confusion matrix for file ")
#    print(cf)
#    print('-----------------------------')
    
    if arguments.saveModel:
        save_model(i, epoch, batch_index=batch_index)
    else:
        save_weights(i, epoch, batch_index=batch_index)

def save_model(i, epoch, batch_index=None):
    if not path.exists("models"):
        os.mkdir("models")

    if arguments.lstm:
        print("[INFO] saving model to models/lstm-epoch-{}-files-{}-{}-batch-{}-{}.h5".format(epoch, i, i+batch_size, batch_index, batch_index+arguments.lstmBatchSize))
        model.save('./models/lstm-epoch-{}-files-{}-{}-batch-{}-{}.h5'.format(epoch, i, i+batch_size, batch_index, batch_index+arguments.lstmBatchSize))
    else:
        print("[INFO] saving model to models/dnn-epoch-{}-files-{}-{}.h5".format(epoch, i, i+batch_size))
        model.save('./models/dnn-epoch-{}-files-{}-{}.h5'.format(epoch, i, i+batch_size))

def save_weights(i, epoch, batch_index=None):
    if not path.exists("checkpoints"):
        os.mkdir("checkpoints")

    if arguments.lstm:
        print("[INFO] saving weights to checkpoints/lstm-epoch-{}-files-{}-{}-batch-{}-{}".format(epoch, i, i+batch_size, batch_index, batch_index+arguments.lstmBatchSize))
        model.save_weights('./checkpoints/lstm-epoch-{}-files-{}-{}-batch-{}-{}'.format(epoch, i, i+batch_size, batch_index, batch_index+arguments.lstmBatchSize))
    else:
        print("[INFO] saving weights to checkpoints/dnn-epoch-{}-files-{}-{}".format(epoch, i, i+batch_size))
        model.save_weights('./checkpoints/dnn-epoch-{}-files-{}-{}'.format(epoch, i, i+batch_size))

def readCSV(f):
    print("[INFO] reading file", f)
    return pd.read_csv(f, delimiter=',', engine='c', encoding="utf-8-sig")

def run():
    leftover = None
    for epoch in range(arguments.epochs):

        print(colored("[INFO] epoch {}/{}".format(epoch+1, arguments.epochs), 'yellow'))
        for i in range(0, len(files), batch_size):

            print(colored("[INFO] loading file {}-{}/{} on epoch {}/{}".format(i+1, i+batch_size, len(files), epoch+1, arguments.epochs), 'yellow'))
            df_from_each_file = [readCSV(f) for f in files[i:(i+batch_size)]]

            # ValueError: The truth value of a DataFrame is ambiguous. Use a.empty, a.bool(), a.item(), a.any() or a.all().
            if leftover is not None:
                df_from_each_file.insert(0, leftover)

            print("[INFO] concatenate the files")
            df = pd.concat(df_from_each_file, ignore_index=True)

            # TODO move back into process_dataset?
            print("[INFO] process dataset, shape:", df.shape)
            if arguments.sample != None:
                if arguments.sample > 1.0:
                    print("invalid sample rate")
                    exit(1)

                if arguments.sample <= 0:
                    print("invalid sample rate")
                    exit(1)

            print("[INFO] sampling", arguments.sample)
            if arguments.sample < 1.0:
                df = df.sample(frac=arguments.sample, replace=False)

            if arguments.drop is not None:
                for col in arguments.drop.split(","):
                    drop_col(col, df)

            # Always drop columns that are unique for every record
#           drop_col('UID', df)

            # Tag is always 0, remove this column
#           drop_col('Tag', df)

            if not arguments.lstm:
                print("dropping all time related columns...")
                drop_col('unixtime', df)
#               drop_col('Timestamp', df)
#               drop_col('num', df)
#               drop_col('date', df)
#               drop_col('time', df)

#           drop_col('SessionID', df)

            print("[INFO] columns:", df.columns)

            print("[INFO] analyze dataset:", df.shape)
            analyze(df)

            if arguments.zscoreUnixtime:
               encode_numeric_zscore(df, "unixtime")

            if arguments.encodeColumns:
                print("[INFO] Shape when encoding dataset:", df.shape)
                encode_columns(df, arguments.resultColumn, arguments.lstm, arguments.debug)
                print("[INFO] Shape AFTER encoding dataset:", df.shape)

            if arguments.debug:
                print("--------------AFTER DROPPING COLUMNS ----------------")
                print("df.columns", df.columns, len(df.columns))
                with pd.option_context('display.max_rows', 10, 'display.max_columns', None):  # more options can be specified also
                    print(df)

            # we are batching the data also for the sequential dense layered dnn,
            # as we observed that smaller batch size increases prediction performance
            for batch_index in range(0, df.shape[0], arguments.lstmBatchSize):

                print("[INFO] processing batch {}-{}/{}".format(batch_index, batch_index+arguments.lstmBatchSize, df.shape[0]))

                dfCopy = df[batch_index:batch_index+arguments.lstmBatchSize]

                # skip leftover that does not reach batch size
                if len(dfCopy.index) != arguments.lstmBatchSize:
                    leftover = dfCopy
                    continue

                train_dnn(dfCopy, i, epoch+1, batch_index)
                leftover = None

# instantiate the parser
parser = argparse.ArgumentParser(description='NETCAP compatible implementation of Network Anomaly Detection with a Deep Neural Network and TensorFlow')

# add commandline flags
parser.add_argument('-read', required=True, type=str, help='Regex to find all labeled input CSV file to read from (required)')
parser.add_argument('-drop', type=str, help='optionally drop specified columns, supply multiple with comma')
parser.add_argument('-sample', type=float, default=1.0, help='optionally sample only a fraction of records')
parser.add_argument('-dropna', default=False, action='store_true', help='drop rows with missing values')
parser.add_argument('-testSize', type=float, default=0.2, help='specify size of the test data in percent (default: 0.25)')
parser.add_argument('-loss', type=str, default='categorical_crossentropy', help='set function (default: categorical_crossentropy)')
parser.add_argument('-optimizer', type=str, default='adam', help='set optimizer (default: adam)')
parser.add_argument('-resultColumn', type=str, default='classification', help='set name of the column with the prediction')
parser.add_argument('-features', type=int, required=True, help='The amount of columns in the csv (dimensionality)')
#parser.add_argument('-class_amount', type=int, default=2, help='The amount of classes e.g. normal, attack1, attack3 is 3')
parser.add_argument('-batchSize', type=int, default=1, help='The amount of files to be read in. (default: 1)')
parser.add_argument('-epochs', type=int, default=1, help='The amount of epochs. (default: 1)')
parser.add_argument('-numCoreLayers', type=int, default=1, help='set number of core layers to use')
parser.add_argument('-shuffle', default=False, help='shuffle data before feeding it to the DNN')
parser.add_argument('-dropoutLayer', default=False, help='insert a dropout layer at the end')
parser.add_argument('-coreLayerSize', type=int, default=4, help='size of an DNN core layer')
parser.add_argument('-wrapLayerSize', type=int, default=2, help='size of the first and last DNN layer')
parser.add_argument('-lstm', default=False, help='use a LSTM network')
parser.add_argument('-lstmBatchSize', type=int, default=100000, help='LSTM network input number of rows')
parser.add_argument('-debug', default=False, help='debug mode on off')
parser.add_argument('-zscoreUnixtime', default=False, help='apply zscore to unixtime column')
parser.add_argument('-encodeColumns', default=False, help='switch between auto encoding or using a fully encoded dataset')
parser.add_argument('-classes', type=str, help='supply one or multiple comma separated class identifiers')
parser.add_argument('-saveModel', default=False, help='save model (if false, only the weights will be saved)')

# parse commandline arguments
arguments = parser.parse_args()
if arguments.read is None:
    print("[INFO] need an input file / multi file regex. use the -read flag")
    exit(1)

if arguments.classes is not None:
    classes = arguments.classes.split(',')
    print("set classes to:", classes)

print("Date:", datetime.datetime.now())

# get all files
files = glob(arguments.read)
files.sort()

if len(files) == 0:
    print("[INFO] no files matched")
    exit(1)

# set batch size
batch_size = arguments.batchSize

# create models
model = create_dnn(
    arguments.features, 
    len(classes), 
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

