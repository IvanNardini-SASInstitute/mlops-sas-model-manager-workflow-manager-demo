import requests as req
import json
import random

def model_proj(token, repoid, folderid):

  mmService = 'http://10.96.17.30'

  headersProj={
      'content-type': 'application/vnd.sas.models.project+json',
      'Authorization':'bearer %s' % token
  }
  
  projName="AIDEAS Churn Classification %d" % randid
  print("Project name = " + projName)
  
  newProj = {
      "name": projName,
      "repositoryId": repoid,
      "folderId": folderid,
      "function": "classification",
      "targetLevel": "Binary"
  }
  
  reply = req.post(mmService + '/modelRepository/projects', data=json.dumps(newProj), headers = headersProj)
  myProj = reply.json()
  
  projectID = myProj['id']
  return projectID
  
def register_model(token, path, modelname, projid):

  mmService = 'http://10.96.17.30'

  #Load zip files
  mfile = open(path, 'rb')
  
  modelName = modelname + " %d" % randid
  print("Custom model name = " + modelName)
  
  headersModel = {
      'Authorization':'bearer %s' % token
  }
  
  files = {'files': (modelName+".zip", mfile, 'multipart/form-data')}
  
  reply = req.post(mmService + "/modelRepository/models?name=" + modelName + "&type=ZIP&projectId=" + projid +"&versionOption=Latest", 
                          files=files, headers=headersModel)
  myModel = json.loads(reply.content.decode('utf-8'))
  mfile.close()
  
  modelID = myModel['items'][0]['id']
  print("Custom model ID = " + modelID)
  

  

