"""
As the first argument give a regex where the output files from the experiments is found with.

example:
python3 scripts/create_stats.py -read experiment-logs/multi-dnn-v0-physical-zscore.log -filelines="-4,-2" -classes="normal,attack"
python3 scripts/create_stats.py -read experiment-logs/dnn-v3.log
"""
import argparse
import re
from ast import literal_eval

from glob import glob
import numpy as np
import sys

# The attack classes as found in score.py and train.py
classes = ["normal", "Single Stage Single Point", "Single Stage Multi Point", "Multi Stage Single Point", "Multi Stage Multi Point"]
#classes = ["Normal", "Attack"]


# instantiate the parser
parser = argparse.ArgumentParser(description='NETCAP compatible implementation of Network Anomaly Detection with a Deep Neural Network and TensorFlow')

# add commandline flags
parser.add_argument('-read', required=True, type=str, help='Regex to find all labeled input CSV file to read from (required)')
parser.add_argument('-classes', type=str, help='supply one or multiple comma separated class identifiers')
parser.add_argument('-filelines', type=str, default='-6,-1', help='The lines to grap from the files. default 6,1')

# parse commandline arguments
arguments = parser.parse_args()


if arguments.classes is not None:
    classes = arguments.classes.split(',')
    print("set classes to:", classes)


files = glob(arguments.read)

# Loop through all of the files and calculate the statistics for all final confusion matrices
for file_name in files:
    print("--- {} ---".format(file_name))

    # Read in the file into memory and save the last 5 lines that contain the array
    fp = open(file_name,"r")
    lines = fp.readlines()
    fp.close()
    print("lines to cut",tuple(map(int, arguments.filelines.split(','))))
    array_line_nr = slice(*tuple(map(int, arguments.filelines.split(','))) )
    array = "".join(lines[array_line_nr])
    #array = "".join(lines[-4:-2])
    array = re.sub('\[\s+', '[', array)
    array = re.sub('\s+', ',', array)
    array = re.sub('\]\],', ']]', array)
    
    array = np.array(literal_eval(array))
    tpsum = 0
    
    print(array)
    print()
    print("{:<30} precision   recall   f1-score".format("name"))
    for i,j in enumerate(classes):
        tp = array[i,i]
        tpsum+=tp
    
        if tp > 0:
            recall = array[i,i]/np.sum(array[i]) 
            precision = array[i,i]/np.sum(array[:,i]) 
            f1_score = 2* (precision * recall) / (precision+recall)
            print("{:<30}     {:.3f}    {:.3f}      {:.3f}".format(j,precision,recall,f1_score))
        else: 
            print("{:<30}     zero tp".format(j))
    
    print("accuracy: {:.3f}\n".format(tpsum/np.sum(array)))

