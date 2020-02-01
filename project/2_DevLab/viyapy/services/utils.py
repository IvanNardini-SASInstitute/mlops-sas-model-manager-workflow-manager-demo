## These utilities are used for the EYAP demo

import csv
import os
import sys
import json
import inflection
import csv
import swat
import glob
import pprint

import numpy as np
import pandas as pd
import sklearn.metrics as metrics
from scipy.stats import gamma
from scipy.stats import kendalltau
from math import sqrt

from ..exceptions import ViyaException

import logging
logger = logging.getLogger(__name__)

def create_metadata(project, model, content_list, definition):
    metadata = {
        'projectId': definition.projectId,
        'projectName': project.Name,
        'modelId': model.Id,
        'modelName': model.Name,
        'taskId': definition.Id,
        'scoreCodeId': content_list[2].id,
        'contentId': content_list[3].id,
        'targetVariable': project.targetVariable,
        'targetEventValue': project.targetEventValue,
        'nonEventValue': project.classTargetValues.replace(project.targetEventValue+',',""),
        'inputVariables': ', '.join(definition.inputVariables),
        'outputVariables': ', '.join(definition.outputVariables),
        'modelDisplayName': model.Name,
        'dataPrefix': definition.dataPrefix,
        'sequence': '',
        'timeValue': ''
        }
    return metadata

