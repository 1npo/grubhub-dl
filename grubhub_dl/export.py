"""Exports EmailMessage objects to various different formats.
"""

import os
import json
import logging
from dataclasses import asdict
from pathlib import Path

from grubhub_dl import models

logger = logging.getLogger(__name__)


def cache_emails(params: models.Parameters, emails: list[models.EmailMessage]):
    """Cache each EmailMessage as a JSON object in the user's cache directory
    
    :param params: The user-provided app parameters
    :param emails: A list of EmailMessage objects that were retrieved from an email API
    """

    output_dir = os.path.join(params.cache_dir, 'emails')
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    for i, email in enumerate(emails, start=1):
        if isinstance(email, models.EmailMessage):
            sent_at = email.sent_at.strftime(params.datetime_format)
            file_name = f'{sent_at}_{email.subject}.json'
            file_path = str(Path(output_dir) / file_name)

            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(json.dumps(asdict(email)))
                    logger.info(
                        'Saved email message %s of %s: %s',
                        i,
                        len(emails),
                        file_path,
                    )


def grubhub_data_to_json(params: models.Parameters, grubhub_data):
    pass


def grubhub_data_to_csv(params: models.Parameters, grubhub_data):
    pass


def grubhub_data_to_sqlite(params: models.Parameters, grubhub_data):
    pass


def grubhub_data_to_postgres(params: models.Parameters, grubhub_data):
    pass


def grubhub_data_to_dataframe(params: models.Parameters, grubhub_data) -> pd.DataFrame:
    pass
