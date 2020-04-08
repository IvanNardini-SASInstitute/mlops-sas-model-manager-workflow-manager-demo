# SAS for Model Ops
# A ModelOps Environment Architecture with SAS Model Manager and SAS Workflow Manager

<img src="https://gitlab.sas.com/ivnard/modelops-with-sas-model-manager-and-sas-workflow-manager/raw/master/Operationalize_Analytics.png">

## Covered functionality

This demo is about **governing open source model in a ModelOps enviroment using SAS Open Model Manager and SAS Workflow Manager** 
In particular, I'll show

1. **Open Source Model Development for a Credit Scoring Business request**

    - Data preparation on MondoDb nosql data

    - Model Training with Python Sklearn – XgBoost libraries

    - Engineering of Machine Learning pipeline

    - Model packaging for Model Deployment to SAS model-container-recipes (Python 3)

2. **CI/CD pipeline with Git and Jenkins**

    - Code versioning in Git

    - Jenkins pipeline that covers Code Quality, Data sanity, Unit test, Integration test and a SAS model registration service to SAS Model Manager central repository

3. **Semi-Automated Model Deployment from SAS Model Manager on a docker private registry with SAS Workflow Manager**

    The main subprocesses of the pipeline are:

    - Model Review

    - Pre-Production Validation

    - Automated Champion Docker image push into a Docker registry

    - Model Performance monitoring

and others...

Below the **high-level architecture of the solution**: 

<img src="https://gitlab.sas.com/ivnard/modelops-with-sas-model-manager-and-sas-workflow-manager/raw/master/Solution_Architecture.png">

## Requirements

An local **Docker enviroment**

An remote **SAS Viya release:V.03.05**

## Usage 

In the **demo_materials** folder, you can find the **customer deck** and **demo video**.

About the steps to make the demo: 

1. **Git clone** the repo on your local enviroment.

2. Go into project folder and run **docker-compose up**. I'll take a while for creating the dockerized enviroment with Jupyter lab and Jenkins.

Once you get all services up and running you have to configure them. So let's do it!

3. To access to JupyterLab web gui, you have to copy and paste in the browser a link like this 

    > 
    > [I 11:59:16.597 NotebookApp] The Jupyter Notebook is running at:
    > http://localhost:8888/?token=c8de56fa4deed24899803e93c227592aef6538f93025fe01
    >

    Then create a **github folder**. 

    Back to JupyterLab, **go to git terminal** and configure parameters of your github folder like this

    >
    > git config --global user.name "Ivanxxxxx"
    > git config --global user.email "xxxxxxxx@sas.com"
    > git config --global core.autocrlf input

    > git init
    > git add .
    > git commit -m "test" 

    > git remote add origin https://github.com/xxxxxxx/ModelOps_Credit_scoring.git
    > git push -u origin master
    >

    **NOTICE: Be use to inizilize the git repo in the right local folder**

    At this point **Open Source Development enviroment is almost ready**.

    One last thing: under *project\3_CI_CD\5_model_manager_registration_service\registration.properties*, **please update the parameters based on your SAS Open Model Manager server**

    > set SASLogon username
    > username=sasdemo

    > set SASLogon password
    > password=Orion123

    > VIYA server
    > server_ip=http://10.96.1.209/

4. To configure Jenkins, once the container is up and running, the post-installation setup wizard begins.

    Please refer to this [link](https://jenkins.io/doc/book/installing/#unlocking-jenkins) to unlock and install all the Jenkins plug-ins in the proper way

    Once your Jenkins server is ready, create Jenkins pipeline 

    - Click the **New Item menu** within Jenkins Classic UI left column

    - **Provide a name** for your new item (e.g. My Pipeline) and select Multibranch Pipeline

    - Click the **Add Source** button, choose the type of repository you want to use and fill in the details (create credential credentials )

    - Select Pipeline source and if you do all in a proper way you can pass this path directly **/project/3_CI_CD/Jenkinsfile**

    - **Click the Save button** 

    **You should watch your first Pipeline run!**

And you can switch to **Blue Ocean for Jenkins Pipelines** to get a more appelling pipeline 

5. SAS Model Manager and SAS Workflow Manager environment

    >
    >
    > To be continued....
    >
    >

<img src="https://gitlab.sas.com/ivnard/modelops-with-sas-model-manager-and-sas-workflow-manager/raw/master/Workflow.png">

## Contributions

Test it. And please provide me feedback for improvements. Pull requests are welcome as well.

And feel free to reach me at [Ivan Nardini](ivan.nardini@sas.com )
