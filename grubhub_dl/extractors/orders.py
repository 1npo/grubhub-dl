"""Extracts the data from Grubhub order confirmation email bodies.
"""

import logging

from bs4 import BeautifulSoup

from grubhub_dl import models

logger = logging.getLogger(__name__)


# Example: Thanks for your Pho #1 Brighto_2021-11-02.095336PM.html
def extract_order_confirmation_type_1(row: pd.Series) -> pd.Series:
    if row['category'] == 'order_confirmation':
        try:
            row_restaurant_name = 7
            row_order_total = 8
            row_ordered_at = 9
            row_order_number_and_phone = 10
            row_order_items_start = 13
            soup = BeautifulSoup(row['body'], 'html.parser')
            table = soup.find_all('table')[1].find_all('td')
            row['restaurant_name'] = table[row_restaurant_name].text.strip()
            row['order_total'] = table[row_order_total].text.split(':')[1].strip()

            try:
                row['ordered_at'] = table[row_ordered_at].text.split(':')[1].strip()
            except Exception as err:
                logger.error(
                    'FAILED TO GET ordered_at !!! err=%s, row=%s, filepath=',
                    err,
                    row,
                    row['file_path']
                )

            row['order_number'] = (
                table[row_order_number_and_phone]
                    .text
                    .split(': ')[1]
                    .split('  ')[1]
            )
            row['restaurant_phone'] = (
                table[row_order_number_and_phone]
                    .text
                    .split(': ')[1]
                    .split('  ')[2]
            )

            item_counter = 0
            item_counting_complete = False
            items = []
            items_buffer = []
            for i in range(row_order_items_start, len(table)):
                if 'Items subtotal' in table[i].text:
                    row['order_subtotal'] = table[i+1].text.strip()
                    item_counting_complete = True
                if 'Service fee' in table[i].text:
                    row['order_service_fee'] = table[i+1].text.strip()
                if 'Sales tax' in table[i].text:
                    row['order_sales_tax'] = table[i+1].text.strip()
                if 'Tip' in table[i].text:
                    row['order_delivery_tip'] = table[i+1].text.strip()
                if 'Payment Method' in table[i].text and '$' in table[i].text:
                    row['order_payment_method'] = table[i].text
                if not item_counting_complete:
                    if item_counter == 2:
                        item_counter = 0
                        items.append(items_buffer)
                    else:
                        item_counter += 1
                        items_buffer.append(table[i].text.strip())
            row['order_items'] = [tuple(item) for item in items]
    
        except Exception as err:
            logger.error('FAILED TO PROCESS ROW: confirmation_type_1 !!!')

    # soup.find_all('table')[1].find_all('td')[2].text.replace('\xa0', '\n').split('\n')
    return row


# Example: Your order from Los Amigos is _2021-05-24.111324PM.html
def extract_order_confirmation_type_2(row: pd.Series) -> pd.Series:
    if row['category'] == 'order_confirmation' and 'Your order from ' in row['subject']:
        try:
            soup = BeautifulSoup(row['body'], 'html.parser')
            
            order_details = soup.find_all('table')[11].find_all('td')[0].text
            row['order_number'] = order_details.split('#')[1].strip()
            row['ordered_at'] = (
                order_details.split('#')[0].split('Order Details')[1].strip()
            )
            row['order_total'] = soup.find_all('table')[15].find_all('td')[1].text.strip()

            row['restaurant_name'] = None
            row['restaurant_phone'] = None

            order_summary = soup.find_all('table')[14].find_all('td')
            for i, line in enumerate(order_summary):
                if line.strip() == 'Items subtotal':
                    row['order_subtotal'] = order_summary[i+1].text.strip()
                if line.strip() == 'Delivery fee':
                    row['order_delivery_fee'] = order_summary[i+1].text.strip()
                if line.strip() == 'Service fee':
                    row['order_service_fee'] = order_summary[i+1].text.strip()
                if line.strip() == 'Sales tax':
                    row['order_sales_tax'] = order_summary[i+1].text.strip()
                if line.strip() == 'Tip':
                    row['order_delivery_tip'] = order_summary[i+1].text.strip()

            item_counter = 0
            items = []
            items_buffer = []
            items_table = soup.find_all('table')[13].find_all('td')
            for item in items_table:
                item = item.text.strip()
                item_counter += 1
                if item_counter <= 3:
                    items_buffer.append(item)
                if item_counter == 3:
                    item_counter = 0
                    items.extend(items_buffer)

            row['order_items'] = items
        except Exception as err:
            logger.error('FAILED TO PROCESS ROW: confirmation_type_2 !!!')
    return row

# Example: Thanks for your Pho 1 Waltham _2025-03-05.094904PM.html
def extract_order_confirmation_type_3(row: pd.Series) -> pd.Series:
    # order_items
    #   soup.find_all('table')[9].find_all('td')
    if row['category'] == 'order_confirmation' and 'Thanks for your ' in row['subject']:
        try:
            soup = BeautifulSoup(row['body'], 'html.parser')
            
            order_details = soup.find_all('table')[6].find_all('td')
            row['ordered_at'] = order_details[2].strip(':')[1].strip()
            row['order_number'] = (
                order_details[3]
                    .text
                    .split('Order number:')[1]
                    .split('Contact Restaurant:')[1]
                    .strip()
            )
            row['order_total'] = soup.find_all('table')[11].find_all('td')[1]

            row['restaurant_name'] = order_details[0].text.strip()
            row['restaurant_phone'] = (
                order_details[3].text.split('Contact Restaurant:')[1].strip()
            )

            order_summary = soup.find_all('table')[10].find_all('td')
            for i, line in enumerate(order_summary):
                if line.strip() == 'Items subtotal':
                    row['order_subtotal'] = order_summary[i+1].text.strip()
                if line.strip() == 'Delivery fee':
                    row['order_delivery_fee'] = order_summary[i+1].text.strip()
                if line.strip() == 'Service fee':
                    row['order_service_fee'] = order_summary[i+1].text.strip()
                if line.strip() == 'Sales tax':
                    row['order_sales_tax'] = order_summary[i+1].text.strip()
                if line.strip() == 'Tip':
                    row['order_delivery_tip'] = order_summary[i+1].text.strip()

            item_counter = 0
            items = []
            items_buffer = []
            items_table = soup.find_all('table')[9].find_all('td')
            for item in items_table:
                item = item.text.strip()
                item_counter += 1
                if item_counter <= 3:
                    items_buffer.append(item)
                if item_counter == 4:
                    item_counter = 0
                    items.extend(items_buffer)

            row['order_items'] = items
        except Exception as err:
            logger.error('FAILED TO PROCESS ROW: confirmation_type_2 !!!')
    return row
