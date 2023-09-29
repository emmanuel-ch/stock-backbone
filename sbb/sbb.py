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
from sbb.exceptions import SBB_Exception, UserInputInvalid, EntityDoesntExist, SKUDoesntExist, OrderQtyIncorrect


class StockBackbone():

    def __init__(self, db_name: str) -> None:
        if db_name == ':memory:':
            pass
        elif not validate_text_input(db_name, 'db name'):
            raise UserInputInvalid('Database name', db_name)
        self._db = db_admin.SBB_DBAdmin(db_name)


    ##############################
    ########## Regular use #######
    ##############################

    def make_PO(self, supplier_id: int, PO_lines: list) -> int:
        if not self.is_entity(supplier_id):
            raise EntityDoesntExist('supplier', supplier_id)
        
        lines = []
        for po_line in PO_lines:
            if not self.is_sku(po_line[0]):
                raise SKUDoesntExist(po_line[0])
            
            try:
                qty_ordered = float(po_line[1])
            except ValueError:
                raise OrderQtyIncorrect(*po_line)
            
            lines.append((po_line[0], qty_ordered, 0))
        
        # Input validated
        po_id = self._db.add_PO(supplier_id)
        lines = [(po_id, *line_content) for line_content in lines]
        num_lines_added = self._db.add_POlines(lines)
        if num_lines_added != len(PO_lines):
            raise SBB_Exception(f'Unexpected exception: {num_lines_added} lines created VS. expected {len(PO_lines)}')

        return po_id


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

    def is_entity(self, entity_id: int) -> bool:
        return self._db.is_entity(entity_id)
    
    def is_sku(self, sku: int) -> bool:
        return self._db.is_sku(sku)


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

