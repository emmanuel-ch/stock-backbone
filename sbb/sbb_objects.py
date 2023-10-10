""" sbb_objects.py
Defines objects used through the software.
"""

from dataclasses import dataclass, field
from typing import Self


@dataclass
class OrderLine:
    id: int = None
    order_id: int = None
    position: int = None
    sku: int = None
    qty_ordered: int = None
    qty_delivered: int = None

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
    id: int = None
    order_type: str = None
    entity_id: int = None
    lines: list[OrderLine] = field(default_factory=list)

    def is_like(self, other: Self) -> bool:  # Method to check equality except on Order id
        return (
            (self.order_type == other.order_type)
            and (self.entity_id == other.entity_id)
            and (self.lines == other.lines)
        )


@dataclass
class StockPosition:
    position: int = None
    sku: int = None
    qty: int = None

    def is_like(self, other: Self) -> bool:  # Method to check equality except on id
        return (
            (self.sku == other.sku)
            and (self.qty == other.qty)
        )
    

@dataclass
class StockChange:
    position: int = None
    sku: int = None
    qty: int = None

