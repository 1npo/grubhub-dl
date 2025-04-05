"""Parses user arguments and runs the app's logic. The entrypoint for ``grubhub-dl``.

Dependencies
============
- pandas
"""

import os
import sys
import argparse
import logging
import pprint
from dataclasses import asdict
from datetime import datetime, timedelta

import pandas as pd

from grubhub_dl import (
    process,
    models,
    config,
    __version__,
    __appname__,
    DEFAULT_SOURCE,
    DEFAULT_DESTINATION,
    DEFAULT_CACHE_DIR,
    DEFAULT_KEYRING_SERVICE,
    DEFAULT_KEYRING_USERNAME,
    DEFAULT_DATETIME_FORMAT,
    ERROR_MESSAGE_FATAL,
)

from grubhub_dl.export import export
from grubhub_dl.validation import validate_enum
from grubhub_dl.emails import cache, gmail

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [ %(levelname)-8s ] %(message)s',
    datefmt='%Y-%m-%d %I:%M:%S %p'
)


def get_grubhub_data(params: models.Parameters) -> pd.DataFrame | None:
    """Run the app's logic

    1. Get all Grubhub emails from the given source (cached JSON file or an email API)
    1. Categorize all the emails by the pattern of the subject line
    1. Extract the data from the email bodies and load it into dataclasses (the extraction
        logic is different for each email category)
    1. Transform the dataclasses into the desired format
    1. Export the dataclasses to the desired output destination
    
    :param params: The user-provided app parameters
    :returns: A dataframe if the requested output format is a dataframe, otherwise None
    """

    # Get email messages
    match params.source:
        case models.Source.cache:
            emails = cache.json_files_to_emails(params)
        case models.Source.gmail:
            emails = gmail.get_emails_from_gmail_api(params)
            cache.emails_to_json_files(params, emails)
        case _:
            logger.error(
                'Unknown data source (%s). This is unexpected! Please report it!',
                params.source
            )
            logger.error(ERROR_MESSAGE_FATAL)
            return None

    if not emails:
        logger.warning('No emails to extract data from. Quitting.')
        return None

    # Transform email messages into a list of dataclasses
    grubhub_data = process.extract_data_from_emails(params, emails)
    
