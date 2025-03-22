"""Categorizes Grubhub emails and applies the appropriate data extractors to each email,
based on its category.
"""

from grubhub_dl import models
from grubhub_dl import extractors


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

    return email


def get_data_from_emails(
    emails: list[models.EmailMessage]
) -> tuple[list[models.Order], list[models.Credit]]:
    """
    """
    
    grubhub_orders = []
    grubhub_credits = []

    for email in emails:
        email = categorize_email(email)
        
        order = None
        for func in (
            extractors.order.extract_order_confirmation_type_1,
            extractors.order.extract_order_confirmation_type_2,
            extractors.order.extract_order_confirmation_type_3,
        ):
            try:
                order = func()(email)
                break
            except Exception as err:
                pass
        
        order_updates = extractors.updates.extract_order_updates(email)
        order_cancellation = extractors.cancellations.extract_order_cancellation(email)

        order = build_grubhub_order(order, order_updates, order_cancellation)

        credit_dollars_off = extractors.credits.extract_credit_dollars_off(email)
        credit_guarantee_perk = extractors.credits.extract_credit_guarantee_perk(email)
        credit_discount = extractors.credits.extract_credit_discounted(email)

        if isinstance(order, models.Order):
            grubhub_orders.append(order)

        for credit in (credit_dollars_off, credit_guarantee_perk, credit_discount):
            if isinstance(credit, models.Credit):
                grubhub_credits.append(credits)
    
