#!/usr/bin/python3

# only works for 1 epoch

from sklearn.model_selection import train_test_split
import argparse
import pandas as pd
from glob import glob
from tfUtils import * 
import keras
from keras.models import Sequential
from keras.layers.core import Dense, Activation
from keras.callbacks import EarlyStopping



monitor = EarlyStopping(
    monitor='val_loss', 
    min_delta=1e-3, 
    patience=5, 
    verbose=1, 
    mode='auto'
)

METRICS = [ 
    keras.metrics.TruePositives(name='tp'), 
    keras.metrics.FalsePositives(name='fp'), 
    keras.metrics.TrueNegatives(name='tn'), 
    keras.metrics.FalseNegatives(name='fn'),  
    keras.metrics.BinaryAccuracy(name='accuracy'), 
    keras.metrics.Precision(name='precision'), 
    keras.metrics.Recall(name='recall'), 
    keras.metrics.AUC(name='auc'), 
]


#instantiate the parser
parser = argparse.ArgumentParser(description='NETCAP compatible implementation of Network Anomaly Detection with a Deep Neural Network and TensorFlow')

# add commandline flags
parser.add_argument('-read', required=True, type=str, help='Regex to find all labeled input CSV file to read from (required)')
parser.add_argument('-drop', type=str, help='optionally drop specified columns, supply multiple with comma')
parser.add_argument('-sample', type=float, nargs='?', help='optionally sample only a fraction of records')
parser.add_argument('-dropna', default=False, action='store_true', help='drop rows with missing values')
parser.add_argument('-test_size', type=float, default=0.25, help='specify size of the test data in percent (default: 0.25)')
parser.add_argument('-loss', type=str, default='categorical_crossentropy', help='set function (default: categorical_crossentropy)')
parser.add_argument('-optimizer', type=str, default='adam', help='set optimizer (default: adam)')
parser.add_argument('-result_column', type=str, default='Normal/Attack', help='set name of the column with the prediction')
parser.add_argument('-dimensionality', type=int, required=True, help='The amount of columns in the csv')
parser.add_argument('-class_amount', type=int, required=True, help='The amount of classes e.g. normal, attack1, attack3 is 3')
parser.add_argument('-batch_size', type=int, default=1, help='The amount of files to be read in. (default: 1)')
parser.add_argument('-epochs', type=int, default=1, help='The amount of epochs. (default: 1)')


## parse commandline arguments
arguments = parser.parse_args()
if arguments.read == None:
    print("[INFO] need an input file. use the -r flag")
    exit(1)

files = glob(arguments.read)
files.sort()

#x_input = 19
#y_amount = 2
batch_size = arguments.batch_size

model = create_dnn(arguments.dimensionality, arguments.class_amount, arguments.loss, arguments.optimizer)
print("[INFO] Created DNN now running the training")
for epoch in range(arguments.epochs):
    print("[INFO] epoch {}/{}".format(epoch, arguments.epochs))
    for i in range(0,len(files),batch_size):
        print("[INFO] loading in the files {}-{}".format(i, i+batch_size))
        df_from_each_file = (pd.read_csv(f, delimiter=',', engine='c', encoding="utf-8-sig") for f in files[i:(i+batch_size)])
        print("[INFO] concatenate the files")
        df = pd.concat(df_from_each_file, ignore_index=True)
        print("[INFO] Process dataset")
        process_dataset(df, arguments.sample, arguments.drop)
        print("[INFO] analyze dataset")
        analyze(df)
        encode_columns(df, arguments.result_column)
        print("[INFO] breaking into predictors and prediction...")
         
        # Break into X (predictors) & y (prediction)
        x, y = to_xy(df, arguments.result_column)
        print("[INFO] creating train/test split")
        
        # Create a test/train split.
        # by default, 25% of data is used for testing
        # it can be configured using the test_size commandline flag
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=arguments.test_size, random_state=42)  
        model.fit(x_train,y_train,validation_data=(x_test,y_test), callbacks=[monitor], verbose=2, epochs=1,batch_size=32)
        model.save_weights('./checkpoints/epoch-{}-files-{}-{}'.format(1,i,i+batch_size))




# useful comments
# set input size of dnn
# set batch size
# number of amount of files read in cofigurable
# unzip actual data
# and try for 1 epoch?
    # concat 2 files.



# write down how go program would preprocess program?kkkk
