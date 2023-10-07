""" sbb_objects.py
Defines objects used through the software.
"""

from dataclasses import dataclass, field
from typing import List, Self


@dataclass
class OrderLine:
    id: int = 0
    order_id: int = 0
    position: int = 0
    sku: int = 0
    qty_ordered: int = 0
    qty_delivered: int = 0

    def is_like(self, other: Self) -> bool:  # Method to check equality except on OrderLine id
        return (
            (self.order_id == other.order_id)
            and (self.position == other.position)
            and (self.sku == other.sku)
            and (self.qty_ordered == other.qty_ordered)
            and (self.qty_delivered == other.qty_delivered)
        )


@dataclass
class Order:
    id: int = 0
    order_type: str = 0
    entity_id: int = 0
    lines: List[OrderLine] = field(default_factory=list)

    def is_like(self, other: Self) -> bool:  # Method to check equality except on Order id
        return (
            (self.order_type == other.order_type)
            and (self.entity_id == other.entity_id)
            and (self.lines == other.lines)
        )


@dataclass
class StockPosition:
    position: int = 0
    sku: int = 0
    qty: int = 0

