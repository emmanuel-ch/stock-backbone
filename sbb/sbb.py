""" sbb.py
Interface to user.

Class StockBackbone - methods:
    make_PO
    receive_PO
    make_SO
    issue_SO

    create_supplier
    create customer
    create_sku
    first_time_setup
"""

import string

from sbb import db_admin
from sbb.exceptions import UserInputInvalid


class StockBackbone():

    def __init__(self, db_name):
        if not validate_text_input(db_name, 'db name'):
            raise UserInputInvalid('Database name', db_name)
        self._db = db_admin.SBB_DBAdmin(db_name)


    ##############################
    ########## Regular use #######
    ##############################

    def make_PO(self, supplier_id: int, PO_lines: dict) -> int:
        pass

    def receive_PO(self, PO_id: int) -> bool:
        pass

    def make_SO(self, customer_id: int, SO_lines: dict) -> int:
        pass

    def issue_SO(self, SO_id: int) -> bool:
        pass


    ##############################
    ########## Configuration #####
    ##############################

    def create_supplier(self, supplier_name: str) -> int:
        if validate_text_input(supplier_name, 'external entity name'):
            return self._db.add_external_entity(supplier_name, 'supplier')
        else:
            raise UserInputInvalid('Supplier name', supplier_name)

    def create_customer(self, customer_name: str) -> int:
        if validate_text_input(customer_name, 'external entity name'):
            return self._db.add_external_entity(customer_name, 'customer')
        else:
            raise UserInputInvalid('Customer name', customer_name)

    def create_sku(self, sku_desc: str) -> int:
        if validate_text_input(sku_desc, 'sku desc'):
            return self._db.add_sku(sku_desc)
        else:
            raise UserInputInvalid('SKU description', sku_desc)


##############################
########## Support ###########
##############################

def validate_text_input(value: str, input_type: str) -> bool:
    match input_type:
        case 'db name':
            valid_chars = '_' + string.ascii_letters + string.digits
            max_length = 30
        case 'sku desc' | 'external entity name':
            valid_chars = ' -_.,()[]' + string.ascii_letters + string.digits
            max_length = 50
        case _:
            return False
    
    acceptable_name = ''.join(char for char in value if char in valid_chars)
    return (value == acceptable_name) and (len(value) > 0) and (len(value) <= max_length)

