"""Saves parameters to, and loads parameters from, INI configuration files.
"""

import logging
import configparser

from grubhub_dl import (
    models,
    __appname__,
	DEFAULT_SOURCE,
    DEFAULT_DESTINATION,
	DEFAULT_CACHE_DIR,
	DEFAULT_KEYRING_SERVICE,
	DEFAULT_KEYRING_USERNAME,
	DEFAULT_DATETIME_FORMAT,
)

from grubhub_dl.validation import validate_enum

logger = logging.getLogger(__name__)


def config_to_params(config_file: str) -> models.Parameters:
	config = configparser.ConfigParser()

	try:
		config.read(config_file)
	except configparser.ParsingError:
		logger.error('Unable to parse configuration file "%s": %s')
		exit(1)

	if __appname__ not in config:
		logger.error(
			'Unable to get configuration. Expected section "%s" not found in file "%s".',
			__appname__,
			config_file
		)
		exit(1)

	try:
		params = models.Parameters(**dict(config.items(__appname__)))
	except TypeError as err:
		logger.error(
			'Unable to load parameters from configuration file "%s": %s',
			config_file,
			err
		)
		exit(1)

	# For parameters whose values are enums, we need to convert the string value of the
	# enum item to the actual Enum object.
	params.source = validate_enum(params.source, models.Source)
	params.destination = validate_enum(params.destination, models.Destination)

	# Ensure that default values are set on any parameters that have default values but
	# were not provided in the user's config file.
	fields_with_defaults = {
		'source':			DEFAULT_SOURCE,
		'destination':		DEFAULT_DESTINATION,
		'cache_dir':		DEFAULT_CACHE_DIR,
		'keyring_service':	DEFAULT_KEYRING_SERVICE,
		'keyring_username':	DEFAULT_KEYRING_USERNAME,
		'datetime_format':	DEFAULT_DATETIME_FORMAT,
	}
	for field, default in fields_with_defaults.items():
		if getattr(params, field) is None:
			setattr(params, field, default)
	
	logger.debug('Got parameters from config file "%s": %s', config_file, params)
	return params
