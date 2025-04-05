"""Caches EmailMessages to JSON files, and retrieves EmailMessages from cache files.
"""

import os
import json
import glob
import logging
from pathlib import Path
from dataclasses import asdict

from grubhub_dl import models

logger = logging.getLogger(__name__)


def emails_to_json_files(params: models.Parameters, emails: list[models.EmailMessage]):
    """Cache each EmailMessage as a JSON object in the user's cache directory
    
    :param params: The user-provided app parameters
    :param emails: A list of EmailMessage objects that were retrieved from an email API
    """

    output_dir = os.path.join(params.cache_dir, 'emails')
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    for i, email in enumerate(emails, start=1):
        if isinstance(email, models.EmailMessage):
            email.sent_at = email.sent_at.strftime(params.datetime_format)
            file_name = f'{email.sent_at}_{email.subject}.json'
            file_path = str(Path(output_dir) / file_name)
            email.cache_file = file_name

            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump(asdict(email), file)
                    logger.debug(
                        'Saved email message %s of %s: %s',
                        i,
                        len(emails),
                        file_path,
                    )
    logger.info('Saved %s emails to %s', len(emails), output_dir)


def json_files_to_emails(params: models.Parameters):
    """Retrieve EmailMessages from cached JSON files
    """

    email_file_dir = os.path.join(params.cache_dir, 'emails')
    email_files = glob.glob(os.path.join(email_file_dir, '*.json'))
    emails = [json.loads(Path(file).read_text()) for file in email_files]
    emails = [models.EmailMessage(**email) for email in emails]
    logger.info('Retrieved %s emails from cached JSON files', len(emails))
    return emails
