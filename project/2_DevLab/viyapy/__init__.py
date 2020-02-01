from .client import ViyaClient
from .exceptions import ViyaException

import logging
from logging import NullHandler
logging.getLogger(__name__).addHandler(NullHandler())