def create_metadata_csv(project, model, content_list, definition, path=os.getcwd(), filename='model_metadata'):
    metadata = create_metadata(project, model, content_list, definition)
    with open(path+'/'+filename+".csv",'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(metadata.keys())
        w.writerow(metadata.values())
    return print('Metadata file %s created successfully!' % (filename) )

def create_requirements_file(package_list=[], path=os.getcwd(), file='requirements.txt'):
    with open(path+'/'+file, 'w') as fp:
        for package_name in package_list:
            exec("import {module}".format(module=package_name))
            package = sys.modules[package_name]
            if package_name == 'sklearn':
                package_name = 'scikit-learn'
            fp.writelines([
                package_name+'==%s\n' % package.__version__,
                      ])
    with open (path+'/'+file, 'r') as fp:
        print(fp.read())
    if not package_list:
        print('Please provide a list of packages.')
        
def generate_lift(targetvar_train, targetvar_test, targetname, eventvalue, y_pred_train, y_pred_test, outdir, debug=False):

    # Find out the number of observations
    nObs_train = len(targetvar_train)
    nObs_test = len(targetvar_test)

    SAMPLES = ('TRAIN', 'TEST')
    nObs = (nObs_train, nObs_test)
    target_vars = (targetvar_train, targetvar_test)
    EventPredProbabilities = (y_pred_train, y_pred_test)

    #Template stats dictionaries
    _dict_DataRole_ = {'parameter': '_DataRole_', 'type': 'char', 'label': 'Data Role',
                       'length': 10, 'order': 1, 'values': ['_DataRole_'], 'preformatted': False}

    _dict_PartInd_ = {'parameter': '_PartInd_', 'type': 'num', 'label': 'Partition Indicator',
                      'length': 8, 'order': 2, 'values': ['_PartInd_'], 'preformatted': False}

    _dict_PartInd__f = {'parameter': '_PartInd__f', 'type': 'char', 'label': 'Formatted Partition',
                        'length': 12, 'order': 3, 'values': ['_PartInd__f'], 'preformatted': False}

    _dict_Column_ = {'parameter': '_Column_', 'type': 'char', 'label': 'Analysis Variable',
                     'length': 32, 'order': 4, 'values': ['_Column_'], 'preformatted': False}

    _dict_Event_ = {'parameter': '_Event_', 'type': 'char', 'label': 'Event',
                    'length': 8, 'order': 5, 'values': ['_Event_'], 'preformatted': False}

    _dict_Depth_ = {'parameter': '_Depth_', 'type': 'num', 'label': 'Depth',
                    'length': 8, 'order': 7, 'values': ['_Depth_'], 'preformatted': False}

    _dict_NObs_ = {'parameter': '_NObs_', 'type': 'num', 'label': 'Sum of Frequencies',
                   'length': 8, 'order': 8, 'values': ['_NObs_'], 'preformatted': False}

    _dict_Gain_ = {'parameter': '_Gain_', 'type': 'num', 'label': 'Gain',
                   'length': 8, 'order': 9, 'values': ['_Gain_'], 'preformatted': False}

    _dict_Resp_ = {'parameter': '_Resp_', 'type': 'num', 'label': '% Captured Response',
                   'length': 8, 'order': 10, 'values': ['_Resp_'], 'preformatted': False}

    _dict_CumResp_ = {'parameter': '_CumResp_', 'type': 'num', 'label': 'Cumulative % Captured Response',
                      'length': 8, 'order': 11, 'values': ['_CumResp_'], 'preformatted': False}

    _dict_PctResp_ = {'parameter': '_PctResp_', 'type': 'num', 'label': '% Response',
                      'length': 8, 'order': 12, 'values': ['_PctResp_'], 'preformatted': False}

    _dict_CumPctResp_ = {'parameter': '_CumPctResp_', 'type': 'num', 'label': 'Cumulative % Response',
                         'length': 8, 'order': 13, 'values': ['_CumPctResp_'], 'preformatted': False}

    _dict_Lift_ = {'parameter': '_Lift_', 'type': 'num', 'label': 'Lift',
                   'length': 8, 'order': 14, 'values': ['_Lift_'], 'preformatted': False}

    _dict_CumLift_ = {'parameter': '_CumLift_', 'type': 'num', 'label': 'Cumulative Lift',
                      'length': 8, 'order': 15, 'values': ['_CumLift_'], 'preformatted': False}

    parameterMap = {'_DataRole_': _dict_DataRole_, '_PartInd_': _dict_PartInd_, '_PartInd__f': _dict_PartInd__f,
                    '_Column_': _dict_Column_, '_Event_': _dict_Event_, '_Depth_': _dict_Depth_,
                    '_NObs_': _dict_NObs_, '_Gain_': _dict_Gain_, '_Resp_': _dict_Resp_,
                    '_CumResp_': _dict_CumResp_,
                    '_PctResp_': _dict_PctResp_, '_CumPctResp_': _dict_CumPctResp_,
                    '_Lift_': _dict_Lift_, '_CumLift_': _dict_CumLift_}

    Lift_accLift_coordinates = {}

    bins = np.arange(0, 100, 10)

    for sample, nobs, trgvar, event_probability in zip(SAMPLES, nObs, target_vars, EventPredProbabilities):

        Lift_accLift_coordinates[sample] = {}

        # Get the quantiles
        quantileCutOff = np.percentile(event_probability, bins)
        nQuantile = len(quantileCutOff)
        quantileIndex = np.zeros(nobs)

        for i in range(nobs):
            iQ = nQuantile
            EPP = event_probability[i]
            for j in range(nQuantile):
                if (EPP > quantileCutOff[-j]):
                    iQ -= 1
            quantileIndex[i] = iQ

        # #       Construct the Lift chart table
        countTable = pd.crosstab(quantileIndex, trgvar[targetname])
        decileN = countTable.sum(eventvalue)
        decilePct = 100 * (decileN / nobs)
        gainN = countTable[eventvalue]
        totalNResponse = gainN.sum(0)
        gainPct = 100 * (gainN / totalNResponse)
        responsePct = 100 * (gainN / decileN)
        overallResponsePct = 100 * (totalNResponse / nobs)
        lift = responsePct / overallResponsePct

        LiftCoordinates = pd.concat([decileN, decilePct, gainN, gainPct, responsePct, lift],
                                    axis=1, ignore_index=True)

        LiftCoordinates = LiftCoordinates.rename({0: 'Decile N',
                                                  1: 'Decile %',
                                                  2: 'Gain N',
                                                  3: 'Gain %',
                                                  4: 'Response %',
                                                  5: 'Lift'}, axis='columns')

        Lift_accLift_coordinates[sample]['Lift'] = LiftCoordinates.to_dict()

        #       Construct the Accumulative Lift chart table
        accCountTable = countTable.cumsum(axis=0)
        decileN = accCountTable.sum(1)
        decilePct = 100 * (decileN / nobs)
        gainN = accCountTable[eventvalue]
        gainPct = 100 * (gainN / totalNResponse)
        responsePct = 100 * (gainN / decileN)
        lift = responsePct / overallResponsePct

        accLiftCoordinates = pd.concat([decileN, decilePct, gainN, gainPct, responsePct, lift],
                                       axis=1, ignore_index=True)
        accLiftCoordinates = accLiftCoordinates.rename({0: 'Acc. Decile N',
                                                        1: 'Acc. Decile %',
                                                        2: 'Acc. Gain N',
                                                        3: 'Acc. Gain %',
                                                        4: 'Acc. Response %',
                                                        5: 'Acc. Lift'}, axis='columns')

        Lift_accLift_coordinates[sample]['Accumulate_Lift'] = accLiftCoordinates.to_dict()

        #         if (debug == True):
        #             pprint.pprint(Lift_accLift_coordinates)

        irow = 0
        sampleidx = 1
        _dict_lift_ = {}
        _list_lift_ = []

    for SAMPLE, dicStats in Lift_accLift_coordinates.items():

        n_rows = list(dicStats['Lift']['Decile N'].keys())

        for rowidx in n_rows:
            decileN = dicStats['Lift']['Decile N'][rowidx]
            gainN = dicStats['Lift']['Gain N'][rowidx]
            gainPct = dicStats['Lift']['Gain %'][rowidx]
            responsePct = dicStats['Lift']['Response %'][rowidx]
            lift = dicStats['Lift']['Lift'][rowidx]
            acc_decilePct = dicStats['Accumulate_Lift']['Acc. Decile %'][rowidx]
            acc_gainPct = dicStats['Accumulate_Lift']['Acc. Gain %'][rowidx]
            acc_responsePct = dicStats['Accumulate_Lift']['Acc. Response %'][rowidx]
            acc_lift = dicStats['Accumulate_Lift']['Acc. Lift'][rowidx]

            irow +=1

            _dict_stat = {}
            _dict_stat.update(_DataRole_=SAMPLE)
            _dict_stat.update(_PartInd_=sampleidx)
            _dict_stat.update(_PartInd__f='           {}'.format(sampleidx))
            _dict_stat.update(_Column_=targetname)
            _dict_stat.update(_Event_=str(eventvalue))
            _dict_stat.update(_Depth_=acc_decilePct)
            _dict_stat.update(_NObs_=decileN)
            _dict_stat.update(_Gain_=gainN)
            _dict_stat.update(_Resp_=gainPct)
            _dict_stat.update(_CumResp_=acc_gainPct)
            _dict_stat.update(_PctResp_=responsePct)
            _dict_stat.update(_CumPctResp_=acc_responsePct)
            _dict_stat.update(_Lift_=lift)
            _dict_stat.update(_CumLift_=acc_lift)

            _dict_lift_.update(dataMap=_dict_stat, rowNumber=irow)
            _list_lift_.append(dict(_dict_lift_))

        sampleidx += 1

    outJSON = {'name': 'dmcas_lift',
               'revision': 0,
               'order': 0,
               'parameterMap': parameterMap,
               'data': _list_lift_,
               'version': 1,
               'xInteger': False,
               'yInteger': False}

    if (debug == True):
        pprint.pprint(Lift_accLift_coordinates)

    jFile = open(outdir + '/dmcas_lift.json', 'w')
    json.dump(outJSON, jFile, indent=4, skipkeys=True)
    jFile.close()
    
def generate_roc(targetvar_train, targetvar_test, targetname, eventvalue, y_pred_train, y_pred_test, outdir, debug=False):
    
    SAMPLES = ('TRAIN', 'TEST')
    target_vars = (targetvar_train, targetvar_test)
    EventPredProbabilities = (y_pred_train, y_pred_test)

    _dict_DataRole_ = {'parameter': '_DataRole_', 'type': 'char', 'label': 'Data Role',
                       'length': 10, 'order': 1, 'values': ['_DataRole_'], 'preformatted': False}

    _dict_PartInd_ = {'parameter': '_PartInd_', 'type': 'num', 'label': 'Partition Indicator',
                      'length': 8, 'order': 2, 'values': ['_PartInd_'], 'preformatted': False}

    _dict_PartInd__f = {'parameter': '_PartInd__f', 'type': 'char', 'label': 'Formatted Partition',
                        'length': 12, 'order': 3, 'values': ['_PartInd__f'], 'preformatted': False}

    _dict_Column_ = {'parameter': '_Column_', 'type': 'num', 'label': 'Analysis Variable',
                   'length': 32, 'order': 4, 'values': ['_Column_'], 'preformatted': False}

    _dict_Event_ = {'parameter' : '_Event_', 'type' : 'char', 'label' : 'Event',
                    'length' : 8, 'order' : 5, 'values' : [ '_Event_' ], 'preformatted' : False}

    _dict_Cutoff_ = {'parameter' : '_Cutoff_', 'type' : 'num', 'label' : 'Cutoff',
                     'length' : 8, 'order' : 6, 'values' : [ '_Cutoff_' ], 'preformatted' : False}

    _dict_Sensitivity_ = {'parameter' : '_Sensitivity_', 'type' : 'num', 'label' : 'Sensitivity',
                          'length' : 8, 'order' : 7, 'values' : [ '_Sensitivity_' ], 'preformatted' : False}

    _dict_Specificity_ = {'parameter' : '_Specificity_', 'type' : 'num', 'label' : 'Specificity',
                          'length' : 8, 'order' : 8, 'values' : [ '_Specificity_' ], 'preformatted' : False}

    _dict_FPR_ = {'parameter' : '_FPR_', 'type' : 'num', 'label' : 'False Positive Rate',
                  'length' : 8, 'order' : 9, 'values' : [ '_FPR_' ], 'preformatted' : False}

    _dict_OneMinusSpecificity_ = {'parameter' : '_OneMinusSpecificity_', 'type' : 'num', 'label' : '1 - Specificity',
                                  'length' : 8, 'order' : 10, 'values' : [ '_OneMinusSpecificity_' ], 'preformatted' : False}

    parameterMap = {'_DataRole_': _dict_DataRole_, '_PartInd_': _dict_PartInd_, '_PartInd__f':  _dict_PartInd__f,
                    '_Column_': _dict_Column_, '_Event_': _dict_Event_, '_Cutoff_': _dict_Cutoff_,
                    '_Sensitivity_': _dict_Sensitivity_, '_Specificity_': _dict_Specificity_,
                    '_FPR_': _dict_FPR_, '_OneMinusSpecificity_': _dict_OneMinusSpecificity_}

    roc_dict = {}

    for sample, trgvar, event_probability in zip(SAMPLES, target_vars, EventPredProbabilities):

        roc_dict[sample] = {}

        # Get coordinates of the ROC curves
        fpr, tpr, threshold = metrics.roc_curve(trgvar, event_probability, pos_label = eventvalue)

        roc_dataframe = pd.DataFrame({'fpr': fpr, 'tpr': tpr, 'threshold': np.minimum(1.0, np.maximum(0.0, threshold))})

        roc_dict[sample] = roc_dataframe.to_dict()

    
    _list_roc_ = []
    irow = 0
    sampleidx = 1
    
    for sample, dicStats in roc_dict.items():

        n_rows = list(roc_dict[sample]['fpr'].keys())
        
        for rowidx in n_rows:
        
            fpr = dicStats['fpr'][rowidx]
            tpr = dicStats['tpr'][rowidx]
            threshold = dicStats['threshold'][rowidx]
            irow += 1
            
            _dict_roc_ = {}

            _dict_stat = {}
            _dict_stat.update(_DataRole_ = sample)
            _dict_stat.update(_PartInd_ = sampleidx)
            _dict_stat.update(_PartInd__f = '           1')
            _dict_stat.update(_Column_ = targetname)
            _dict_stat.update(_Event_ = str(eventvalue))
            _dict_stat.update(_Cutoff_ = threshold)
            _dict_stat.update(_Sensitivity_ = tpr)
            _dict_stat.update(_Specificity_ = (1.0 - fpr))
            _dict_stat.update(_FPR_ = fpr)
            _dict_stat.update(_OneMinusSpecificity_ = fpr)

            _dict_roc_.update(dataMap = _dict_stat, rowNumber = irow)
            
            _list_roc_.append(dict(_dict_roc_))
        
        sampleidx +=1
        
    outJSON = {'name' : 'dmcas_roc',
       'revision' : 0,
       'order' : 0,
       'parameterMap' : parameterMap,
       'data' : _list_roc_,
       'version' : 1,
       'xInteger' : False,
       'yInteger' : False}
    
    jFile = open(outdir + '/dmcas_roc.json', 'w')
    json.dump(outJSON, jFile, indent=4, skipkeys=True)
    jFile.close()

def generate_inputvar(traindf, targetname, outdir, debug=False):

    """
    A Model managment function for generating inputVar json file

    Parameters
    ----------
    traindf : pandas DataFrame
        The Analytical Business Table with all inputs and target variable
    target : str
        The name of Target variable
    outdir : path
        The path of output directory

    Raises
    ------
    ValueError
        Unable to identify compatible metadata
    Exception
        You don't pass the right arguments. Check their types

    Return
    -------
        inputVar json file

    """

    if isinstance(traindf, pd.DataFrame) and isinstance(targetname, str):

        dpvars = traindf.columns.difference([targetname]).tolist()

        file = []

        for varidx in dpvars:

            try:

                variable = traindf[varidx]

                # Metadata information Base

                varname = varidx
                varrole = 'input'
                vartype = variable.dtypes.name
                # varlevel = ''

                first_value = variable.loc[variable.first_valid_index()]
                numericstate = pd.api.types.is_numeric_dtype(first_value)
                stringstate = pd.api.types.is_string_dtype(first_value)

                if (debug):
                    print(20 * '-')
                    print('{} metadata profile'.format(varname))
                    print(20 * '-')

                    print(varname)
                    print(varrole)
                    print(vartype)
                    # print(varlevel)
                    print(numericstate)
                    print(stringstate)

                if (numericstate):

                    if (vartype == 'category'):
                        outvarlevel = 'nominal'
                    else:
                        outvarlevel = 'interval'

                    outvartype = 'decimal'
                    outvarlen = 8

                elif (stringstate):

                    outvarlevel = 'nominal'
                    outvartype = 'string'
                    outvarlen = variable.str.len().max()

            except ValueError:

                print('Unable to identify compatible metadata')

                if (debug):
                    print(10 * '-')
                    print("SAS Variable metadata profile")
                    print(varname)
                    print(varrole)
                    print(outvartype)
                    print(outvarlevel)
                    print(outvarlen)

            else:

                jsondicts = {}
                jsondicts['name'] = varname
                jsondicts['role'] = varrole
                jsondicts['type'] = outvartype
                jsondicts['level'] = outvarlevel
                jsondicts['length'] = outvarlen
                file.append(jsondicts)

    else:
        raise Exception("You don't pass the right arguments. Check their types")

    with open(outdir + '/inputVar.json', 'w') as f:
        json.dump(file, f, indent=2)

    msg = "inputVar.json file generated successfully!"

    return msg

def generate_outputvar(traindf, targetname, outdir, debug=False):

    """
    Output variable list to dictionary for generating outputVar and targetVar json files

    Parameters
    ----------
    traindf : pandas DataFrame
        The Analytical Business Table with all inputs and target variables
    target : str
        The name of Target variable
    outdir : path
        The path of output directory

    Raises
    ------
    ValueError
        Unable to identify compatible metadata
    Exception
        You don't pass the right arguments. Check their types

    Return
    -------
        outputVar json file

    """

    if isinstance(traindf, pd.DataFrame) and isinstance(targetname, str):

        file_one = []
        #         file_two = []

        try:

            variable = traindf[targetname]

            # Metadata information Base

            varname = targetname
            varrole = 'target'
            vartype = variable.dtypes.name
            # varlevel = ''

            first_value = variable.loc[variable.first_valid_index()]
            numericstate = pd.api.types.is_numeric_dtype(first_value)
            stringstate = pd.api.types.is_string_dtype(first_value)

            if (debug):
                print(20 * '-')
                print('{} metadata profile'.format(varname))
                print(20 * '-')

                print(varname)
                print(varrole)
                print(vartype)
                #                 print(varlevel)
                print(numericstate)
                print(stringstate)

            if (numericstate):

                if (vartype == 'category'):
                    outvarlevel = 'nominal'
                else:
                    outvarlevel = 'interval'

                outvartype = 'decimal'
                outvarlen = 8

            elif (stringstate):

                outvarlevel = 'nominal'
                outvartype = 'string'
                outvarlen = variable.str.len().max()

        except ValueError:

            print('Unable to identify compatible metadata')

            if (debug):
                print(10 * '-')
                print("SAS Variable metadata profile")
                print(varname)
                print(varrole)
                print(outvartype)
                print(outvarlevel)
                print(outvarlen)

        else:

            if outvarlevel == 'nominal':

                taglevels = list(traindf[targetname].unique())

                for level in taglevels:
                    jsondict_one = {}

                    jsondict_one['name'] = 'P_' + targetname + str(level)
                    jsondict_one['role'] = varrole
                    jsondict_one['type'] = outvartype
                    jsondict_one['level'] = outvarlevel
                    jsondict_one['length'] = outvarlen

                    file_one.append(jsondict_one)

            else:

                jsondict_one['name'] = 'P_' + targetname
                jsondict_one['role'] = varrole
                jsondict_one['type'] = outvartype
                jsondict_one['level'] = outvarlevel
                jsondict_one['length'] = outvarlen

                file_one.append(jsondict_one)

    #             jsondict_two = {}

    #             jsondict_two['name'] = targetname
    #             file_two.append(jsondict_two)
    else:

        raise Exception("You don't pass the right arguments. Check their types")

    with open(outdir + '/outputVar.json', 'w') as f_one:
        #open(outdir + '/targetVar.json', 'w') as f_two
        json.dump(file_one, f_one, indent=2)
        #json.dump(file_two, f_two, indent=2)

    msg = "outputVar.json and targetVar files generated successfully!"

    return msg

def generate_modelproperties(modelName, modelDesc, targetname, modelType, eventvalue, nTargetCat, modeler, outdir, eventProbVar = None, debug = False):

    # modelTerm

    #    thisForm = modelDesc + ' : ' + targetVariable + ' = '
    #    iTerm = 0
    #    for thisTerm in modelTerm:
    #        if (iTerm > 0):
    #            thisForm = thisForm + ' + '
    #        thisForm += thisTerm
    #        iTerm += 1

    modeldesc = modelDesc + ' : ' + targetname

    if (nTargetCat > 2):
        targetLevel = 'NOMINAL'
    else:
        targetLevel = 'BINARY'

    if (eventProbVar == None):
        eventProbVar = 'P_' + targetname.upper() + str(eventvalue)

    # modeler = os.getlogin()

    toolVersion = str(sys.version_info.major) + '.' + str(sys.version_info.minor) + '.' + str(sys.version_info.micro)

    index=('name', 'description', 'function', 'scoreCodeType', 'trainTable', 'trainCodeType', 'algorithm', \
           'targetVariable', 'targetEvent', 'targetLevel', 'eventProbVar', 'modeler', 'tool', 'toolVersion')
    
    metadata = (modelName.lower(), \
                modeldesc.lower(), \
                 'classification', \
                 'python', \
                 ' ', \
                 'Python', \
                 modelType.lower().capitalize(), \
                 targetname.upper(), \
                 str(eventvalue), \
                 targetLevel, \
                 eventProbVar, \
                 modeler.lower(), \
                 'Python 3', \
                 toolVersion)
    
    jsondicts = dict(zip(index, metadata))

    # jsondicts = {}

    #     jsondicts['custom properties'] = []
    #     jsondicts['externalUrl'] = ""
    #     jsondicts['trainTable'] = ""
    #     jsondicts['trainCodeType'] = ""
    #     jsondicts['description'] = ""
    #     jsondicts['tool'] = ""
    #     jsondicts['toolVersion'] = ""
    #     jsondicts['targetVariable'] = tgname.upper()
    #     jsondicts['scoreCodeType'] = "Python"
    #     jsondicts['externalModelId'] = ""
    #     jsondicts['createdBy'] = coder.lower()
    #     jsondicts['function'] = mlpj.lower()
    #     jsondicts['eventProbVar'] = 'P_' + upper(tgname) + str(tgevent)
    #     jsondicts['modeler'] = ""
    #     jsondicts['name'] = modelname.lower()
    #     jsondicts['targetEvent'] = str(tgevent)
    #     jsondicts['targetLevel'] = "BINARY"
    #     jsondicts['algorithm'] = algt.lower()

    with open(outdir + '/modelproperties.json', 'w') as f:
        json.dump(jsondicts, f, indent=2)

    #     print("fileMetadata Json file generated successfully!")

    # else:
    #     print('Score code must be a .py or .ds2. No json file will be generated. ')

def generate_fitstat(targetvar_train, targetvar_test, targetname, eventvalue, y_pred_train, y_pred_test, outdir, debug=False):

    '''
    Function to prepare FitStat json file
    '''

    _dict_DataRole_ = {'parameter': '_DataRole_', 'type': 'char', 'label': 'Data Role',
                       'length': 10, 'order': 1, 'values': ['_DataRole_'], 'preformatted': False}

    _dict_PartInd_ = {'parameter': '_PartInd_', 'type': 'num', 'label': 'Partition Indicator',
                      'length': 8, 'order': 2, 'values': ['_PartInd_'], 'preformatted': False}

    _dict_PartInd__f = {'parameter': '_PartInd__f', 'type': 'char', 'label': 'Formatted Partition',
                        'length': 12, 'order': 3, 'values': ['_PartInd__f'], 'preformatted': False}

    _dict_NObs_ = {'parameter': '_NObs_', 'type': 'num', 'label': 'Sum of Frequencies',
                   'length': 8, 'order': 4, 'values': ['_NObs_'], 'preformatted': False}

    _dict_ASE_ = {'parameter': '_ASE_', 'type': 'num', 'label': 'Average Squared Error',
                  'length': 8, 'order': 5, 'values': ['_ASE_'], 'preformatted': False}

    _dict_RASE_ = {'parameter': '_RASE_', 'type': 'num', 'label': 'Root Average Squared Error',
                   'length': 8, 'order': 7, 'values': ['_RASE_'], 'preformatted': False}

    _dict_MCE_ = {'parameter': '_MCE_', 'type': 'num', 'label': 'Misclassification Error',
                  'length': 8, 'order': 8, 'values': ['_MCE_'], 'preformatted': False}

    _dict_GINI_= {'parameter': '_GINI_', 'type': 'num', 'label': 'Gini coefficient',
                'length': 8, 'order': 10, 'values': ['_GINI_'], 'preformatted': False}

    _dict_MCLL_= {'parameter': '_MCLL_', 'type': 'num', 'label': 'Multiclass log loss',
                'length': 8, 'order': 10, 'values': ['_MCLL_'], 'preformatted': False}
    
    _dict_KS_ = {'parameter': '_KS_', 'type': 'num', 'label': 'Kolmogorov-Smirnov coefficient',
                'length': 8, 'order': 10, 'values': ['_KS_'], 'preformatted': False}

    # _dict_THRESH_ = {'parameter': '_THRESH_', 'type': 'num', 'label': 'Threshold for MCE',
    #                  'length': 8, 'order': 9, 'values': ['_THRESH_'], 'preformatted': False}

    _dict_C_ = {'parameter': '_C_', 'type': 'num', 'label': 'Area Under Curve',
                'length': 8, 'order': 10, 'values': ['_C_'], 'preformatted': False}

    _dict_DIV_ = {'parameter': '_DIV_', 'type': 'num', 'label': 'Divisor for ASE',
                  'length': 8, 'order': 6, 'values': ['_DIV_'], 'preformatted': False}

    _dict_TAU_ = {'parameter': '_TAU_', 'type': 'num', 'label': 'TAU coefficient',
                  'length': 8, 'order': 6, 'values': ['_TAU_'], 'preformatted': False}


    # '_THRESH_' : _dict_THRESH_
    
    parameterMap = {'_DataRole_': _dict_DataRole_, '_PartInd_': _dict_PartInd_, '_PartInd__f':  _dict_PartInd__f,
                    '_NObs_' : _dict_NObs_, '_ASE_' : _dict_ASE_, '_RASE_' : _dict_RASE_,
                    '_MCE_' : _dict_MCE_, '_GINI_': _dict_GINI_, '_MCLL_': _dict_MCLL_, 
                    '_KS_': _dict_KS_, '_C_' : _dict_C_, '_DIV_' : _dict_DIV_, '_TAU_' : _dict_TAU_ }

    # Find out the number of observations
    nObs_train = len(targetvar_train)
    nObs_test = len(targetvar_test)

    SAMPLES = ('TRAIN', 'TEST')
    nObs = (nObs_train, nObs_test)
    target_vars = (targetvar_train, targetvar_test)
    EventPredProbabilities = (y_pred_train, y_pred_test)

    # Statistics

    # '_KSCut_', '_KSPostCutoff_'

    stats_index = ('_DataRole_', '_PartInd_', '_PartInd__f', '_NObs_', '_ASE_', \
                    '_RASE_', '_MCE_', '_GINI_','_MCLL_', '_KS_', \
                        '_C_', '_DIV_', '_TAU_')

    stats = {}
    data = {}
    datamap=[]

    partidx = 1

    for sample, nobs, targetvar, event_probability in zip(SAMPLES, nObs, target_vars, EventPredProbabilities):

        stats = {}
        data = {}

        prob_threshold = np.mean(targetvar.values)
        y_predclass = np.where(event_probability>= prob_threshold, 1, 0)

        # Datarole
        _DataRole_ = sample

        # Partition index

        _partind_ = str(partidx)

        # Formatted Partition index
        
        _formattedPartition_='           '+str(partidx)

        # Number of sample observation
        _nobs_=str(nobs)

        # ASE uses average squared error as the objective function
        _ase_ = str(metrics.mean_squared_error(targetvar, y_predclass))

        # RASE uses the root average squared error as the objective function

        _rase_=str(sqrt(metrics.mean_squared_error(targetvar, y_predclass)))

        # MCE uses the misclassification rate as the objective function

        _mce_ = str(1-metrics.accuracy_score(targetvar, y_predclass))

        # AUC uses area under the curve as the objective function
        _auc_ = metrics.roc_auc_score(targetvar, y_predclass)

        # GINI uses the Gini coefficient as the objective function
        _gini_= str((2 * _auc_) - 1)

        # GAMMA uses the gamma coefficient as the objective function
        # shape, loc, scale = gamma.fit(y_predclass, floc=0)
        # _gamma_ = 1/scale

        # MCLL uses the multiclass log loss as the objective function
        _mcLL_ = str(metrics.log_loss(targetvar, y_predclass))

        # KS uses the Kolmogorov-Smirnov coefficient as the objective function
        fpr, tpr, thresholds = metrics.roc_curve(targetvar, y_predclass)

        _ks_=str(max(fpr-tpr))

        # _KSPostCutoff_
        
        # _kspostcutoff_='null'

        # C uses Area Under ROC

        _c_ = str(metrics.auc(fpr, tpr))
        
        #_DIV_

        _div_ = str(len(targetvar))

        # TAU uses the tau coefficient as the objective function

        _tau_ = str(kendalltau(targetvar, y_predclass)[0])

        # _KSCut_
        
        # _kscut_ = 'null'
        
        # rowNumber
        
        rowNumber = str(partidx)

        partidx += 1
        
        # header 
        
        header = 'null'

        #_gamma_

        # _kspostcutoff_, _kscut_
        
        stats_values = (_DataRole_, _partind_, _formattedPartition_, _nobs_, _ase_, \
                    _rase_, _mce_, _gini_, _mcLL_, _ks_, _c_, _div_, _tau_)

        stats_dataframe = pd.DataFrame(stats_values, index=stats_index)
        stats = pd.Series.to_dict(stats_dataframe[0])
        data['dataMap'] = stats
        data['rowNumber'] = rowNumber
        data['header'] = header
        datamap.append(data)

    outJSON = {'name' : 'dmcas_fitstat',
        'revision' : 0,
        'order' : 0,
        'parameterMap' : parameterMap,
        'data' : datamap,
        'version' : 1,
        'xInteger' : False,
        'yInteger' : False}
       
    with open(outdir + '/dmcas_fitstat.json', 'w') as f:
        json.dump(outJSON, f, indent=2, skipkeys=True)
		
    # msg = "dmcas_fitstat.json generated successfully!"

    # return msg

def generate_fileMetadata(scorefilename, picklename, outdir, debug=False): 
    
    '''Metadata file information for generating MetaData file json'''
        
    file = []
    
    #File name lists
    
    jsonroles = ('inputVariables', 'outputVariables', 'score', 'python pickle')
    jsonnames = ('inputVar.json', 'outputVar.json', scorefilename, picklename)
    
    
    for role,name in zip(jsonroles, jsonnames):
        
        jsondicts={}
        jsondicts['role'] = role
        jsondicts['name'] = name
        file.append(jsondicts)

        with open(outdir + '/fileMetadata.json', 'w') as f:
            json.dump(file, f, indent=2)
            
    # print("fileMetadata Json file generated successfully!")

# def generate_container_scorefile():

def load_to_viya(server,user,password,score_result_dir,dataPrefix, printCASMessages = False):
    #os.environ['CAS_CLIENT_SSL_CA_LIST']='/opt/sas/viya/config/etc/SASSecurityCertificateFramework/cacerts/trustedcerts.pem'
    s = swat.CAS(server, 5570, user, password)
    swat.options.cas.print_messages = printCASMessages
    perfFiles = glob.glob(score_result_dir+dataPrefix+'*')
    for i, file_ in enumerate(perfFiles, 1):
        filename = os.path.splitext(os.listdir(score_result_dir)[i])[0]
        upload_file = s.upload_file(file_, casout=filename)
        if s.table.tableExists(caslib='Public', name=filename).exists ==2:
            s.table.dropTable(caslib='Public', name=filename)
        promote_table = s.table.promote(caslib='CASUSER',
                                        drop=True,
                                        targetLib = 'Public',
                                        name=filename)
        results = s.table.tableExists(caslib='Public', name=filename)
        if results.exists == 0:
            print ('The table %s failed to load into memory.' % (filename))
        elif results.exists == 1:
            print ('Promotion failed, the table %s is session-scoped.' % (filename))
        else:
            print ('The table %s was successfully promoted!' % (filename))
    s.session.endsession()
