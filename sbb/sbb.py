""" sbb.py
Interface to user.

Class StockBackbone - methods:
    make_PO
    make_SO
    _make_order
    get_order

    create_supplier
    create customer
    create_sku

    is_entity
    is_sku

validate_text_input
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
        return self._make_order('purchase', 'supplier', supplier_id, PO_lines)

    def make_SO(self, customerer_id: int, SO_lines: list) -> int:
        return self._make_order('sale', 'customer', customerer_id, SO_lines)

    def _make_order(self, order_type: str, entity_type: str, entity_id: int, order_lines: list) -> int:
        if not self.is_entity(entity_id):
            raise EntityDoesntExist(entity_type, entity_id)
        
        lines = []
        position = 1
        for order_line in order_lines:
            if not self.is_sku(order_line[0]):
                raise SKUDoesntExist(order_line[0])
            
            try:
                qty_ordered = float(order_line[1])
            except ValueError:
                raise OrderQtyIncorrect(*order_line)
            
            lines.append((position, order_line[0], qty_ordered, 0))
            position += 1
        
        # Input validated
        order_id = self._db.add_order(order_type, entity_id)
        lines = [(order_id, *line_content) for line_content in lines]
        num_lines_added = self._db.add_order_lines(lines)
        if num_lines_added != len(order_lines):
            raise SBB_Exception(f'Unexpected exception: {num_lines_added} lines created VS. expected {len(order_lines)}')

        return order_id

    def get_order(self, order_id):
        order_info = self._db.get_order(order_id)
        order_info['lines'] = self._db.get_order_lines(order_id)
        return order_info
    
    def set_order(self, mode: str, order_id: int) -> bool:
        if mode == 'full-delivery':
            order_lines = self.get_order(order_id)['lines']
            data = [[i[3], i[0]] for i in order_lines]
            self._db.set_order_lines('delivered_qty', data)
        else:
            SBB_Exception('Unexpected exception: order-setting order not expected')


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

