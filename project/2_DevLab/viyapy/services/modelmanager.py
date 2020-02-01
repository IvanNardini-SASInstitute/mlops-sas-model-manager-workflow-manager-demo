import os
import sys
import json
import inflection

from ..exceptions import ViyaException

import logging
logger = logging.getLogger(__name__)


class ModelManager:

    repositories_service_url = "/modelRepository/repositories"
    projects_service_url = "/modelRepository/projects"
    models_service_url = "/modelRepository/models"
    performance_definition_service_url = '/modelManagement/performanceTasks'

    def __init__(self, client):
        self.client = client

    def get_repositories(self):
        repo_list = self.client.request("get", self.repositories_service_url)
        logger.info(f"Repository status is: {repo_list.ok}")
        return repo_list.json()

    def get_repository(self, name):
        repo_list = self.client.request("get", self.repositories_service_url,
                                        params={"filter": f'eq(name, "{name}")'})
        try:
            repository = Repository(self)
            repository.from_viya(repo_list.json().get("items")[0])
            logger.info(f"Retrieved successfully: {repository}")
            return repository
        except (KeyError, IndexError):
            raise ViyaException(f"Could not find repository '{name}'")

    def get_project_list(self, response_content=''):
        response = self.client.request("get", f"{self.projects_service_url}")
        logger.info(f"Project list retrieved successfully: {response.ok}")
        if response_content == 'json':
            return response.json()
        else:
            return response

    def check_project_exists(self, name):
        response = self.client.request("get", f"{self.projects_service_url}?name={name}")
        #logger.info(f"URL is: {self.projects_service_url}?name={name}")
        #logger.info(f"Project check is: {response.ok}")
        return response.json()

    def get_project(self, project_id):
        response = self.client.request("get", f"{self.projects_service_url}/{project_id}")
        try:
            project = Project(self)
            project.from_viya(response.json())
            project.etag = response.headers.get("ETag")
            logger.info(f"Retrieved successfully: {project}")
            return project
        except (KeyError, IndexError):
            raise ViyaException(f"Could not find project '{project_id}'")

    def get_model(self, model_id):
        response = self.client.request("get", f"{self.models_service_url}/{model_id}")
        try:
            model = Model(self)
            model.from_viya(response.json())
            model.etag = response.headers.get("ETag")
            logger.info(f"Retrieved successfully: {model}")
            return model
        except (KeyError, IndexError):
            raise ViyaException(f"Could not find model '{model_id}'")

    def get_performance_definition(self, definition_id):
        response = self.client.request("get", f"{self.performance_definition_service_url}/{definition_id}")
        try:
            definition = PerformanceDefinition(self)
            definition.from_viya(response.json())
            logger.info(f"Retrieved successfully: {definition}")
            return definition
        except (KeyError, IndexError):
            raise ViyaException(f"Could not find repository '{defintion_id}'")

    def create_project(self, project):
        response = self.client.request("post", self.projects_service_url,
                                       headers={"Content-Type": "application/vnd.sas.models.project+json"},
                                       data=json.dumps(project.to_viya()))
        project.from_viya(response.json())
        project.etag = response.headers.get("ETag")
        logger.info(f"Created successfully: {project}")
        return project

    def update_project(self, project):
        response = self.client.request("put", f"{self.projects_service_url}/{project.id}",
                                       headers={"Content-Type": "application/vnd.sas.models.project+json",
                                                "If-Match": project.etag},
                                       data=json.dumps(project.to_viya()))
        project.from_viya(response.json())
        project.etag = response.headers.get("ETag")
        logger.info(f"Updated successfully: {project}")
        return project

    def delete_project(self, project):
        self.client.request("delete", f"{self.projects_service_url}/{project.id}")
        logger.info(f"Deleted successfully: {project}")

    def create_model(self, model):
        response = self.client.request("post", self.models_service_url,
                                       headers={"Content-Type": "application/vnd.sas.models.model+json"},
                                       data=json.dumps(model.to_viya()))
        model.from_viya(response.json().get("items")[0])
        logger.info(f"Created successfully: {model}")
        return model

    def update_model(self, model):
        response = self.client.request("put", f"{self.models_service_url}/{model.id}",
                                        headers={"Content-Type": "application/vnd.sas.models.model+json",
                                                 "If-Match": model.etag},
                                        data=json.dumps(model.to_viya()))
        model.from_viya(response.json())
        model.etag = response.headers.get("ETag")
        logger.info(f"Updated successfully: {model}")
        return model

    def create_model_version(self, model, options='major'):
        response = self.client.request("post", f"{self.models_service_url}/{model.id}/modelVersions",
                                        headers={"Content-Type": "application/vnd.sas.models.model.version+json"},
                                        data=json.dumps({'option': options}))
        ## TODO: Response returned is 'modelVersion' and either needs to be a new class or the model needs to be returned properly with updated version
        return response

    ## TODO: rename file -> content to keep in line with MM naming
    ## TODO: fix these properly

    def create_file(self, model, filename, binary=False, role=None):
        with open(filename, "r" + ("b" if binary else "")) as f:
            file_content = f.read()
        file_name = os.path.basename(filename)
        response = self.client.request("post", f"{self.models_service_url}/{model.id}/contents",
                                        headers={"Content-Type": "application/octet-stream"},
                                        params={"name": file_name, "role": role},
                                        data=file_content)
        #@todo: setting role when creating the file currently doesn't work, requires an update
        file = File(self)
        file.from_viya(response.json())
        logger.info(f"Created successfully: {file}")
        return file

    def get_all_files(self, model_id, role=''):
        response = self.client.request("get", f"{self.models_service_url}/{model_id}/contents?role={role}",
                                         headers={"Content-Type": "application/vnd.sas.collection+json"})
        try:
            file = File(self)
            file.from_viya(response.json())
            logger.info(f"Retrieved successfully: {file}")
            return file
        except (KeyError, IndexError):
            raise ViyaException(f"Could not find files for '{model_id}'")

    def get_files(self, model_id, role=''):
        '''Get model content given a content role.
        '''
        response = self.client.request("get", f"{self.models_service_url}/{model_id}/contents?role={role}",
                                         headers={"Content-Type": "application/vnd.sas.collection+json"})
        try:
            file = File(self)
            file.from_viya(response.json().get("items")[0])
            logger.info(f"Retrieved successfully: {file}")
            return file
        except (KeyError, IndexError):
            raise ViyaException(f"Could not find files for '{model_id}'")

    def get_file_metadata(self, model, file):
        response = self.client.request("get", f"{self.models_service_url}/{model.id}/contents/{file.id}",
                                        headers={"Content-Type": 'application/vnd.sas.models.model.content+json'})
        file = File(self)
        file.from_viya(response.json())
        file.etag = response.headers.get("ETag")
        logger.info(f"Retrieved successfully: {file}")
        return file

    def get_file_content(self, model_id, file_id):
        response = self.client.request("get", f"{self.models_service_url}/{model_id}/contents/{file_id}/content",
                                        headers={"Content-Type": 'application/octet-stream'})
        logger.info(f"Retrieved successfully: Model Content with ID '{file_id}'")
        return response

    def update_content(self, model, file):
        response = self.client.request("put", f"{self.models_service_url}/{model.id}/contents/{file.id}",
                                        headers={"Content-Type": "application/vnd.sas.models.model.content+json",
                                                "If-Match": file.etag},
                                        data=json.dumps(file.to_viya()))
        file = File(self)
        file.from_viya(response.json())
        file.etag = response.headers.get("ETag")
        logger.info(f"Retrieved successfully: {file}")
        return file

    def delete_content(self, model, file):
        response = self.client.request("delete", f"{self.models_service_url}/{model.id}/contents/{file.id}")
        return response

    def update_model_contents(self, model, file, content_file):
        response = self.client.request("put", f"{self.models_service_url}/{model.id}/contents/{file.id}/content",
                                        headers={"Content-Type": "application/octet-stream",
                                                 "If-Match": file.etag},
                                        data=content_file)
        file = File(self)
        file.from_viya(response.json())
        logger.info(f"Retrieved successfully: {file}")
        return file

    def create_performance_definition(self, definition):
        response = self.client.request("post", self.performance_definition_service_url,
                                       headers={"Content-Type": 'application/vnd.sas.models.performance.task+json'},
                                       data=json.dumps(definition.to_viya()))
        definition.from_viya(response.json())
        logger.info(f"Created successfully: {definition}")
        return definition

    ## TODO: create a new class for the performance execution?
    ## the call below returns response corresponding to:
        # performance job
        # job execution results that includes the code, log, and job status (state).

    def execute_performance_definition(self, definition):
        response = self.client.request("post", f"{self.performance_definition_service_url}/{definition.id}")
        job = PerformanceJob(self)
        job.from_viya(response.json())
        logger.info(f"Executed successfully: {definition}")
        return job

