"""Parses user arguments and executes the app's logic. The entrypoint for ``grubhub-dl``.

Parameters can be provided as command-line arguments or by configuration file.

If no CLI arguments are provided, parameters will be retrieved from this file, if it
exists: ``~/.config/grubhub-dl/grubhub-dl.ini``.

If CLI arguments are provided, the configuration file will be ignored.

Dependencies
============
- pandas
"""

__version__ = '0.1.0'
__appname__ = 'grubhub-dl'

import os
import time
import sys
import argparse
import logging

import pandas as pd

from grubhub_dl import (
    extract,
    export,
    models,
    DEFAULT_CACHE_DIR,
    DEFAULT_CONFIG_FILE,
    DEFAULT_KEYRING_SERVICE,
    DEFAULT_KEYRING_USERNAME,
    DEFAULT_DATETIME_FORMAT,
    ERROR_MESSAGE_FATAL,
)
from grubhub_dl.validation import validate_enum
from grubhub_dl.emails import cache, gmail

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [ %(levelname)-8s ] %(message)s',
    datefmt='%Y-%m-%d %I:%M:%S %p'
)


def get_grubhub_data(params: models.Parameters) -> pd.DataFrame | None:
    """Execute the app's logic

    1. Get all Grubhub emails from the given source (cached JSON file or an email API)
    1. Categorize all the emails by the pattern of the subject line
    1. Extract the data from the email bodies and load it into dataclasses (the extraction
        logic is different for each email category)
    1. Transform the dataclasses into the desired format
    1. Export the dataclasses to the desired output destination
    
    :param params: The user-provided app parameters
    :returns: A dataframe if the requested output format is a dataframe, otherwise None
    """

    match params.import_from:
        case models.Source.cache:
            emails = cache.get_emails_from_cache(params)
        case models.Source.gmail:
            emails = gmail.get_emails_from_gmail_api(params)
            export.cache_emails(params, emails)
        case _:
            logger.error(
                'Unknown data source (%s). This is unexpected! Please report it!',
                params.import_from
            )
            logger.error(ERROR_MESSAGE_FATAL)
            return None

    if not emails:
        logger.warning('No emails to extract data from. Quitting.')
        return None

    grubhub_data = extract.get_data_from_emails(emails)

    match params.export_to:
        case models.Destination.json:
            export.grubhub_data_to_json(params, grubhub_data)
        case models.Destination.table:
            export.grubhub_data_to_table(params, grubhub_data)
        case models.Destination.json_file:
            export.grubhub_data_to_json_file(params, grubhub_data)
        case models.Destination.csv_file:
            export.grubhub_data_to_csv_file(params, grubhub_data)
        case models.Destination.sqlite:
            export.grubhub_data_to_sqlite(params, grubhub_data)
        case models.Destination.dataframe:
            return export.grubhub_data_to_dataframe(params, grubhub_data)
        case _:
            logger.error(
                'Unknown destination type (%s). This is unexpected! Please report it!',
                params.import_from
            )
            logger.error(ERROR_MESSAGE_FATAL)
            return None


def get_arguments(args: list = None) -> argparse.Namespace:
    """Parse the user-provided arguments
    """

    parser = argparse.ArgumentParser(prog=f'{__appname__} v{__version__}')

    parser_action = parser.add_subparsers(dest='action')
    parser_gmail = parser_action.add_parser('gmail', help='Get emails from the Gmail API')
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Display more verbose debugging information in the output log'
    )
    parser.add_argument(
        '--config',
        metavar='FILE',
        action='store',
        type=str,
        default=DEFAULT_CONFIG_FILE,
        help='Get parameters from this config file.'
    )

    parser.add_argument(
        '--to',
        action='store',
        type=lambda dest: validate_enum(dest, models.Destination),
        default=models.Destination.json,
        help='Export processed Grubhub data in this format'
    )
    parser.add_argument(
        '--path',
        metavar='PATH',
        action='store',
        type=str,
        help='When exporting Grubhub data to a file, export it to the file at this path'
    )
    parser.add_argument(
        '--sqlite-path',
        metavar='PATH',
        action='store',
        type=str,
        help='When exporting Grubhub data to SQLite, export it to the DB at this path'
    )

    parser.add_argument(
        '--email',
        action='store',
        type=str,
        help='Get Grubhub data from emails that were sent to this email address'
    )
    parser.add_argument(
        '--email-creds',
        action='store',
        type=str,
        help='Get email API credentials from this file'
    )

    parser.add_argument(
        '--cache-dir',
        action='store',
        type=str,
        default=DEFAULT_CACHE_DIR,
        help='Store cache files in this directory'
    )
    parser.add_argument(
        '--keyring-service',
        action='store',
        type=str,
        default=DEFAULT_KEYRING_SERVICE,
        help='Cache API authorization in the system keyring using this service name'
    )
    parser.add_argument(
        '--keyring-username',
        action='store',
        type=str,
        default=DEFAULT_KEYRING_USERNAME,
        help='Cache API authorization in the system keyring under this user name'
    )
    parser.add_argument(
        '--datetime-format',
        action='store',
        type=str,
        default=DEFAULT_DATETIME_FORMAT,
        help='Format all timestamps using this format string'
    )

    namespace, unknown = parser.parse_known_args(args)

    if unknown:
        logger.warning('Ignoring unknown parameters: %s', ','.join(unknown))

    return namespace


def get_parameters(args: list) -> models.Parameters:
    """Get app parameters from the user and validate them.
    """

    namespace = get_arguments(args)

    if namespace.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug('Verbose log output enabled (log_level=DEBUG)')

    params = models.Parameters(
        source=models.Source.cache,
        config_file=namespace.config,
        destination=namespace.to,
        output_path=namespace.path,
        sqlite_path=namespace.sqlite_path,
        email_address=namespace.email,
        email_creds_file=namespace.email_creds,
        cache_dir=namespace.cache_dir,
        keyring_service=namespace.keyring_service,
        keyring_username=namespace.keyring_username,
        datetime_format=namespace.datetime_format,
    )

    if namespace.action:
        if namespace.action == 'gmail':
            params.source = models.Source.gmail





    return params


def main(args: list = None):
    start_time = time.time()

    logger.info('Starting %s v%s', __appname__, __version__)

    df = None

    try:
        params = get_parameters(args)

        logger.debug('source            = %s', params.source)
        logger.debug('config_file       = %s', params.config_file)
        logger.debug('destination       = %s', params.destination)
        logger.debug('output_path       = %s', params.output_path)
        logger.debug('sqlite_path       = %s', params.sqlite_path)
        logger.debug('email_address     = %s', params.email_address)
        logger.debug('email_creds_file  = %s', params.email_creds_file)
        logger.debug('cache_dir         = %s', params.cache_dir)
        logger.debug('keyring_service   = %s', params.keyring_service)
        logger.debug('keyring_username  = %s', params.keyring_username)
        logger.debug('datetime_format   = %s', params.datetime_format)

        df = get_grubhub_data(params)

    except KeyboardInterrupt:
        logger.warning('Received Ctrl-C from user. Quitting...')

    end_time = (time.time() - start_time)
    run_time = time.strftime('%Hh%Mm%Ss', time.gmtime(end_time))

    logger.info('Finished in %s', run_time)

    return df


if __name__ == '__main__':
    main(sys.argv[1:])