#    grubhub_data = {
#        'emails':               [],
#        'orders':               [],
#        'order_items':          [],
#        'order_updates':        [],
#        'order_cancellations':  [],
#        'credits':              [],
#    }

    records_emails = [asdict(r) for r in grubhub_data['emails']]
    records_orders = [asdict(r) for r in grubhub_data['orders']]
    records_order_items = [asdict(r) for r in grubhub_data['order_items']]
    records_order_updates = [asdict(r) for r in grubhub_data['order_updates']]
    records_order_cancellations = [asdict(r) for r in grubhub_data['order_cancellations']]
    records_credits = [asdict(r) for r in grubhub_data['credits']]

    df_emails = pd.DataFrame.from_dict(records_emails)
    df_orders = pd.DataFrame.from_dict(records_orders)
    df_order_items = pd.DataFrame.from_dict(records_order_items)
    df_order_updates = pd.DataFrame.from_dict(records_order_updates)
    df_order_cancellations = pd.DataFrame.from_dict(records_order_cancellations)
    df_credits = pd.DataFrame.from_dict(records_credits)

    orders_field_subset = [
        'email_id',
        'order_number',
    ]
    df_emails = df_emails.merge(df_orders[orders_field_subset], how='left', on='email_id')

    emails_field_subset = [
        'email_id',
        'subject',
        'category',
        'cache_file',
    ]
    df_orders = df_orders.merge(df_emails[emails_field_subset], how='left', on='email_id')

    today = datetime.now().strftime('%Y-%m-%d_%I%M%S%p')
    output_dir = '/home/nick/grubhub_data_debug/'
    debug_file = os.path.join(output_dir, f'grubhub_dl_debug_{today}.xlsx')
    with pd.ExcelWriter(debug_file, engine='xlsxwriter') as writer:
        df_emails.to_excel(writer, index=False, sheet_name='emails')
        df_orders.to_excel(writer, index=False, sheet_name='orders')
        df_order_items.to_excel(writer, index=False, sheet_name='order_items')
        df_order_updates.to_excel(writer, index=False, sheet_name='order_updates')
        df_order_cancellations.to_excel(writer, index=False, sheet_name='order_cancellations')
        df_credits.to_excel(writer, index=False, sheet_name='credits')

    #exit(0)

    # Load the dataclasses
    match params.destination:
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
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Display more verbose debugging information in the output log'
    )
    parser.add_argument(
        '--config-file',
        metavar='FILE',
        action='store',
        type=str,
        help='Get parameters from this config file.'
    )
    parser.add_argument(
        '--source',
        action='store',
        type=lambda src: validate_enum(src, models.Source),
        default=DEFAULT_SOURCE,
        help='Get Grubhub data from this source'
    )
    parser.add_argument(
        '--destination',
        action='store',
        type=lambda dest: validate_enum(dest, models.Destination),
        default=DEFAULT_DESTINATION,
        help='Export processed Grubhub data in this format'
    )
    parser.add_argument(
        '--output-path',
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
        '--email-address',
        action='store',
        type=str,
        help='Get Grubhub data from emails that were sent to this email address'
    )
    parser.add_argument(
        '--email-creds-file',
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
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug('Verbose log output enabled (log_level=DEBUG)')

    if namespace.config_file and os.path.exists(namespace.config_file):
        params = config.config_to_params(namespace.config_file)
        return params
    
    if namespace.source == models.Source.gmail:
        if not namespace.email_address:
            logger.error('An email address must be provided when the source is "gmail".')
            exit(1)
        if not namespace.email_creds_file:
            logger.error(
                ('A JSON file containing your credentials for accessing the Gmail API '
                'must be provided when the source is "gmail".')
            )
            exit(1)
    
    if namespace.destination and 'file' in namespace.destination.name:
        if not namespace.output_path:
            logger.error(
                'An output path must be specified when the destination is "%s"',
                namespace.destination
            )
            exit(1)

    return models.Parameters(
        source=namespace.source,
        config_file=namespace.config_file,
        destination=namespace.destination,
        output_path=namespace.output_path,
        sqlite_path=namespace.sqlite_path,
        email_address=namespace.email_address,
        email_creds_file=namespace.email_creds_file,
        cache_dir=namespace.cache_dir,
        keyring_service=namespace.keyring_service,
        keyring_username=namespace.keyring_username,
        datetime_format=namespace.datetime_format,
    )


def get_runtime(duration: timedelta) -> str:
    hours = duration.seconds // 3600
    mins = (duration.seconds % 3600) // 60
    secs = duration.seconds % 60
    milisecs = int(f'{duration.microseconds}'[:-3])
    return f'{hours:02d}h {mins:02d}m {secs:02d}s {milisecs}ms'


def main(args: list = None):
    df = None
    
    try:
        started_at = datetime.now()
        params = get_parameters(args)

        logger.info(
            'Starting %s v%s with the following parameters:',
            __appname__,
            __version__
        )
        logger.info('source            = %s', params.source)
        logger.info('config_file       = %s', params.config_file)
        logger.info('destination       = %s', params.destination)
        logger.info('output_path       = %s', params.output_path)
        logger.info('sqlite_path       = %s', params.sqlite_path)
        logger.info('email_address     = %s', params.email_address)
        logger.info('email_creds_file  = %s', params.email_creds_file)
        logger.info('cache_dir         = %s', params.cache_dir)
        logger.info('keyring_service   = %s', params.keyring_service)
        logger.info('keyring_username  = %s', params.keyring_username)
        logger.info('datetime_format   = %s', params.datetime_format)

        df = get_grubhub_data(params)

    except KeyboardInterrupt:
        logger.warning('Received Ctrl-C from user. Quitting...')

    duration = (datetime.now() - started_at)

    logger.info('Finished in %s', get_runtime(duration))

    return df or None


if __name__ == '__main__':
    main(sys.argv[1:])