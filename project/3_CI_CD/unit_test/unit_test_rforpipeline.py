import argparse
import os
import os.path
import pandas as pd
import sys
import pandas as pd
import joblib

import unittest

# parse arguments
parser = argparse.ArgumentParser(description='Score')
parser.add_argument('-m', dest="modelFile",
                    help='model filename, default will be the first pkl file found in the directory')
parser.add_argument('-i', dest="scoreInputCSV",
                    required=True, help='input filename')
parser.add_argument('-o', dest="scoreOutputCSV",
                    required=True, help='output csv filename')

args = parser.parse_args()
modelFile = args.modelFile
scoreInputCSV = args.scoreInputCSV
scoreOutputCSV = args.scoreOutputCSV

# search for the first pkl file in the directory if argument is not given
if modelFile == None:
    for file in os.listdir("."):
        if file.endswith(".pickle"):
            modelFile = file
            break

if modelFile == None:
    print('Not found Python pickle file!')
    sys.exit()

if not os.path.isfile(scoreInputCSV):
    print('Not found input file', scoreInputCSV)
    sys.exit()

inputDf = pd.read_csv(scoreInputCSV)

targetVars = ['BAD']
inVars = ['LOAN', 'MORTDUE', 'VALUE', 'YOJ', 'DEROG',
          'DELINQ', 'CLAGE', 'NINQ', 'CLNO', 'DEBTINC']

model = open(modelFile, 'rb')
rfor = joblib.load(model)
model.close()

outputDf = pd.DataFrame(rfor.predict_proba(inputDf[inVars]))

outputcols = map(lambda x: 'P_BAD' + str(x), list(rfor.classes_))
outputDf.columns = outputcols

# merge with input data
outputDf = pd.merge(inputDf, outputDf, how='inner',
                    left_index=True, right_index=True)

outputDf.to_csv(scoreOutputCSV, sep=',', index=False)


def computeScore(LOAN, MORTDUE, VALUE, YOJ, DEROG, DELINQ, CLAGE, NINQ, CLNO, DEBTINC, Office, Other, HomeImp):
    "Output: P_BAD1, P_BAD0"

    modelFile = os.getcwd() + 'model/gboost_obj_3_6_1.pkl'
    model = open(modelFile, 'rb')
    dtree = pickle.load(model)
    model.close()

    input_list=[LOAN, MORTDUE, VALUE, YOJ, DEROG, DELINQ, CLAGE, NINQ, CLNO, DEBTINC, Office, Other, HomeImp]

    # Just to make sure there's no None value in the data
    # convert any of None to 0 if any
    converted = [0 if v is None else v for v in input_list]

    prob = dtree.predict_proba([converted])

    P_BAD0 = prob[0,0]
    P_BAD1 = prob[0,1]
    #print("Probability of defaulting is " + str(P_BAD1) + ", while not defaulting is " + str(P_BAD0))

    return P_BAD1, P_BAD0

class Test(unittest.TestCase):
    def test(self):
        self.assertEqual(computeScore(1100,25680,39025,10.5,0,0,94.36667,1,9,34,0,1,1)
, (0.997854340629609, 0.0021456593703910176))

if __name__ == '__main__':
    unittest.main()
