import argparse
import os
import os.path
import sys
import pandas as pd
import joblib
import json

import unitest

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

    print('printing first few lines...')
    print(outputDf.head())
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

# class ScoringTest(unittest.TestCase):

#     def setUp(self):
#         # Model pickle
#         self.model = sys.argv[1]
#         # Input CSV
#         self.inputCSV = sys.argv[2]
#         # Output CSV
#         self.outputCSV = sys.argv[3]
    
#     def runTest(self):
#         self.assertEqual()


if __name__ == "__main__":
    sys.exit(main())


# class Test(unittest.TestCase):
#     def scoretest(self):
#         self.assertEqual(computeScore(1100,25680,39025,10.5,0,0,94.36667,1,9,34,0,1,1)
# , (0.997854340629609, 0.0021456593703910176))

# if __name__ == '__main__':
#     unittest.main()

# def computeScore(LOAN, MORTDUE, VALUE, YOJ, DEROG, DELINQ, CLAGE, NINQ, CLNO, DEBTINC, Office, Other, HomeImp):
#     "Output: P_BAD1, P_BAD0"

#     modelFile = os.getcwd() + 'model/gboost_obj_3_6_1.pkl'
#     model = open(modelFile, 'rb')
#     dtree = pickle.load(model)
#     model.close()

#     input_list=[LOAN, MORTDUE, VALUE, YOJ, DEROG, DELINQ, CLAGE, NINQ, CLNO, DEBTINC, Office, Other, HomeImp]

#     # Just to make sure there's no None value in the data
#     # convert any of None to 0 if any
#     converted = [0 if v is None else v for v in input_list]

#     prob = dtree.predict_proba([converted])

#     P_BAD0 = prob[0,0]
#     P_BAD1 = prob[0,1]
#     #print("Probability of defaulting is " + str(P_BAD1) + ", while not defaulting is " + str(P_BAD0))

#     return P_BAD1, P_BAD0

# class Test(unittest.TestCase):
#     def test(self):
#         self.assertEqual(computeScore(1100,25680,39025,10.5,0,0,94.36667,1,9,34,0,1,1)
# , (0.997854340629609, 0.0021456593703910176))

# if __name__ == '__main__':
#     unittest.main()
