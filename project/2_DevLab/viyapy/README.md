
## Viya API Functions
---
### Introduction

This is a high-level Python library for the SAS Viya Model Manager APIs for Python users. This library has been designed to make it simpler for Python users to create model projects & repositories, import models & manage and govern their models through the Model Manager API.

This package is used as part of the AP Practice 'Modern Analytics Platform' demo.

### Usage

As an example, if one wanted to write an API call to authenticate to Model Manager using Python, an example would be:

```{python}
import requests

response = requests.post(
    'http://viyaserver.sas.com/SASLogon/oauth/token',
    auth=('sas.ec', ''),
    headers={
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data={
        'grant_type': 'password',
        'username': 'sasdemo',
        'password': '****'
    })

token = response.json()['access_token']
```

Using the viya-py package, an equivalent code would be:

```{python}
from viyapy import ViyaClient

client = ViyaClient('http://viyaserver.sas.com')
token = client.logon.authenticate('sasdemo', '****')
```

### Installation

To install the latest development version as part of your project:

```bash
pip install git+https://gitlab.sas.com/SAS-AP/viya-py-api
```

Or in a `requirements.txt` file:

```text
-e git+https://gitlab.sas.com/SAS-AP/viya-py-api#egg=viyapy
```

Note that you may be asked to enter your GitLab credentials.

#### Dependencies

Dependencies are listed in the 'requirements.txt' file.

#### Development

When installing via pip, viyapy installs its own dependencies.

However, for development, testing and building the package, the following dependencies must be installed manually:

For development and testing:
* `requests` (tested with 2.21.0)
* `inflection` (tested with 0.3.1)

For building the package:
* `setuptools`
* `wheel`

To build a wheel package:

```bash
python setup.py bdist_wheel
```

### Quickstart

#### End-to-End Project Creation

```python
from viyapy import ViyaClient
from viyapy.variables import String, Decimal, Boolean, Date, DateTime, Integer

# Configure logging if required

import sys
import logging
logger = logging.getLogger('viyapy')
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)

# Authenticate client with Viya server

client = ViyaClient('http://viyaserver.sas.com')
client.logon.authenticate('sasdemo', '****')

# Retrieve model manager repository

repository = client.model_manager.get_repository('Repository 1')

# Create model manager project

project = repository.create_project(
    name='MAP',
    description='Project demonstrating management of open source models in Viya',
    function='classification',
    target_level='binary',
    target_event_value='1',
    class_target_values='1,0',
    target_variable='bad',
    event_probability_variable='P_BAD1',
    external_url='http://github.com/user/project',
    input=[
        Decimal('bad', level='binary'),
        Decimal('clage'),
        Decimal('clno'),
        Decimal('debtinc'),
        Decimal('derog'),
        String('job'),
        Decimal('loan'),
        Decimal('mortdue'),
        Decimal('ninq'),
        String('reason'),
        Decimal('value'),
        Integer('yoj')
    ],
    output=[
        Decimal('P_BAD0', description='Probability of not defaulting'),
        Decimal('P_BAD1', description='Probability of defaulting')
    ])

# Add model to project
# The model inherits values from the project (e.g. input and output variables) unless they are explicitly specified.

model = project.create_model(
    name='Python_GradientBoost',
    algorithm='scikit-learn.GradientBoostingClassifier',
    modeler='Yi Jian Ching',
    files=[
        '/home/sasdemo/data/gboost_train.py',
        '/home/sasdemo/data/gboost_score.py',
        ('/home/sasdemo/data/model/gboost_obj_3_6_5.pkl', True)  # binary file
    ])

# Create performance definition for project and model
# The definition inherits values from the project (e.g. input and output variables) unless they are explicitly specified.

perf_def = project.create_performance_definition(
    name='Performance Monitoring',
    models=[model])
```

#### Reloading a Project

```python
from viyapy import ViyaClient

# Authenticate client with Viya server

client = ViyaClient('http://viyaserver.sas.com')
client.logon.authenticate('viyademo', '****')

# Reload existing project

project = client.model_manager.get_project('ProjectID')
```

### Help & Questions

If you notice any issues or you have any questions about these assets, please reach out to:
- AP Team Contact								                : [Yi Jian Ching](mailto:Yijian.Ching@sas.com)
- API Developer                                 : [Thierry Jossermoz](mailto:Thierry.Jossermoz@sas.com)

It was originally based on the functions used in the 'Accelerate Modelling at Scale with SAS Viya' demo, created by Alex Ge.
