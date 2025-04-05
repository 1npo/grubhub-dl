"""Set up an IPython session to examine/step through the HTML elements of an email body.

Example
=======
.. code-block:: ipython
    
    %run tools/explore_email_bodies.py

    soup = explore_file("email_body.html")

    soup.find_all('table')

"""

import os
from pathlib import Path
from bs4 import BeautifulSoup

def explore_file(file) -> BeautifulSoup:
    email_bodies_dir = os.path.expanduser('~/.cache/grubhub-dl/email_bodies/')
    email_body_filepath = os.path.join(email_bodies_dir, file)
    email_body = Path(email_body_filepath).read_text()
    soup = BeautifulSoup(email_body, 'html.parser')
    return soup

