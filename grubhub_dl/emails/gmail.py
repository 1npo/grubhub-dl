"""Gets Grubhub emails via the Gmail API, and loads them into EmailMessage dataclasses.

Dependencies
============
- keyring
- google-api-python-client
- google-auth-oauthlib
- google-auth openpyxl
"""

import os
import json
import base64
import logging
from datetime import datetime

import keyring
from googleapiclient.discovery import build, Resource
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from openpyxl.utils.escape import unescape

from grubhub_dl import (
    models,
    DEFAULT_KEYRING_SERVICE,
    DEFAULT_KEYRING_USERNAME,
    DEFAULT_GMAIL_QUERY,
    GMAIL_SCOPES,
)

logger = logging.getLogger(__name__)


def get_gmail_service(params: models.Parameters) -> Resource:
    """Authenticate with Google in the browser, and cache credentials in the system
    keyring to avoid needing to open the browser and attempting to authenticate every time
    this module is run.
    """

    creds_file = params.credentials_file
    creds = None
    token = keyring.get_password(DEFAULT_KEYRING_SERVICE, DEFAULT_KEYRING_USERNAME)
    if token:
        try:
            creds = Credentials.from_authorized_user_info(json.loads(token))
        except (ValueError, KeyError) as err:
            logger.warning('Unable to load cached credentials: %s', err)

    if not creds or not creds.valid:
        if creds and not creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if os.path.exists(creds_file):
                app_flow = InstalledAppFlow.from_client_secrets_file(
                    creds_file,
                    GMAIL_SCOPES
                )
                creds = app_flow.run_local_server(port=0)

                if hasattr(creds, 'expiry'):
                    expiry = creds.expiry.isoformat()
                else:
                    expiry = None
                
                token = {
                    'token':            creds.token,
                    'refresh_token':    creds.refresh_token,
                    'token_uri':        creds.token_uri,
                    'client_id':        creds.client_id,
                    'client_secret':    creds.client_secret,
                    'scopes':           creds.scopes,
                    'expiry':           expiry,
                }
                keyring.set_password(
                    DEFAULT_KEYRING_SERVICE,
                    DEFAULT_KEYRING_USERNAME,
                    json.dumps(token)
                )

            else:
                logger.error(
                    "Credentials file doesn't exist (%s) Quitting...",
                    creds_file
                )
                exit(1)

    logger.info('Initialized Gmail API service')
    return build('gmail', 'v1', credentials=creds)


def get_grubhub_emails(
    service: Resource,
    query: str = DEFAULT_GMAIL_QUERY
) -> list | None:
    """Get a listing of all Grubhub emails in the user's Gmail inbox"""

    response = service.users().messages().list(userId='me', q=query).execute()
    messages = []

    if 'messages' in response:
        messages.extend(response['messages'])
    
    while 'nextPageToken' in response:
        page_token = response['nextPageToken']
        response = service.users().messages().list(
            userId='me',
            q=query,
            pageToken=page_token
        ).execute()
        if 'messages' in response:
            messages.extend(response['messages'])

    return messages


def get_grubhub_email_contents(service: Resource, message_id: str):
    """Get the contents of the email identified by ``message_id``"""

    message = service.users().messages().get(userId='me', id=message_id).execute()
    headers = message['payload']['headers']

    def get_header_value(headers: list, name: str) -> str | None:
        return next(
            (
                header['value']
                for header in headers
                if header['name'].lower() == name
            ),
            None
        )

    subject = get_header_value(headers, 'subject')
    sent_by = get_header_value(headers, 'from')
    sent_at = get_header_value(headers, 'date')

    if sent_at:
        sent_at = sent_at.replace('(UTC)', '').strip()
        sent_at = datetime.strptime(sent_at, '%a, %d %b %Y %H:%M:%S %z')
    body = None

    if 'body' in message['payload'] and 'data' in message['payload']['body']:
        body = (
            base64.urlsafe_b64decode(message['payload']['body']['data'])
                .decode('utf-8')
        )

    return models.EmailMessage(
        id=message_id,
        subject=subject,
        sent_by=sent_by,
        sent_at=sent_at,
        body=unescape(body) if body else body,
    )


def get_emails_from_gmail_api(params: models.Parameters) -> list:
    service = get_gmail_service(params)
    messages = get_grubhub_emails(service)
    emails = []

    for i, email in enumerate(messages, start=1):
        content = get_grubhub_email_contents(service, message_id=email['id'])
        emails.append(content)
        logger.info(
            'Retrieved email %s: %s: %s',
            i,
            content.sent_at,
            content.subject
        )

    logger.info('Retrieved %s emails and cached them to a spreadsheet', len(emails))
    return emails
