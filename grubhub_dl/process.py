"""Categorizes Grubhub emails, applies the appropriate data extractors to each email,
and produces a set of dataclasses that contain the extracted and cleaned data.
"""

import pprint
import logging
from datetime import datetime

from grubhub_dl import models, Dataclass
from grubhub_dl.extractors import (
    cancellations,
    credits,
    orders,
    updates
)

logger = logging.getLogger(__name__)


def build_grubhub_order(
    order: models.Order,
    order_updates: models.OrderUpdate,
    order_cancellations: models.OrderCancellation
):
    """
    """
    pass


def categorize_email(email: models.EmailMessage) -> models.EmailMessage:
    """Determine the category of the given EmailMessage, and add the category Enum to
    the Email Message
    
    These email categories determine which data extraction functions need to be applied to
    the email body.
    """
    
    if 'Enjoy $' in email.subject:
        email.category = models.EmailCategory.credit_dollars_off
    if 'You can now enjoy a discounted' in email.subject:
        email.category = models.EmailCategory.credit_discounted
    if "You're approved for a Grubhub" in email.subject:
        email.category = models.EmailCategory.credit_guarantee_perk
    if any([
        'Thanks for your' in email.subject,
        'your order from' in email.subject.lower()
    ]):
        email.category = models.EmailCategory.order_confirmation
    if 'Your order was canceled' in email.subject:
        email.category = models.EmailCategory.order_canceled
    if 'Your order was updated' in email.subject:
        email.category = models.EmailCategory.order_updated
    
    if not email.category:
        email.category = models.EmailCategory.uncategorized
    return email


def clean_dataclass_fields(params: models.Parameters, obj: Dataclass):
    """Perform some post-extraction cleanup on the newly populated dataclasses
    """
    
    # We want to store the category values as enums (both the name and the value) for use
    # during the extraction process. But once extraction is complete, we only want to keep
    # the name of the enum.
    if hasattr(obj, 'category'):
        obj.category = obj.category.name

    if hasattr(obj, 'order_number'):
        order_number = str(obj.order_number)
        order_number = order_number.replace('#', '')
        if '-' not in order_number:
            order_number = order_number[:8] + '-' + order_number[8:]
        obj.order_number = order_number
    
    timestamp_fields = [
        'expires',
        'ordered_at',
        'sent_at',
    ]
    for field in timestamp_fields:
        if hasattr(obj, field):
            new_value = getattr(obj, field)
            if isinstance(new_value, datetime):
                new_value = new_value.strftime(params.datetime_format)
                setattr(obj, field, new_value)

    integer_fields = [
        'amount',
        'refund_amount',
        'refund_item_amount',
        'refund_fees_amount',
        'tip_adjusted_amount',
        'order_subtotal',
        'order_total',
        'order_service_fee_original',
        'order_service_fee_actual',
        'order_derlivery_fee',
        'order_sales_tax',
        'order_delivery_tip',
        'percent_off',
        'percent_off_max_value',
    ]
    for field in integer_fields:
        if hasattr(obj, field):
            new_value = getattr(obj, field)
            if new_value:
                # new_value = int(new_value.replace('$', '').replace('.', ''))
                pass
            setattr(obj, field, new_value)

    return obj

def extract_data_from_emails(
    params: models.Parameters,
    emails: list[models.EmailMessage]
) -> tuple[list[models.Order], list[models.Credit]]:
    """
    """
    
    grubhub_data = {
        'emails':               [],
        'orders':               [],
        'order_items':          [],
        'order_updates':        [],
        'order_cancellations':  [],
        'credits':              [],
    }

    for i, email in enumerate(emails, start=1):
        email = categorize_email(email)
        if not email.body:
            continue
        
        order = orders.extract_order_confirmation(email)
        order_updates = updates.extract_order_updates(email)
        order_cancellation = cancellations.extract_order_cancellation(email)
        credit_dollars_off = credits.extract_credit_dollars_off(email)
        credit_guarantee_perk = credits.extract_credit_guarantee_perk(email)
        credit_discount = credits.extract_credit_discounted(email)
        
        if email:
            email = clean_dataclass_fields(params, email)
            grubhub_data['emails'].append(email)

        if order:
            order = clean_dataclass_fields(params, order)
            grubhub_data['orders'].append(order)
        
        if order_updates:
            order_updates = clean_dataclass_fields(params, order_updates)
            grubhub_data['order_updates'].append(order_updates)
        
        if order_cancellation:
            order_cancellation = clean_dataclass_fields(params, order_cancellation)
            grubhub_data['order_cancellations'].append(order_cancellation)
        
        if credit_dollars_off:
            credit_dollars_off = clean_dataclass_fields(params, credit_dollars_off)
            grubhub_data['credits'].append(credit_dollars_off)

        if credit_guarantee_perk:
            credit_guarantee_perk = clean_dataclass_fields(params, credit_guarantee_perk)
            grubhub_data['credits'].append(credit_guarantee_perk)

        if credit_discount:
            credit_guarantee_perk = clean_dataclass_fields(params, credit_discount)
            grubhub_data['credits'].append(credit_discount)

    return grubhub_data
