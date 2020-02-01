import logging
logger = logging.getLogger(__name__)


class SASLogon:

    service_url = "/SASLogon/oauth/token"

    def __init__(self, client, token=None):
        """
        :param base_url: http/https url to a sas viya server
        """
        self.client = client
        self.token = token

    def authenticate(self, username, password):
        """
        Retrieve an access token from the SASLogon service

        :param username: Username for a user or service account
        :param password: Password for a user or a service account
        :return dict: Dictionary including the access token used to authenticate to other services and a refresh token
        """
        response = self.client.auth_request('post', self.service_url,
                                            data={"grant_type": "password",
                                                  "username": username,
                                                  "password": password})
        self.token = response.json()
        logger.info(f"Token retrieved successfully (expires in: {self.token.get('expires_in')})")
        return self.token

    def refresh(self):
        """
        Retrieve an access token from the SASLogon service using a refresh token

        :return dict: Dictionary including the access token used to authenticate to other services and a refresh token
        """
        response = self.client.auth_request('post', self.service_url,
                                            data={"grant_type": "refresh_token",
                                                  "refresh_token": self.token.get('refresh_token', None)})
        self.token = response.json()
        logger.info(f"Token retrieved successfully (expires in: {self.token.get('expires_in')})")
        return self.token
