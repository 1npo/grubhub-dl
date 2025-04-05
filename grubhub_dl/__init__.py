"""Defines constants that are used globally throughout ``grubhub-dl``.
"""

import os
import typing as t
from pathlib import Path

from grubhub_dl import models

__version__ = '0.1.0'
__appname__ = 'grubhub-dl'

DEFAULT_SOURCE = models.Source.cache
DEFAULT_DESTINATION = models.Destination.json
DEFAULT_CACHE_DIR = str(Path(os.path.expanduser('~/.cache/grubhub-dl')))
DEFAULT_KEYRING_SERVICE = 'grubhub-dl'
DEFAULT_KEYRING_USERNAME = 'email-api-access-token'
DEFAULT_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'
DEFAULT_GMAIL_QUERY = 'from:grubhub.com'
ERROR_MESSAGE_FATAL = 'Unable to continue, quitting.'
GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class Dataclass(t.Protocol):
    """A generic type hint for dataclasses"""
    __dataclass_fields__: t.ClassVar[t.Dict[str, t.Any]]
