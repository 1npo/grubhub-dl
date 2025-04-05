"""Extracts the data from Grubhub credits/perks email bodies.

Dependencies
============
- beautifulsoup4
"""

from datetime import datetime

from bs4 import BeautifulSoup

from grubhub_dl import models


def extract_credit_dollars_off(email: models.EmailMessage) -> models.Credit | None:
    """
    """
    
    if email.category == models.EmailCategory.credit_dollars_off:
        credit = models.Credit(
            email_id=email.email_id,
            category=models.CreditCategory.dollars_off
        )
        soup = BeautifulSoup(email.body, 'html.parser')
        table = soup.find_all('table')[0].find_all('td')
        credit.amount = int(
            table[3]
                .text
                .strip()
                .split(' ')[0]
                .replace('$', '')
                .replace('.', '')
        )
        credit.expires = datetime.strptime(
            table[4].text.strip(),
            'Expires %B %d, %Y %I:%M%p'
        )
        return credit


def extract_credit_guarantee_perk(email: models.EmailMessage) -> models.Credit | None:
    """
    """
    
    if email.category == models.EmailCategory.credit_guarantee_perk:
        credit = models.Credit(
            email_id=email.email_id,
            category=models.CreditCategory.guarantee_perk
        )
        soup = BeautifulSoup(email.body, 'html.parser')
        table = soup.find_all('table')[6].find_all('td')
        credit.amount = int(
            table[2]
                .text
                .strip()
                .replace('*', '')
                .replace('$', '')
                .replace('.', '')
        )
        credit.code = table[4].text.strip()
        credit.expires = datetime.strptime(
            table[8].text.strip(),
            '%B %d, %Y %I:%M%p'
        )
        return credit


def extract_credit_discounted(email: models.EmailMessage) -> models.Credit | None:
    """
    """
    
    if email.category == models.EmailCategory.credit_discounted:
        credit = models.Credit(
            email_id=email.email_id,
            category=models.CreditCategory.discount
        )
        soup = BeautifulSoup(email.body, 'html.parser')
        body = soup.find_all('body')[0].text
        data = []
        [data.append(line) for line in body.split('\n') if line not in data]
        for i, line in enumerate(data):
            if 'Expires:' in line or 'Expiration Date:' in line:
                credit.expires = datetime.strptime(
                    # "%b %d, %Y %I:%M%p %Z" should be the correct format for this date
                    # string: "Oct 22, 2021 2:15am EDT", but strptime doesn't agree, and
                    # the timezone abbreviation at the end seems to be the culprit.
                    #
                    # I'm just taking the abbreviation off the date string for now with
                    # [:-4]. So this may break if the timezone abbreviation is not exactly
                    # three characters.
                    #
                    # UPDATE 2025-3-16: The timezone is implementation dependent, and on
                    # Windows the timezone is "Eastern Daylight Time", not "EDT". So
                    # strptime will fail on Windows unless we remove the timezone first.
                    line.split(': ')[1][:-4],
                    '%b %d, %Y %I:%M%p'
                )
            if 'Amount:' in line:
                credit.amount = int(
                    line
                        .split(': ')[1]
                        .replace('*', '')
                        .strip()
                        .replace('$', '')
                        .replace('.', '')
                )
            if 'Percent Off:' in line:
                percent_off_line = line.split(': ')[1].replace('*', '').strip()
                percent_off_elem = percent_off_line.split('%')
                credit.percent_off = int(percent_off_elem[0])
                credit.percent_off_max_value = int(
                    percent_off_elem[1]
                        .split(' up to ')[1]
                        .split(' ')[0]
                        .replace('$', '')
                        .replace('.', '')
                )
            if 'Code:' in line:
                credit.code = line.split(': ')[1].strip()

        return credit
