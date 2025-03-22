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


class CreditCategory(Enum):
    dollars_off = auto()
    discount = auto()
    guarantee_perk = auto()
    order_refund = auto()


@dataclass
class EmailMessage:
    id: str
    subject: str
    sent_by: str
    sent_at: datetime
    body: str
    category: EmailCategory = None


@dataclass
class OrderItem:
    pass


@dataclass
class OrderRefund:
    refund_amount: str = None
    refund_item: str = None
    refund_reason: str = None
    refund_item_amount: str = None
    refund_fees_amount: str = None
    tip_adjusted_amount: str = None


@dataclass
class OrderCancellation:
    order_number: str = None
    amount: str = None
    reason: str = None


@dataclass
class Order:
    restaurant_name: str = None
    restaurant_phone: str = None
    ordered_at: datetime
    order_number: str = None
    order_subtotal: str = None
    order_total: str = None
    order_service_fee: str = None
    order_delivery_fee: str = None
    order_sales_tax: str = None
    order_delivery_tip: str = None
    order_items: list[OrderItem] = None
    order_refund: OrderRefund = None
    order_cancellation: OrderCancellation = None


@dataclass
class Credit:
    amount: str = None
    code: str = None
    expires: datetime = None
    category: CreditCategory = None
