"""Extracts the data from Grubhub order cancellations email bodies.
"""

import logging

from bs4 import BeautifulSoup

from grubhub_dl import models

logger = logging.getLogger(__name__)


def extract_order_cancellation(email: models.EmailMessage) -> models.OrderCancellation:
    if email.category == models.EmailCategory.order_canceled:
        cancellation = models.OrderCancellation()
        soup = BeautifulSoup(email.body, 'html.parser')
        try:
            table = soup.find_all('table')[5].find_all('td')
            cancellation.order_number = table[1].text.strip()
            cancellation.amount = table[5].text.strip()
            cancellation.reason = table[3].text.strip()
            return cancellation
        except Exception:
            table = soup.find_all('table')[3].find_all('td')
            cancellation.order_number = table[2].text.strip()
            cancellation.amount = table[6].text.strip()
            cancellation.reason = table[4].text.strip()
            return cancellation
        except Exception as err:
            logger.warning(
                ('Unable to extract cancellation data from file due to an unexpected '
                'email body format. Skipping... (err=%s, email=%s)'),
                err,
                email
            )
