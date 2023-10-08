""" exceptions.py
Defines exceptions to be used by software.
"""

from typing import Any


class SBB_Exception(Exception):
    """Base class for SBB exceptions."""
    pass

class UserInputInvalid(SBB_Exception):
    """User text input invalid."""
    def __init__(self, which_input: str, value_entered: Any, *args, **kwargs):
        msg = f'User text input invalid for field [{which_input}]: {value_entered}'
        super().__init__(msg, *args, **kwargs)

class EntityDoesntExist(SBB_Exception):
    """Requested entity doesn't exist."""
    def __init__(self, entity_id: int, *args, **kwargs):
        msg = f'Requested entity doesn\'t exist: {entity_id}'
        super().__init__(msg, *args, **kwargs)

class SKUDoesntExist(SBB_Exception):
    """Requested SKU doesn't exist."""
    def __init__(self, sku: int, *args, **kwargs):
        msg = f'Requested SKU doesn\'t exist: {sku}'
        super().__init__(msg, *args, **kwargs)

class OrderQtyIncorrect(SBB_Exception):
    """Order lines incorrect."""
    def __init__(self, order_type: str, order_lines: int, *args, **kwargs):
        msg = f'Impossible to make {order_type} because of invalid order lines: {order_lines}'
        super().__init__(msg, *args, **kwargs)

class WrongOrderType(SBB_Exception):
    """Order lines incorrect."""
    def __init__(self, expected_order_type: str, actual_order_type: str, *args, **kwargs):
        msg = f'Expected order type {expected_order_type} but received order type {actual_order_type}'
        super().__init__(msg, *args, **kwargs)

