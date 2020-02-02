"""
As the first argument give a regex where the output files from the experiments is found with.
"""

import re
from ast import literal_eval

from glob import glob
import numpy as np
import sys

# The attack classes as found in score.py and train.py
classes = ["normal", "Single Stage Single Point", "Single Stage Multi Point", "Multi Stage Single Point", "Multi Stage Multi Point"]

files = glob(sys.argv[1])

# Loop through all of the files and calculate the statistics for all final confusion matrices
for file_name in files:
    print("--- {} ---".format(file_name))

    # Read in the file into memory and save the last 5 lines that contain the array
    fp = open(file_name,"r")
    lines = fp.readlines()
    fp.close()
    array = "".join(lines[-5:])
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

