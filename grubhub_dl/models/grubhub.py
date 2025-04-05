"""Defines the Grubhub data and various related enumerations.
"""

from enum import Enum, auto
from datetime import datetime
from dataclasses import dataclass


class EmailCategory(Enum):
    credit_dollars_off = auto()
    credit_discounted = auto()
    credit_guarantee_perk = auto()
    order_confirmation = auto()
    order_canceled = auto()
    order_updated = auto()
    uncategorized = auto()


class CreditCategory(Enum):
    dollars_off = auto()
    discount = auto()
    guarantee_perk = auto()
    order_refund = auto()


@dataclass
class EmailMessage:
    email_id: str
    subject: str
    sent_by: str
    sent_at: datetime
    body: str
    category: EmailCategory = None
    cache_file: str = None


@dataclass
class OrderItem:
    pass


@dataclass
class OrderUpdate:
    email_id: str = None
    order_number: str = None
    refund_amount: str = None
    refund_item: str = None
    refund_reason: str = None
    refund_item_amount: str = None
    refund_fees_amount: str = None
    tip_adjusted_amount: str = None


@dataclass
class OrderCancellation:
    email_id: str = None
    order_number: str = None
    amount: str = None
    reason: str = None


@dataclass
class Order:
    email_id: str = None
    restaurant_name: str = None
    restaurant_phone: str = None
    ordered_at: datetime = None
    order_number: str = None
    order_subtotal: str = None
    order_total: str = None
    order_service_fee_original: str = None
    order_service_fee_actual: str = None
    order_delivery_fee_original: str = None
    order_delivery_fee_actual: str = None
    order_sales_tax: str = None
    order_delivery_tip: str = None
    order_payment_method: str = None
    order_has_free_delivery: bool = None
    order_has_promo_code: bool = None
    order_items: list[str] = None


@dataclass
class Credit:
    email_id: str = None
    amount: str = None
    percent_off: int = None
    percent_off_max_value: int = None
    code: str = None
    expires: datetime = None
    category: CreditCategory = None
