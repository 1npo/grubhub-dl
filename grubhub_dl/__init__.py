"""Defines constants that are used globally throughout ``grubhub-dl``.
"""

import os
from pathlib import Path

DEFAULT_CACHE_DIR = str(Path(os.path.expanduser('~/.cache/grubhub-dl')))
DEFAULT_CONFIG_FILE = str(Path(os.path.expanduser('~/.config/grubhub-dl.ini')))
DEFAULT_KEYRING_SERVICE = 'grubhub-dl'
DEFAULT_KEYRING_USERNAME = 'email-api-access-token'
DEFAULT_DATETIME_FORMAT = '%Y-%m-%d.%I%M%S%p'
DEFAULT_GMAIL_QUERY = 'from:grubhub.com'
ERROR_MESSAGE_FATAL = 'Unable to continue, quitting.'
GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
