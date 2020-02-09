import requests as req
import json
import random

  
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
  

  

