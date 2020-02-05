import argparse
import os
import os.path
import sys
import pandas as pd
import joblib
import json

import unittest

# Find the first file that matches the pattern.


def find_file(suffix):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    for file in os.listdir(current_dir):
        if file.endswith(suffix):
            filename = file
            return os.path.join(current_dir, filename)

    return None


def load_var_names(filename):
    var_file = find_file(filename)
    if var_file is None:
        return None
    if os.path.isfile(var_file):
        with open(var_file) as f:
            json_object = json.load(f)

        names = []
        for row in json_object:
            names.append(row["name"])
        return names
    else:
        print('Didnot find file: ', filename)
        return None


def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3


def load_data_by_input_vars(data):
    names = load_var_names('inputVar.json')
    if names is None:
        return data
    else:
        newcolumns = intersection(list(data.columns), names)
        return data[newcolumns]


def run(model_file, input_file, output_file):

    if model_file is None:
        print('Not found Python pickle file!')
        sys.exit()

    if not os.path.isfile(input_file):
        print('Not found input file', input_file)
        sys.exit()

    inputDf = pd.read_csv(input_file).fillna(0)

    output_vars = load_var_names('outputVar.json')

    in_dataf = load_data_by_input_vars(inputDf)

    model = open(model_file, 'rb')
    rfor = joblib.load(model)
    model.close()

    outputDf = pd.DataFrame(rfor.predict_proba(in_dataf))

    if output_vars is None:
        outputcols = map(lambda x: 'P_' + str(x), list(rfor.classes_))
    else:
        outputcols = map(lambda x: output_vars[x], list(rfor.classes_))
    outputDf.columns = outputcols

    # merge with input data
    outputDf = pd.merge(inputDf, outputDf, how='inner',
                        left_index=True, right_index=True)

    # print('printing first few lines...')
    # print(outputDf.head())
    outputDf.to_csv(output_file, sep=',', index=False)
    return outputDf.to_dict()


def main():
    # parse arguments
    parser = argparse.ArgumentParser(description='Score')
    parser.add_argument('-m', dest="modelFile",
                        help='model file name, the default is the first PKL file that is found in the directory')
    parser.add_argument('-i', dest="scoreInputCSV",
                        required=True, help='input filename')
    parser.add_argument('-o', dest="scoreOutputCSV",
                        required=True, help='output csv filename')

    args = parser.parse_args()
    model_file = args.modelFile
    input_file = args.scoreInputCSV
    output_file = args.scoreOutputCSV

    # Search for the first PKL file in the directory if argument is not specified.
    if model_file is None:
        for file in os.listdir("."):
            if file.endswith(".pickle"):
                model_file = file
                break

    result = run(model_file, input_file, output_file)
    return 0

class ScoringTest(unittest.TestCase):

    def setUp(self):
        self.model = sys.argv[1]
        self.input = sys.argv[2]
        self.output = sys.argv[3]

    def runTest_dictionary(self):

        '''
        Unit test #1 for the type : dictionary
        '''
        # print(".Running Test to check if the function generate a dictionary...")
        self.assertIsInstance(run(self.model, self.input, self.output), dict)

    def runTest_content(self):

        '''
        Unit test #2 for the content: Not Empty
        '''
        # print("Running Test to check if the function generate a non-empty dictionary...")
        self.assertTrue(bool(run(self.model, self.input, self.output)))

    def runTest_score(self):

        '''
        Unit test #3 for the score: Dicts Equality
        '''
        
        outdict = {'BAD': {0: 1}, 'LOAN': {0: 1100}, 'MORTDUE': {0: 25860}, 'VALUE': {0: 39025}, 'REASON': {0: 'HomeImp'},
                    'JOB': {0: 'Other'}, 'YOJ': {0: 10.5}, 'DEROG': {0: 0}, 'DELINQ': {0: 0}, 'CLAGE': {0: 94.3666666666667}, 'NINQ': {0: 1},
                    'CLNO': {0: 9}, 'DEBTINC': {0: 0.0}, 'P_BAD0': {0: 1.2}, 'P_BAD1': {0: 0.0}}

        # print("Running Test to check if the function score data correctly...")
        self.assertDictEqual(run(self.model, self.input, self.output), outdict)
        

if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(ScoringTest('runTest_dictionary'))
    suite.addTest(ScoringTest('runTest_content'))
    suite.addTest(ScoringTest('runTest_score'))
    out = unittest.TextTestRunner(sys.stdout, verbosity=3).run(suite)

    def outcheck(outls):
        if len(outls.errors) >= 1 or len(outls.failures) >= 1:
            return 1
        else:
            return 0

    sys.exit(outcheck(out))