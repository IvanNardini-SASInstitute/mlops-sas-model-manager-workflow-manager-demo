import argparse
import os
import os.path
import sys
import pandas as pd
import numpy as np
import joblib
        
# parse arguments
parser = argparse.ArgumentParser(description='Score')
parser.add_argument('-m', dest="modelFile", help='model filename, default will be the first pkl file found in the directory')
parser.add_argument('-i', dest="scoreInputCSV", required=True, help='input filename')
parser.add_argument('-o', dest="scoreOutputCSV", required=True, help='output csv filename')

args = parser.parse_args()
modelFile = args.modelFile
scoreInputCSV = args.scoreInputCSV
scoreOutputCSV = args.scoreOutputCSV

#modelFile = 'dtree.pkl'
#scoreInputCSV = 'hmeq.csv'
#scoreOutputCSV = 'scoreOut.csv'

#search for the first pkl file in the directory if argument is not given
if modelFile == None:
    for file in os.listdir("."):
        if file.endswith(".pickle"):
            modelFile = file
            break

if modelFile == None:
    print('Not found Python pickle file!')
    sys.exit()
    
if not os.path.isfile(scoreInputCSV):
    print('Not found input file',scoreInputCSV)
    sys.exit()
    
inputDf = pd.read_csv(scoreInputCSV)

targetVars = ['BAD']
inVars = ['LOAN', 'MORTDUE', 'VALUE', 'YOJ', 'DEROG', 'DELINQ', 'CLAGE', 'NINQ', 'CLNO', 'DEBTINC']

model = open(modelFile, 'rb')
rfor = joblib.load(model)
model.close()

outputDf = pd.DataFrame(rfor.predict_proba(inputDf[inVars]))

outputcols = map(lambda x:'P_BAD' + str(x) ,list(rfor.classes_))
outputDf.columns = outputcols

#merge with input data
outputDf = pd.merge(inputDf,outputDf,how='inner',left_index=True,right_index=True)

#print(outputDf.head())

outputDf.to_csv(scoreOutputCSV,sep=',',index=False)
