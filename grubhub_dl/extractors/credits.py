"""Extracts the data from Grubhub credits/perks email bodies.
"""

from datetime import datetime

from bs4 import BeautifulSoup

from grubhub_dl import models


def extract_credit_dollars_off(email: models.EmailMessage) -> models.Credit | None:
    if email.category == models.EmailCategory.credit_dollars_off:
        credit = models.Credit()
        soup = BeautifulSoup(email.body, 'html.parser')
        table = soup.find_all('table')[0].find_all('td')
        credit.amount = table[3].text.strip().split(' ')[0]
        credit.expires = datetime.strptime(
            table[4].text.strip(),
            'Expires %B %d, %Y %I:%M%p'
        )
        return credit


def extract_credit_guarantee_perk(email: models.EmailMessage) -> models.Credit | None:
    if email.category == models.EmailCategory.credit_guarantee_perk:
        credit = models.Credit()
        soup = BeautifulSoup(email.body, 'html.parser')
        table = soup.find_all('table')[6].find_all('td')
        credit.amount = table[2].text.strip().replace('*', '')
        credit.code = table[4].text.strip()
        credit.expires = datetime.strptime(
            table[8].text.strip(),
            '%B %d, %Y %I:%M%p'
        )
        return credit


def extract_credit_discounted(email: models.EmailMessage) -> models.Credit | None:
    if email.category == models.EmailCategory.credit_discounted:
        credit = models.Credit()
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
            if 'Amount:' in line or 'Percent Off:' in line:
                credit.amount = line.split(': ')[1].replace('*', '').strip()
            if 'Code:' in line:
                credit.code = line.split(': ')[1].strip()
        return credit
