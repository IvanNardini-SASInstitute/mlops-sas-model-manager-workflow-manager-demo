import weakref
import requests

from .services.saslogon import SASLogon
from .services.modelmanager import ModelManager
from .exceptions import ViyaException

import logging
logger = logging.getLogger(__name__)


class ViyaClient:

    def __init__(self, viya_url, client_id="sas.ec", client_secret="", token=None):
        """
        :param viya_url: url in the form protocol://host:port to SAS Viya server
        :param client_id: Application client ID
        :param client_secret: Application client secret
        :param token: if a previously retrieved token was persisted, it can be restored using this parameter
        """
        self.viya_url = viya_url
        self.client_id = client_id
        self.client_secret = client_secret

        self.logon = SASLogon(weakref.proxy(self), token)
        self.model_manager = ModelManager(weakref.proxy(self))

    def auth_request(self, verb, service_url, **kwargs):
        """
        Low-level request method to viya for non authenticated requests.

        Mainly used by SASLogon when retrieving an access token.

        :param verb: type of http method to use for request
        :param service_url: url of the service
        :param kwargs: keyword arguments for request
        :return: response
        """
        logger.debug(f"{verb} {service_url}")

        response = requests.request(verb, self.viya_url + service_url, auth=(self.client_id, self.client_secret), **kwargs)

        if not response.ok:
            logger.debug(response.json())
            raise ViyaException(response.json().get('error_description', response.json().get('message')))

        return response

    def request(self, verb, service_url, **kwargs):
        """
        Low-level request method to viya for authenticated requests.

        Mainly used by services requiring an access token.

        :param verb: type of http method to use for request
        :param service_url: url of the service
        :param kwargs: keyword arguments for request
        :return: response
        """
        logger.debug(f"{verb} {service_url} {kwargs}")

        if self.logon.token is None:
            raise ViyaException("the client is not authenticated. Call 'client.logon.authenticate().'")

        headers = {"Authorization": "Bearer " + self.logon.token.get("access_token"),
                   "Content-Type": "application/json"}
        headers.update(kwargs.pop('headers', {}))
        response = requests.request(verb, self.viya_url + service_url, headers=headers, **kwargs)

        if not response.ok:
            logger.debug(response.json())
            raise ViyaException(response.json().get('message', 'No message'))

        return response
