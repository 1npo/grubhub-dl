"""Implements modules that get EmailMessage objects from cached files or email APIs.
"""

from .cache import emails_to_json_files, json_files_to_emails
from .gmail import get_emails_from_gmail_api

__all__ = ['emails_to_json_files', 'json_files_to_emails', 'get_emails_from_gmail_api']