class BaseObject:

    _defaults = None

    def __init__(self, client, **kwargs):
        self._client = client
        self._data = {}
        if isinstance(self._defaults, dict):
            self.from_python(**self._defaults)
        self.from_python(**kwargs)

    @property
    def etag(self):
        return self._etag

    @etag.setter
    def set_etag(self, etag):
        self._etag = etag

    def from_python(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def from_viya(self, data):
        super(BaseObject, self).__setattr__("_data", data)

    def to_viya(self):
        return self._data

    def __repr__(self):
        return f"{self.__class__.__name__} <ID: '{self.id}', Name: '{self.name}'>"

    def __getattr__(self, key):
        if key.startswith('_'):
            return super(BaseObject, self).__getattr__(key)
        else:
            try:
                return self._data[inflection.camelize(key, False)]
            except KeyError:
                return None

    def __setattr__(self, key, value):
        if key.startswith('_'):
            super(BaseObject, self).__setattr__(key, value)
        else:
            self._data[inflection.camelize(key, False)] = value


class Repository(BaseObject):

    def create_project(self, **kwargs):
        # Inherit properties from repository if not explicitly defined
        kwargs["repository_id"] = self.id
        kwargs["folder_id"] = self.folder_id

        project = Project(self._client, **kwargs)
        project = self._client.create_project(project)
        # Viya ignores some arguments the first time a project is created
        # So perform update right after creation so users don't have to
        # Remove input and output variables before updating
        for k in ("input", "output"):
            kwargs.pop(k, None)
        project.update(**kwargs)
        return project


class Project(BaseObject):

    def from_python(self, repository=None, input=None, output=None, **kwargs):
        super(Project, self).from_python(**kwargs)
        if self.variables is None:
            self.variables = []
        if input is not None:
            self._add_input(*input)
        if output is not None:
            self._add_output(*output)

    def _add_input(self, *variables):
        self.variables += [v.to_viya("input") for v in variables]

    def _add_output(self, *variables):
        self.variables += [v.to_viya("output") for v in variables]

    def update(self, **kwargs):
        if not self.etag:
            raise ViyaException("ETag is not set")
        self.from_python(**kwargs)
        return self._client.update_project(self)

    def delete(self):
        self._client.delete_project(self)

    def create_model(self, files=None, **kwargs):
        kwargs["project_id"] = self.id

        # Inherit properties from project if not explicitly defined
        if "input" not in kwargs:
            kwargs["input_variables"] = [{"name": v.get("name"), "type": v.get("type"), "role": v.get("role"),
                                          "description": v.get("description"), "level": v.get("level")}
                                         for v in self.variables if v.get("role") == "input"]
        if "output" not in kwargs:
            kwargs["output_variables"] = [{"name": v.get("name"), "type": v.get("type"), "role": v.get("role"),
                                           "description": v.get("description"), "level": v.get("level")}
                                          for v in self.variables if v.get("role") == "output"]

        # inherit project keys that match model keys
        for attr in ("description", "function", "target_level", "target_variable"):
            if attr not in kwargs:
                kwargs[attr] = getattr(self, attr, None)

        # special cases where model key doesn't match project key
        if "target_event" not in kwargs:
            kwargs["target_event"] = self.target_event_value
        if "event_prob_var" not in kwargs:
            kwargs["event_prob_var"] = self.event_probability_variable

        model = Model(self._client, **kwargs)
        self._client.create_model(model)
        if files:
            model.add_files(*files)
        return model

    def create_performance_definition(self, **kwargs):
        kwargs["project_id"] = self.id

        # Inherit properties from project if not explicitly defined
        if 'input' not in kwargs and 'input_variables' not in kwargs:
            kwargs["input_variables"] = [v.get("name") for v in self.variables if v.get("role") == "input"]
        if 'output' not in kwargs and 'output_variables' not in kwargs:
            kwargs["output_variables"] = [self.event_probability_variable]

        definition = PerformanceDefinition(self._client, **kwargs)
        return self._client.create_performance_definition(definition)


class Model(BaseObject):

    _defaults = {
        'score_code_type': 'Python',
        'train_code_type': 'Python',
        'tool': f"Python {sys.version_info.major}",
        'tool_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"}

    def from_python(self, input=None, output=None, **kwargs):
        super(Model, self).from_python(**kwargs)
        if self.input_variables is None:
            self.input_variables = []
        if self.output_variables is None:
            self.output_variables = []
        if input:
            self._add_input(*input)
        if output:
            self._add_output(*output)

    def _add_input(self, *variables):
        self.input_variables += [v.to_viya("input") for v in variables]

    def _add_output(self, *variables):
        self.output_variables += [v.to_viya("output") for v in variables]

    def add_files(self, *files):
        content_list = []
        for file in files:
            if isinstance(file, (list, tuple)):
                if len(file) == 2:
                    file_name, binary = file
                    role = None
                if len(file) == 3:
                    file_name, binary, role = file
            else:
                file_name, binary, role = file, False, None
            content = self.add_file(file_name, binary, role)
            content_list.append(content)
        return content_list

    def add_file(self, file, binary=False, role=None):
        if self.id is None:
            raise ViyaException("The model needs to be created before adding files.")
        return self._client.create_file(self, file, binary, role)

class File(BaseObject):
    pass

class PerformanceDefinition(BaseObject):

    _defaults = {
        'data_prefix': 'pythonperfs',
        'performance_result_saved': True,
        'score_execution_required': False,
        'trace_on': False,
        'max_bins': 10,
        'result_library': 'ModelPerformanceData',
        'cas_server_id': 'cas-shared-default',
        'data_library': 'Public',
        'include_all_data': False,
        'load_performance_result': True,
        'champion_monitored': False,
        'challenger_monitored': False}

    def from_python(self, models=None, input=None, output=None, **kwargs):
        super(PerformanceDefinition, self).from_python(**kwargs)
        if isinstance(models, (list, tuple)):
            self.model_ids = [model.id if isinstance(model, Model) else model for model in models]
        if input:
            self.input_variables = [v.name for v in input]
        if output:
            self.output_variables = [v.name for v in output]

    def execute_performance_definition(self):
        self._client.execute_performance_definition(self)

class PerformanceJob(BaseObject):
        # this is returned from executing the performance task - from API doc:
        # performance job
        # job execution results that includes the code, log, and job status (state).
    pass
