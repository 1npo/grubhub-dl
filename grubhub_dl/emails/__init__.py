"""Implements modules that get EmailMessage objects from cached files or email APIs.
"""

from .cache import get_emails_from_cache
from .gmail import get_emails_from_gmail_api

__all__ = ['get_emails_from_cache', 'get_emails_from_gmail_api']
