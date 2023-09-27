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

        