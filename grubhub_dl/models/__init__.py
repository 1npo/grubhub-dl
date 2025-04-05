"""Defines the data model for ``grubhub-dl``.
"""

from .grubhub import (
    EmailCategory,
    CreditCategory,
    EmailMessage,
    OrderItem,
    OrderUpdate,
    OrderCancellation,
    Order,
    Credit,
)
from .params import (
    Source,
    Destination,
    Parameters,
    VALID_SOURCES,
    VALID_DESTINATIONS,
)

__all__ = [
    'EmailCategory',
    'CreditCategory',
    'EmailMessage',
    'OrderItem',
    'OrderUpdate',
    'OrderCancellation',
    'Order',
    'Credit',
    'Source',
    'Destination',
    'Parameters',
    'VALID_SOURCES',
    'VALID_DESTINATIONS',
]
