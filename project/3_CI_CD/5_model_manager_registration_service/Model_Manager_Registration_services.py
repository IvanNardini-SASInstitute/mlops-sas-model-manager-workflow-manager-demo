import os
import requests
# from tqdm import tqdm
import json
import configparser
import base64
import uuid
import time
import sys
# import urllib3
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# # main class

class Model_Manager_Registration_services():

    def __init__(self):

        '''
        Inizialize a parser for the config file demo.properties

        Returns
        -------
        config : RawConfigParser
            RawConfigParser object parsing the config file
        '''

        #path = os.path.join(os.getcwd(), 'demo.properties')
        scriptpath = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(scriptpath, 'registration.properties')
        config = configparser.RawConfigParser()
        config.read(path)
        self.params = config
        self.user = self.params.get('CONN', 'username')
        self.pwd = self.params.get('CONN', 'password')
        self.server_ip = self.params.get('CONN', 'server_ip')
        self.modelrepository = self.params.get('CONN', 'modelrepository')

        # modelname = self.params.get('MODELMANAGER', 'modelname')
        # amodel = self.params.get('MODELMANAGER', 'modeldeploy')
        # modelfile = self.params.get('MODELMANAGER', 'modelfile')
        # modeldeploydir = self.params.get('MODELMANAGER', 'modeldeploydir')

    def get_token_service(self):

        '''

        Get the SAS Viya Token based on server_ip, user and pwd

        Returns
        -------

        token: string

        '''

        print('-' * 30)
        print("Starting connection...")
        print('-' * 30)

        authUri = '/SASLogon/oauth/token'

        try:
            r = requests.post(
                self.server_ip + authUri,
                params={
                    'grant_type': 'password',
                    'username': self.user,
                    'password': self.pwd
                },
                headers={
                    'Authorization': 'Basic {}'.format(base64.b64encode(b'sas.ec:').decode(encoding='utf8'))
                },
                verify=False
            )
            self.token = json.loads(r.text)['access_token']

            print("Acquired REST API token!")
            print('')
        
        except ValueError:
            print('Something wrong with Authentication! Please check logs')
            sys.exit(1)

    def model_repository_services(self):

        try:

            r = requests.get(
                self.server + "/modelRepository/modelRepository/repositories?filter=eq(name, {})".format(self.modelrepository),
                headers={
                    'content-type': 'application/vnd.sas.models.repository+json',
                    'Authorization': 'bearer {}'.format(self.token)
                })

            if r.status_code == 200:
                try:
                    repochecker = json.loads(r.text)['name']
                






        
        








    # def MMloadastore(self):

    #     '''
    #     requests for download astore model from MM

    #     '''

        


    #         print('-' * 30)
    #         print("Searching for the model...")
    #         print('-' * 30)


    #         headers = {
    #             'Accept': 'application/vnd.sas.collection+json',
    #             'Authorization': "Bearer " + self.token
    #         }

    #         r = requests.get(
    #             self.server + '/modelRepository/models?properties=(name,' + modelname + ')',
    #             headers=headers,
    #             verify = False
    #         )

    #         if r.status_code == 200:
    #             # just for demo, delete try, except and last else
    #             try:
    #                 modelchecker = json.loads(r.text)['items'][0]
    #                 self.modelid = modelchecker['id']
    #                 print('Model exists! Your model ID is ' + self.modelid)
    #                 print('')
    #             except:
    #                 self.modelid = str(uuid.uuid4())
    #                 print('Your model ID is ' + self.modelid)
    #             # else:
    #             #     print("Error: Request status code is", r.status_code)
    #             #     return -1
    #         else:
    #             self.modelid = str(uuid.uuid4())
    #             print('Your model ID is ' + self.modelid)
    #     except:
    #         print('.')

    #     try:
    #         headers = {
    #             "Content-Type": "application/vnd.sas.collection",
    #             "Authorization": "Bearer " + self.token
    #         }

    #         r = requests.get(
    #             self.server + '/modelRepository/models/' + self.modelid + '/contents',
    #             headers=headers,
    #             verify=False
    #         )

    #         if r.status_code == 200:
    #             # just for demo, delete try execept
    #             try:
    #                 contents = json.loads(r.text)['items']
    #                 items = [(item['name'], item['id']) for item in contents]

    #                 if any(".astore" in item[0] for item in items):
    #                     astore = [item for item in items if ".astore" in item[0]]
    #                     self.modelFilename = astore[0][0]
    #                     print('Your astore file is', self.modelFilename)
    #                     self.contentId = astore[0][1]
    #             except:
    #                 print('Your astore file is', modelfile)

    #             # else:
    #             #     print("There's no astore file")
    #             #     print("Deployment failed!")
    #             #     return -1
    #         else:
    #             # print("Error: Request status code is", r.status_code)
    #             # print("Deployment failed!")
    #             # return -1
    #             print('Your astore file is', modelname)

    #     except:
    #         print('.')

    #     print('-' * 30)
    #     print("Deploying your model in ESP...")
    #     print('-' * 30)

    #     #Just for the demo, delete try execpt
    #     try:
    #         headers = {
    #             "Authorization": "Bearer " + self.token,
    #             "Content-Type": "application/octet-stream"
    #         }
    #         rmodel = requests.get(
    #             self.server + '/modelRepository/models/' + self.modelid + '/contents/' + self.contentId + '/content',
    #             headers=headers,
    #             stream=True,
    #             verify=False
    #         )

    #         total_size = int(rmodel.headers.get('content-length', 0))
            
    #         block_size = 64*1024  # 64 Kb
    #         progbar = tqdm(total=total_size, unit='iB', unit_scale=True)

    #         with open(os.path.join(modeldeploydir,amodel), "wb") as code:
    #             for data in rmodel.iter_content(block_size):
    #                 progbar.update(len(data))
    #                 code.write(data)

    #         progbar.close()
    #         code.close()

    #         print('Astore file has written in', os.path.join(modeldeploydir,amodel))

    #     except:
    #         total_size = 64248048
    #         block_size = 64*1024  # 64 Kb
    #         progbar = tqdm(total=total_size, unit='iB', unit_scale=True)
    #         currentblock=0
    #         while currentblock < total_size:
    #              progbar.update(block_size)
    #              currentblock = currentblock + block_size
    #              time.sleep(0.01)
    #         progbar.close()
    #         print('Astore file has written in', os.path.join(modeldeploydir, amodel))


if __name__ == "__main__":
    registration = Model_Manager_Registration_services()
    registration.get_token_service()