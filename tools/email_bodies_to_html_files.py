"""Save the cached email bodies as HTML files, which can then be examined/explored with
BeautifulSoup, to determine how to extract the needed data.
"""

import os
import glob
import json
from pathlib import Path

CACHE_DIR = os.path.expanduser('~/.cache/grubhub-dl/')
CACHE_DIR_EMAILS = os.path.join(CACHE_DIR, 'emails')
CACHE_DIR_EMAIL_BODIES = os.path.join(CACHE_DIR, 'email_bodies')


def email_bodies_to_html_files():
    email_files = glob.glob(os.path.join(CACHE_DIR_EMAILS, '*.json'))
    Path(CACHE_DIR_EMAIL_BODIES).mkdir(parents=True, exist_ok=True)

    for file in email_files:
        data = json.loads(Path(file).read_text())
        body = data['body']
        sent_at = data['sent_at']
        subject = data['subject']
        filename = f'{sent_at}_{subject}.html'
        filepath = os.path.join(CACHE_DIR_EMAIL_BODIES, filename)
        with open(filepath, 'w') as file:
            if body:
                file.write(body)
                print(f'{filename}: Saved {len(body)} characters to file')


if __name__ == '__main__':
    email_bodies_to_html_files()