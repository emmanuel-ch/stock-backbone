""" sbb.py
Interface to user.

Class StockBackbone - methods:
    make_PO
    make_SO
    _make_order
    get_order
    receive_PO

    create_supplier
    create customer
    create_sku

    is_entity
    is_sku
    validate_text_input
"""

import string

from sbb import db_admin
from sbb.exceptions import (
    SBB_Exception, UserInputInvalid,
    EntityDoesntExist, SKUDoesntExist,
    OrderQtyIncorrect, WrongOrderType,
    NotEnoughStockToFullfillOrder
)
from sbb.sbb_objects import Order, OrderLine, StockPosition, StockChange


class StockBackbone():

    def __init__(self, db_name: str) -> None:
        if db_name == ':memory:':
            pass
        elif not StockBackbone.validate_text_input(db_name, 'db name'):
            raise UserInputInvalid('Database name', db_name)
        self._db = db_admin.SBB_DBAdmin(db_name)


    ##############################
    ########## Regular use #######
    ##############################

    def make_PO(self, supplier_id: int, PO_lines: list[OrderLine]) -> int:
        return self._make_order(Order(
            order_type='purchase',
            entity_id=supplier_id,
            lines=[
                OrderLine(sku=item[0], qty_ordered=item[1], qty_delivered=0)
                for item in PO_lines
            ]
        ))

    def make_SO(self, customer_id: int, SO_lines: list[OrderLine]) -> int:
        return self._make_order(Order(
            order_type='sale',
            entity_id=customer_id,
            lines=[
                OrderLine(sku=item[0], qty_ordered=item[1], qty_delivered=0)
                for item in SO_lines
            ]
        ))

    def _make_order(self, the_order: Order) -> int:
        # FIXME: Prevent having 2 lines with same SKU
        if not self.is_entity(the_order.entity_id):
            raise EntityDoesntExist(the_order.entity_id)
        
        position = 1
        for order_line in the_order.lines:
            if not self.is_sku(order_line.sku):
                raise SKUDoesntExist(order_line.sku)
            
            try:
                order_line.qty_ordered = float(order_line.qty_ordered)
            except ValueError:
                raise OrderQtyIncorrect(the_order.order_type, order_line)
            
            order_line.position = position
            position += 1
        
        # Input validated
        order_id = self._db.add_order(the_order)
        for ol in the_order.lines:
            ol.order_id = order_id
        num_lines_added = self._db.add_order_lines(the_order.lines)
        if num_lines_added != len(the_order.lines):
            raise SBB_Exception(
                f'Unexpected exception: {num_lines_added} lines created ',
                f'VS. expected {len(the_order.lines)}'
                )

        return order_id

    def get_order(self, order_id: int) -> Order:
        the_order = self._db.get_order(order_id)
        return the_order
    
    def receive_PO(self, mode: str, order_id: int) -> bool:
        if mode == 'full-delivery':
            the_order = self.get_order(order_id)
            if the_order.order_type != 'purchase':
                raise WrongOrderType('purchase', the_order.order_type)
            
            # Add inventory to stock
            add_inv = self._db.change_inventory('101', [
                StockChange(sku=ol.sku, qty=ol.qty_ordered)
                for ol in the_order.lines
                ])

            if add_inv:
                # Update PO
                for ol in the_order.lines:
                    ol.qty_delivered = ol.qty_ordered
                self._db.set_order_lines('delivered_qty', the_order.lines)
            else:
                raise SBB_Exception('Unable to increase inventory')
        else:
            raise SBB_Exception(
                'Unexpected exception: order-setting order not expected'
                )
    
    def issue_SO(self, mode: str, order_id: int) -> bool:
        if mode == 'ship-full':
            the_order = self.get_order(order_id)
            if the_order.order_type != 'sale':
                raise WrongOrderType('sale', the_order.order_type)
            
            # Check if order is fulfillable
            inv_levels = self._db.get_inventory_level([
                item.sku for item in the_order.lines
            ])
            inv_changes = []
            for ol in the_order.lines:
                qty_change = ol.qty_ordered - ol.qty_delivered
                stock_position = [
                    stk for stk in inv_levels
                    if stk.sku == ol.sku
                    ]
                if not stock_position:
                    raise NotEnoughStockToFullfillOrder(
                        order_id, ol.sku, qty_change, 0
                    )
                stock_position = stock_position[0]
                qty_after = stock_position.qty - qty_change
                if qty_after < 0:
                    raise NotEnoughStockToFullfillOrder(
                        order_id, ol.sku, qty_change, stock_position.qty
                    )
                inv_changes.append(StockPosition(
                    position=stock_position.position,
                    qty=qty_after
                ))

            # We have enough stock. Proceed
            rem_inv = self._db.change_inventory('201', inv_changes)

            if rem_inv:  # All lines on SO have been fulfilled
                for ol in the_order.lines:
                    ol.qty_delivered = ol.qty_ordered
                self._db.set_order_lines('delivered_qty', the_order.lines)
        else:
            raise SBB_Exception(
                'Unexpected exception: order-setting order not expected'
                )


    ##############################
    ########## Configuration #####
    ##############################

    def create_supplier(self, supplier_name: str) -> int:
        if StockBackbone.validate_text_input(supplier_name, 
                                             'external entity name'):
            return self._db.add_external_entity(supplier_name, 'supplier')
        else:
            raise UserInputInvalid('Supplier name', supplier_name)

    def create_customer(self, customer_name: str) -> int:
        if StockBackbone.validate_text_input(customer_name, 
                                             'external entity name'):
            return self._db.add_external_entity(customer_name, 'customer')
        else:
            raise UserInputInvalid('Customer name', customer_name)

    def create_sku(self, sku_desc: str) -> int:
        if StockBackbone.validate_text_input(sku_desc, 'sku desc'):
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

    @staticmethod
    def validate_text_input(value: str, input_type: str) -> bool:
        match input_type:
            case 'db name':
                valid_chrs = '_' + string.ascii_letters + string.digits
                max_length = 30
            case 'sku desc' | 'external entity name':
                valid_chrs = ' -_.,()[]' + string.ascii_letters + string.digits
                max_length = 50
            case _:
                return False
        
        acceptable_name = ''.join(char for char in value if char in valid_chrs)
        return (
            (value == acceptable_name)
            and (len(value) > 0)
            and (len(value) <= max_length)
        )

