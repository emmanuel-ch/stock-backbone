""" test_sbb.py
Tests StockBackbone and StockBackbone_Admin methods
"""

import pytest

from sbb.sbb import StockBackbone
from sbb.exceptions import (
    EntityDoesntExist, SKUDoesntExist, OrderQtyIncorrect,
    NotEnoughStockToFullfillOrder
)
from sbb.sbb_objects import StockPosition


@pytest.fixture
def dummy_sbb():
    sbb_object = StockBackbone(':memory:')
    yield sbb_object
    sbb_object._db.close_connection()


@pytest.mark.parametrize("field_type,test_input,expected_outcome", [
    ('db name', 'a_good_name', True),
    ('db name', 'not / acceptable', False) ,
    ('sku desc', 'acceptable 1 (2)_3 -_.,()[]', True),
    ('sku desc', 'not["acc]/ept@ble{*!?&#\+=}', False),
    ('external entity name', 'acceptable 1 (2)_3 -_.,()[]', True),
    ('external entity name', 'not["acc]/ept@ble{*!?&#\+=}', False)
    ])
def test_validate_text_input(field_type, test_input, expected_outcome):
    assert (
        StockBackbone.validate_text_input(test_input, field_type)
        == expected_outcome
    )


##############################
######## Purch. orders #######
##############################

def test_make_PO_invalid_supplier_id(dummy_sbb):
    sku = dummy_sbb.create_sku('A product')
    with pytest.raises(EntityDoesntExist):
        dummy_sbb.make_PO(666, [(sku + 1, 5)])

def test_make_PO_invalid_sku(dummy_sbb):
    supplier_id = dummy_sbb.create_supplier('A supplier')
    sku = dummy_sbb.create_sku('A product')
    with pytest.raises(SKUDoesntExist):
        dummy_sbb.make_PO(supplier_id, [(sku + 1, 1)])

def test_make_PO_invalid_qty_ordered(dummy_sbb):
    supplier_id = dummy_sbb.create_supplier('A supplier')
    sku = dummy_sbb.create_sku('A product')
    with pytest.raises(OrderQtyIncorrect):
        dummy_sbb.make_PO(supplier_id, [(sku, '1.b')])

def test_make_PO_valid(dummy_sbb):
    supplier_id = dummy_sbb.create_supplier('A supplier')
    sku = [dummy_sbb.create_sku(f'Product {chr(65+i)}') for i in range(3)]
    po_id = dummy_sbb.make_PO(supplier_id, [
        (sku[0], 5),
        (sku[1], 1),
        (sku[2], 100)
        ])
    assert isinstance(po_id, int)

def test_receive_PO(dummy_sbb):
    supplier_id = dummy_sbb.create_supplier('A supplier')
    sku = [dummy_sbb.create_sku(f'Product {chr(65+i)}') for i in range(3)]
    po_id = dummy_sbb.make_PO(supplier_id, [
        (sku[0], 5),
        (sku[1], 1),
        (sku[2], 100)
        ])
    
    lines_before = dummy_sbb.get_order(po_id).lines
    dummy_sbb.receive_PO('full-delivery', po_id)
    lines_after = dummy_sbb.get_order(po_id).lines

    assert all([
        (lines_before[i].position == lines_after[i].position)
        and (lines_before[i].qty_ordered == lines_after[i].qty_delivered)
        for i in range(len(lines_before))
        ])


##############################
########## Sale orders #######
##############################

def test_make_SO_invalid_customer_id(dummy_sbb):
    sku = dummy_sbb.create_sku('A product')
    with pytest.raises(EntityDoesntExist):
        dummy_sbb.make_SO(666, [(sku + 1, 5)])

def test_make_SO_invalid_sku(dummy_sbb):
    customer_id = dummy_sbb.create_customer('A customer')
    sku = dummy_sbb.create_sku('A product')
    with pytest.raises(SKUDoesntExist):
        dummy_sbb.make_SO(customer_id, [(sku + 1, 1)])

def test_make_SO_invalid_qty_ordered(dummy_sbb):
    customer_id = dummy_sbb.create_customer('A customer')
    sku = dummy_sbb.create_sku('A product')
    with pytest.raises(OrderQtyIncorrect):
        dummy_sbb.make_SO(customer_id, [(sku, '1.b')])

def test_make_SO_valid(dummy_sbb):
    customer_id = dummy_sbb.create_customer('A customer')
    sku = [dummy_sbb.create_sku(f'Product {chr(65+i)}') for i in range(3)]
    so_id = dummy_sbb.make_SO(customer_id, [
        (sku[0], 5),
        (sku[1], 1),
        (sku[2], 100)
        ])
    assert isinstance(so_id, int)


def test_issue_SO_stock_unavailable(dummy_sbb):
    customer_id = dummy_sbb.create_customer('A customer')
    sku = [dummy_sbb.create_sku(f'Product {chr(65+i)}') for i in range(3)]
    so_id = dummy_sbb.make_SO(customer_id, [
        (sku[0], 5),
        (sku[1], 1),
        (sku[2], 100)
        ])
    dummy_sbb._db.set_inventory_level([
        StockPosition(sku=sku[0], qty=10)
    ])

    with pytest.raises(NotEnoughStockToFullfillOrder):
        _ = dummy_sbb.issue_SO('ship-full', so_id)


def test_issue_SO_stock_available(dummy_sbb):
    customer_id = dummy_sbb.create_customer('A customer')
    sku = [dummy_sbb.create_sku(f'Product {chr(65+i)}') for i in range(3)]
    so_id = dummy_sbb.make_SO(customer_id, [
        (sku[0], 5),
        (sku[1], 1),
        (sku[2], 100)
        ])
    dummy_sbb._db.set_inventory_level([
        StockPosition(sku=sku[0], qty=10),
        StockPosition(sku=sku[1], qty=1),
        StockPosition(sku=sku[2], qty=100),
    ])

    _ = dummy_sbb.issue_SO('ship-full', so_id)
    expected_inventory = [
        StockPosition(sku=sku[0], qty=5),
        StockPosition(sku=sku[1], qty=0),
        StockPosition(sku=sku[2], qty=0),
    ]

    inv_level_after = dummy_sbb._db.get_inventory_level(sku[:])

    assert all([
        exp.is_like(inv_level_after[i])
        for i, exp in enumerate(expected_inventory)
    ])