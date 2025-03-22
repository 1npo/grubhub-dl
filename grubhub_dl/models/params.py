"""Defines the user-provided parameters and the enumerations for some parameters.
"""

from dataclasses import dataclass
from enum import Enum, auto


class Source(Enum):
    """Supported data sources to get Grubhub emails from"""
    cache = auto() # default
    gmail = auto()


class Destination(Enum):
    """Supported output types to export Grubhub emails to"""
    json = auto() # default
    table = auto()
    json_file = auto() 
    csv_file = auto()
    dataframe = auto()
    sqlite = auto()


@dataclass
class Parameters:
    """User-provided parameters"""
    source: Source = None
    config_file: str = None
    destination: Destination = None
    output_path: str = None
    sqlite_path: str = None
    email_address: str = None
    email_creds_file: str = None
    cache_dir: str = None
    keyring_service: str = None
    keyring_username: str = None
    datetime_format: str = None


VALID_SOURCES = [src.name for src in Source]
VALID_DESTINATIONS = [dest.name for dest in Destination]
