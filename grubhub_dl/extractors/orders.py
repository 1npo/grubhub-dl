"""Extracts the data from Grubhub order confirmation email bodies.

Dependencies
============
- beautifulsoup4
"""

import logging
from datetime import datetime
from dataclasses import replace

from bs4 import BeautifulSoup, element

from grubhub_dl import models

logger = logging.getLogger(__name__)


# Needed fields
# [x] email_id
# [x] restaurant_name
# [x] restaurant_phone
# [x] ordered_at
# [x] order_number
# [x] order_subtotal
# [x] order_total
# [x] order_service_fee_original
# [x] order_service_fee_actual
# [x] order_delivery_fee
# [x] order_sales_tax
# [x] order_delivery_tip
# [x] order_payment_method
# [x] order_has_free_delivery
# [x] order_has_promo_code
# [ ] order_items
# [ ] order_subtype
# [ ] subject
# [ ] category
# [ ] cache_file

def extract_order_payment_method_details(
    soup: BeautifulSoup,
    order: models.Order
) -> models.Order:
    """Try to extract the data for the following fields:

    - order_payment_method
    - order_has_free_delivery
    - order_has_promo_code
    """

    try:
        table = soup.find_all('table')[1].find_all('td')
        for i in range(13, len(table)):
            if 'Payment Method' in table[i].text and '$' in table[i].text:
                payment_method_data = table[i].text

                # TODO: Parse out payment method, card number, and charged amount
                order.order_payment_method = payment_method_data

                if any([
                    'PROMO CODE' in payment_method_data.upper(),
                    'REWARD' in payment_method_data.upper()
                ]):
                    order.order_has_promo_code = True
                
                if any([
                    'GH+ $0 DELIVERY' in payment_method_data.upper(),
                    'FREE DELIVERY' in payment_method_data.upper(),
                ]):
                    order.order_has_free_delivery = True
        return order
    except Exception:
        pass

    try:
        pass
    except Exception:
        pass

    try:
        pass
    except Exception:
        pass

    logger.debug('Failed to get payment method details from order confirmation email')
    return order


def extract_order_total(soup: BeautifulSoup, order: models.Order) -> models.Order:
    """Try to extract the data for the ``order_total`` field.
    """

    try:
        order_total = (
            soup
                .find_all('table')[1]
                .find_all('td')[8]
                .text
                .split(':')[1]
                .strip()
                .replace('$', '')
                .replace('.', '')
        )
        order.order_total = int(order_total)
        return order
    except Exception:
        pass

    try:
        order_total = (
            soup
                .find_all('table')[15]
                .find_all('td')[1]
                .text
                .strip()
                .replace('$', '')
                .replace('.', '')
        )
        order.order_total = int(order_total)
        return order
    except Exception:
        pass

    try:
        order_total = (
            soup
                .find_all('table')[11]
                .find_all('td')[1]
                .text
                .strip()
                .replace('$', '')
                .replace('.', '')
        )
        order.order_total = int(order_total)
        return order
    except Exception:
        pass
    
    logger.debug('Failed to get "order_total" from order confirmation email')
    return order


def process_summary_lines(summary: element.ResultSet, start: int = 0) -> dict:
    """Helper function used by ``extract_order_summary``
    """
    
    summary_data = {}
    for i in range(start, len(summary)):
        line = summary[i].text
        if 'items subtotal' in line.strip().lower():
            summary_data['order_subtotal'] = summary[i+1].text.strip()
        if 'delivery fee' in line.strip().lower():
            value = summary[i+1].text.strip()
            if value.count('$') == 2:
                segments = value.split(' ')
                summary_data['order_delivery_fee_original'] = segments[0]
                summary_data['order_delivery_fee_actual'] = segments[-1]
            else:
                summary_data['order_delivery_fee_actual'] = value
        if 'service fee' in line.strip().lower():
            value = summary[i+1].text.strip()
            if value.count('$') == 2:
                segments = value.split(' ')
                summary_data['order_service_fee_original'] = segments[0]
                summary_data['order_service_fee_actual'] = segments[-1]
            else:
                summary_data['order_service_fee_actual'] = value
        if 'sales tax' in line.strip().lower():
            summary_data['order_sales_tax'] = summary[i+1].text.strip()
        if 'tip' in line.strip().lower():
            summary_data['order_delivery_tip'] = summary[i+1].text.strip()
    
    # logger.warning('summary_data=%s', summary_data)
    return summary_data


def add_summary_data_to_order(summary_data: dict, order: models.Order) -> models.Order:
    """Helper function used by ``extract_order_summary``
    """
    #required_fields = [
    #    'order_subtotal',
    #    'order_delivery_fee_actual',
    #    'order_delivery_tip',
    #    'order_service_fee_actual',
    #]
    #for field in required_fields:
    #    if field not in summary_data or not summary_data[field]:
    #        raise KeyError
    
    for field in summary_data:
        summary_data[field] = int(summary_data[field].replace('$', '').replace('.', ''))
    
    order = replace(order, **summary_data)
    return order
    

