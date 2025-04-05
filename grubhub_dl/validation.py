"""Provides assorted functions that are used to validate data.
"""

import logging
from enum import Enum, EnumType

from grubhub_dl import ERROR_MESSAGE_FATAL
from grubhub_dl import models

logger = logging.getLogger(__name__)


def validate_enum(name: str, enum_type: EnumType) -> Enum:
    """Get the EnumItem that has the given string from the given EnumType, if valid

    :param name: The name of the item in the given enumeration to get
    :param enum_type: The enumeration that the ``name`` item is expected to be in
    :returns: The EnumItem that has the given ``name``, if it's a valid EnumItem,
        otherwise None
    """

    if name is None:
        return None

    if not isinstance(enum_type, EnumType):
        logger.error(
            ('Can only validate an enumeration, but a %s was provided. This is '
            'unexpected! Please investigate or report this issue.'),
            type(enum_type)
        )
        logger.error(ERROR_MESSAGE_FATAL)
        exit(1)

    if isinstance(name, str):
        # The user should be able to use dashes instead of underscores when providing a
        # Destination type, eg "json-file" instead of "json_file".
        if enum_type == models.Destination:
            name = name.replace('-', '_')
        
        try:
            return enum_type[name]
        except KeyError:
            logger.debug('Item "%s" not found in enumeration %s', name, enum_type)

    if enum_type == models.Source:
        logger.error(
            'Invalid source: %s. Valid data sources are: %s',
            name,
            ', '.join(models.VALID_SOURCES)
        )
    elif enum_type == models.Destination:
        logger.error(
            'Invalid destination: %s. Valid destination formats are: %s',
            name,
            ', '.join(models.VALID_DESTINATIONS)
        )
    logger.error(ERROR_MESSAGE_FATAL)
    exit(1)

