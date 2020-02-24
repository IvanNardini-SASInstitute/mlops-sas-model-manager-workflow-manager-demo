
import os
import requests
# from tqdm import tqdm
import json
import random
import configparser
import base64
import uuid
import time
import sys
# import urllib3
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

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

        self.randid = random.randint(1,1000)

        #path = os.path.join(os.getcwd(), 'demo.properties')
        scriptpath = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(scriptpath, 'registration.properties')
        config = configparser.RawConfigParser()
        config.read(path)
        self.params = config
        self.user = self.params.get('CONN', 'username')
        self.pwd = self.params.get('CONN', 'password')
        self.server_ip = self.params.get('CONN', 'server_ip')
        self.modelrepository = self.params.get('MODELMANAGER', 'modelrepository')
        self.modelfolder_name = self.params.get('MODELMANAGER', 'modelfolder')
        self.modelproject_name = self.params.get('MODELMANAGER', 'modelproject')
        self.model_dir = self.params.get('MODELMANAGER', 'modeldir')

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
            req = requests.post(
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

            resp = json.loads(req.text)
            self.token = resp['access_token']

            print("REST API token acquired!")
            print('')
            print("Your Token is {}".format(self.token[:10]))
            print('')

        except (RuntimeError, ValueError):
            print('Something wrong with Authentication! Please check logs')
            sys.exit(1)

    def model_repository_service(self):

        print('-' * 30)
        print("Starting Model Repository Service...")
        print('-' * 30)
        self.modelrepo_name='{}_{}'.format(self.modelrepository, self.randid)
        print('')

        try:

            req = requests.get(
                self.server_ip +
                "/modelRepository/repositories?name={}".format(self.modelrepo_name),
                headers={
                    'content-type': 'application/vnd.sas.models.repository+json',
                    'Authorization': 'bearer {}'.format(self.token)
                }
            )

            resp = json.loads(req.text)

            if req.status_code == 200 and not resp['items']:

                print('Creating the {} repository...'.format(self.modelrepo_name))
                print('')

                try:

                    payload={}
                    payload['name'] = '{}'.format(self.modelrepo_name)
                    print("The Repository name is " + payload["name"])
                    print('')

                    req = requests.post(
                        self.server_ip +
                        "/modelRepository/repositories",
                        headers={
                            'content-type': 'application/vnd.sas.models.repository+json',
                            'Authorization': 'bearer {}'.format(self.token)
                        },
                        data=json.dumps(payload)
                    )

                    resp = json.loads(req.text)

                    self.repositoryID = resp['id']
                    self.parentFolderID = resp['folderId']

                    print('Model Repository service creates {} repository!'.format(payload['name']))
                    print('')
                    print('{} ID is {}'.format(payload['name'], self.repositoryID))
                    print('')
                
                except ValueError:
                    print('Model Repository service is not able to create {} repository!'.format(payload['name']))
                    print('')
                    print('Please contact the Viya Administrator')
                    sys.exit(1)
            
            elif req.status_code == 200 and resp['items'][0]['name'] == str(self.modelrepo_name) :

                print('')
                print('The {} repository exists!'.format(self.modelrepo_name))

                self.repositoryID = resp['items'][0]['id']
                self.parentFolderID = resp['items'][0]['folderId']
                print('{} ID is {}'.format(self.modelrepo_name, self.repositoryID))
                print('')

            else:
                print('Model Repository service is not able to retrive Model Repository Metadata!')
                print('')
                print('Please contact the Viya Administrator')
                sys.exit(1)

        except (RuntimeError, ValueError):
            print('Something wrong with Model Repository service! Please check logs')
            sys.exit(1)

    def model_folder_service(self):

        print('-' * 30)
        print("Starting Model Folder Service...")
        print('-' * 30)
        print('')

        parentURI = '/folders/folders/{}'.format(self.parentFolderID)
        self.modelfold_name='{}_{}'.format(self.modelfolder_name, self.randid)
        print('')

        print('Creating the {} folder...'.format(self.modelfold_name))
        print('')

        try:

            payload={}
            payload['name'] = '{}'.format(self.modelfold_name)

            req = requests.post(
                    self.server_ip +
                    "/folders/folders?parentFolderUri={}".format(parentURI),
                    headers={
                        'content-type': 'application/json',
                        'Authorization': 'bearer {}'.format(self.token)
                    }, 
                    data=json.dumps(payload)
                )
            
            resp = json.loads(req.text)

            self.folder_ID = resp['id']

            print('Model Repository service creates {} folder!'.format(payload['name']))
            print('')
            print('{} ID is {}'.format(payload['name'], self.folder_ID))
            print('')
        
        except ValueError:
            print('Something wrong with Model Repository service! Please check logs')
            sys.exit(1)

    def model_project_service(self):

        print('-' * 30)
        print("Starting Model Project Service...")
        print('-' * 30)
        print('')
        self.modelproj_name='{}_{}'.format(self.modelproject_name, self.randid)

        try:

            req = requests.get(
                self.server_ip + "/modelRepository/projects?filter=eq(name, '{}')".format(self.modelproj_name),
                headers={
                    'content-type': 'application/vnd.sas.models.project+json',
                    'Authorization': 'bearer {}'.format(self.token)
                }
            )
            
            resp = json.loads(req.text)

            if req.status_code == 200 and not resp['items']:

                print('Creating the {} project...'.format(self.modelproj_name))
                print('')

                try:

                    payload = {}
                    payload['name'] = self.modelproj_name
                    payload['repositoryId'] = self.repositoryID
                    payload['folderId'] = self.folder_ID

                    req = requests.post(
                            self.server_ip +
                            "/modelRepository/projects",
                            headers={
                                'content-type': 'application/vnd.sas.models.project+json',
                                'Authorization': 'bearer {}'.format(self.token)
                            },
                            data=json.dumps(payload)
                        )

                    resp = json.loads(req.text)

                    self.projectID = resp['id']

                    print('Model Repository service creates {} repository!'.format(payload['name']))
                    print('')
                    print('{} ID is {}'.format(payload['name'], self.projectID))
                    print('')
                
                except ValueError:
                    print('Model Repository service is not able to create {} project!'.format(payload['name']))
                    print('')
                    print('Please contact the Viya Administrator')
                    sys.exit(1)

            elif req.status_code == 200 and resp['items'][0]['name'] == str(self.modelproj_name):

                print('The {} project exists!'.format(self.modelproj_name))

                self.projectID = resp['items'][0]['id']
                print(self.projectID)
                print("{} ID is {}".format(self.modelproj_name, self.projectID))
                print('')
                
            else :
                print('Model Repository service is not able to retrive Model Project Metadata!')
                print('')
                print('Please contact the Viya Administrator')
                sys.exit(1)

        except ValueError:
            print('Something wrong with Model Repository service! Please check logs')
            sys.exit(1)

    def model_registration_service(self):

        print('-' * 30)
        print("Starting Model Registration Service...")
        print('-' * 30)
        print('')

        files = [content for content in os.listdir(self.model_dir) if content.endswith(".zip")]

        if not files:
            print("Can't find model zip file in the {} repository !".format(self.model_dir))
            print('')
            sys.exit(1)
        else:
            self.contentname = files[0][:-4]
            # self.randid _{}
            self.modelname = "{}".format(self.contentname)
            self.model_path = self.model_dir + files[0]
        
        try:

            print(' Registring {} model as {}...'.format(self.contentname, self.modelname))
            print('')
            
            modelfile = open(self.model_path, 'rb')

            files_dic = {}
            files_dic['files'] = ("{}.zip".format(self.modelname), modelfile, 'multipart/form-data')

            req = requests.post(
            self.server_ip + "/modelRepository/models?name={}&type=ZIP&projectId={}&versionOption=Latest".format(self.modelname, self.projectID),
            headers={
                'Authorization': 'bearer {}'.format(self.token)
            },
            files=files_dic)
            
            resp = json.loads(req.text)

            if req.status_code == 201:

                try:

                    print('The {} model is successfully registered as {} !'.format(self.contentname, self.modelname))
                    print('')
                    self.modelID = resp['items'][0]['id']
                    print('{} ID is {}'.format(self.modelname, self.modelID))
                    print('')

                except ValueError:

                    print('Model Registration service is not able to register {} model!'.format(self.modelname))
                    print('')
                    print('Please check logs')
                    sys.exit(1)
            
            else:
                print('Model Registration service is not able to retrive Model Metadata!')
                print('')
                print('Please contact the Viya Administrator')
                sys.exit(1)

            # Some Metadata of the project needs to be updated once it created

            payload={}
            payload['name'] = self.modelproj_name
            payload['description'] = 'Marketing Churn project with Containers'
            payload['function'] = 'classification'
            payload['targetLevel'] = 'binary'
            payload['targetEventValue'] = '1'
            payload['classTargetValues'] ='1,0'
            payload['targetVariable'] ='BAD'
            payload['eventProbabilityVariable'] = 'P_BAD1'
            payload['externalUrl'] = 'https://github.com/IvanNardini/ModelOps.git'
            payload['repositoryId'] = self.repositoryID
            payload['folderId'] = self.folder_ID


            req = requests.get(self.server_ip + '/modelRepository/projects/' + self.projectID, 
                               headers = {
                                'content-type':  'application/vnd.sas.models.project+json',
                                'Authorization': 'bearer {}'.format(self.token)
                               }
                            )

            resp = json.loads(req.text)
            
            self.projectEtag = req.headers['ETag']

            req = requests.put(self.server_ip + '/modelRepository/projects/' + self.projectID,
                                headers={
                                        'Content-type': 'application/vnd.sas.models.project+json',
                                        'If-match': self.projectEtag,
                                        'Authorization': 'bearer {}'.format(self.token)
                                        },
                                data=json.dumps(payload)
                            )

            resp = json.loads(req.text)

        except ValueError:
            print('Something wrong with Model Repository service! Please check logs')
            sys.exit(1)
    

if __name__ == "__main__":
        
    registration = Model_Manager_Registration_services()
    registration.get_token_service()
    registration.model_repository_service()
    registration.model_folder_service()
    registration.model_project_service()
    registration.model_registration_service()

    # SENDGRID_API_KEY='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'
    
    # message = Mail(
    # from_email='SASModelManager_RegistrationService@jenkins.com',
    # to_emails='ivan.nardini92@gmail.com',
    # subject='Churn Classification Project: Status',
    # html_content='<strong> Analytics team delivers the champion model. \
    #                        Jenkins validates it.\
    #                        The system registers it in SAS Model Manager \
    #                        To approve it, go to http://172.28.234.57/SASModelManager/ </strong>')
    # try:
    #     sg = SendGridAPIClient(SENDGRID_API_KEY)
    #     response = sg.send(message)
    #     # print(response.status_code)
    #     print('Model Registration Mail successfully delivered!')
    #     # print(response.body)
    #     # print(response.headers)
    # # Exception as e
    # except ValueError:
    #     # print(e.message)
    #     print(response.status_code)
    #     print('')
    #     print(response.body)
    #     sys.exit(1)