def extract_order_summary(soup: BeautifulSoup, order: models.Order) -> models.Order:
    """Try to extract the data for the following fields:
    
    - order_subtotal
    - order_service_fee_original
    - order_service_fee_actual
    - order_delivery_fee
    - order_sales_tax
    - order_delivery_tip
    """

    try:
        summary = soup.find_all('table')[1].find_all('td')
        summary_data = process_summary_lines(summary, start=13)
        order = add_summary_data_to_order(summary_data, order)
        return order
    except Exception as err:
        #logger.warning('EXTRACT SUMMARY: ATTEMPT 1 FAIL: %s', err)
        pass

    try:
        summary = soup.find_all('table')[14].find_all('td')
        summary_data = process_summary_lines(summary)
        order = add_summary_data_to_order(summary_data, order)
        return order
    except Exception as err:
        #logger.warning('EXTRACT SUMMARY: ATTEMPT 2 FAIL: %s', err)
        pass

    try:
        summary = soup.find_all('table')[10].find_all('td')
        summary_data = process_summary_lines(summary)
        order = add_summary_data_to_order(summary_data, order)
        return order
    except Exception as err:
        #logger.warning('EXTRACT SUMMARY: ATTEMPT 3 FAIL: %s', err)
        pass
    
    logger.debug('Failed to get order summary fields from order confirmation email')
    return order


def extract_restaurant_phone(soup: BeautifulSoup, order: models.Order) -> models.Order:
    """Try to extract the data for the ``restaurant_phone`` field.
    """
    
    try:
        order.restaurant_phone = (
            soup
                .find_all('table')[1]
                .find_all('td')[10]
                .text
                .split(': ')[2]
                .strip()
        )
    except Exception:
        pass

    try:
        order.restaurant_phone = (
            soup
                .find_all('table')[6]
                .find_all('td')[3]
                .text
                .split('Contact Restaurant:')[1]
                .strip()
        )
    except Exception:
        pass
    
    # TODO: Is a third method needed? Find out

    logger.debug('Failed to get "restaurant_phone" from order confirmation email')
    return order


def extract_restaurant_name(soup: BeautifulSoup, order: models.Order) -> models.Order:
    """Try to extract the data for the ``restaurant_name`` field.
    """
    
    try:
        order.restaurant_name = (
            soup
                .find_all('table')[1]
                .find_all('td')[7]
                .text
                .strip()
        )
        return order
    except Exception:
        pass

    try:
        order.restaurant_name = (
            soup
                .find_all('table')[6]
                .find_all('td')[0]
                .text
                .strip()
        )
    except Exception:
        pass

    # TODO: Is a third method needed? Find out

    logger.debug('Failed to get "restaurant_name" from order confirmation email')
    return order


def extract_order_number(soup: BeautifulSoup, order: models.Order) -> models.Order:
    """Try to extract the data for the ``order_number`` field.
    """
    
    try:
        order.order_number = (
            soup
                .find_all('table')[1]
                .find_all('td')[10]
                .text
                .split(': ')[1]
                .split('  ')[1]
                .replace('#', '')
                .strip()
        )
        return order
    except Exception:
        pass

    try:
        order.order_number = (
            soup
                .find_all('table')[11]
                .find_all('td')[0]
                .text
                .split('#')[1]
                .replace('#', '')
                .strip()
        )
        return order
    except Exception:
        pass

    try:
        order.order_number = (
            soup
                .find_all('table')[6]
                .find_all('td')[3]
                .text
                .split('Order number:')[1]
                .split('Contact Restaurant:')[1]
                .replace('#', '')
                .strip()
        )
        return order
    except Exception:
        pass

    logger.debug('Failed to get "order_number" from order confirmation email')
    return order


def extract_ordered_at(soup: BeautifulSoup, order: models.Order) -> models.Order:
    """Try to extract the data for the ``ordered_at`` field.
    """
    
    try:
        value = (
            soup
                .find_all('table')[1]
                .find_all('td')[9]
                .text
                .split('Ordered:')[1]
                .strip()
        )
        order.ordered_at = datetime.strptime(value, '%b %d, %Y %I:%M:%S%p')
        return order
    except Exception:
        pass

    try:
        value = (
            soup
                .find_all('table')[11]
                .find_all('td')[0]
                .text
                .split('#')[0]
                .split('Order Details')[1]
                .strip()
        )
        order.ordered_at = datetime.strptime(value, '%b %d, %Y %I:%M:%S%p')
        return order
    except Exception:
        pass

    try:
        value = (
            soup
                .find_all('table')[6]
                .find_all('td')[2]
                .split('Ordered:')[1]
                .strip()
        )
        order.ordered_at = datetime.strptime(value, '%b %d, %Y %I:%M:%S%p')
        return order
    except Exception:
        pass

    logger.debug('Failed to get "ordered_at" from order confirmation email')
    return order


def extract_order_confirmation(email: models.EmailMessage) -> models.Order:
    """
    """

    if email.category == models.EmailCategory.order_confirmation:
        soup = BeautifulSoup(email.body, 'html.parser')
        order = models.Order(email_id=email.email_id)
        order = extract_ordered_at(soup, order)
        order = extract_order_number(soup, order)
        order = extract_restaurant_name(soup, order)
        order = extract_restaurant_phone(soup, order)
        order = extract_order_summary(soup, order)
        order = extract_order_total(soup, order)
        order = extract_order_payment_method_details(soup, order)
        # order = extract_order_items(soup, order)
        return order
