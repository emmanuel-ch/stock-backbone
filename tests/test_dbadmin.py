""" test_dbadmin.py
Tests SBB_DBAdmin methods.
"""

import pytest
from pathlib import Path

from sbb import db_admin
from sbb.sbb_objects import Order, OrderLine, StockPosition


@pytest.fixture
def dummy_db_file():
    db_name = 'test_db'
    new_db = db_admin.SBB_DBAdmin(db_name)
    db_path = Path('data') / (db_name + '.db')

    yield db_path

    new_db.close_connection()
    db_path.unlink()

@pytest.fixture
def dummy_db():
    new_db = db_admin.SBB_DBAdmin(':memory:')
    yield new_db
    new_db.close_connection()


def test_create_db_and_close_connection(dummy_db_file):
    assert dummy_db_file.is_file()

def test_missing_table(dummy_db):
    dummy_db._cur.execute("DROP TABLE inventory;")
    assert not dummy_db.is_db_setup()


##############################
####### Entities & SKU #######
##############################

def test_add_external_entity(dummy_db):
    # Initial state
    ini_num_entity = dummy_db._cur.execute("SELECT COUNT(*) FROM external_entity;").fetchone()[0]

    # Change
    entity_details = ('entity name', 'type_of_entity')
    dummy_db.add_external_entity(*entity_details)

    # Final state
    new_num_entity = dummy_db._cur.execute("SELECT COUNT(*) FROM external_entity;").fetchone()[0]
    last_entity_created = (
        dummy_db
        ._cur
        .execute("SELECT name, entity_type FROM external_entity ORDER BY id DESC LIMIT 1")
        .fetchone()
    )
        
    assert (new_num_entity == ini_num_entity + 1) and (last_entity_created == entity_details)


def test_is_entity_with_existing_entity(dummy_db):
    entity_details = ('entity name', 'type_of_entity')
    entity_id = dummy_db.add_external_entity(*entity_details)
    assert dummy_db.is_entity(entity_id)

def test_is_entity_with_notexisting_entity(dummy_db):
    entity_details = ('entity name', 'type_of_entity')
    entity_id = dummy_db.add_external_entity(*entity_details)
    assert not dummy_db.is_entity(entity_id + 1)

def test_add_sku(dummy_db):
    ini_num_sku = dummy_db._cur.execute("SELECT COUNT(*) FROM product;").fetchone()[0]
    sku_desc = 'test_sku_name'
    dummy_db.add_sku(sku_desc)
    new_num_sku = dummy_db._cur.execute("SELECT COUNT(*) FROM product;").fetchone()[0]

    last_sku_desc_created = (
        dummy_db
        ._cur
        .execute("SELECT desc FROM product ORDER BY sku DESC LIMIT 1")
        .fetchone()[0]
    )

    assert (new_num_sku == ini_num_sku + 1) and (last_sku_desc_created == sku_desc)

def test_is_sku_with_existing_sku(dummy_db):
    product_desc = 'product desc'
    sku = dummy_db.add_sku(product_desc)
    assert dummy_db.is_sku(sku)

def test_is_sku_with_notexisting_sku(dummy_db):
    product_desc = 'product desc'
    sku = dummy_db.add_sku(product_desc)
    assert not dummy_db.is_sku(sku + 1)


##############################
########### Orders ###########
##############################

def test_add_order(dummy_db):
    # Initial state
    ini_num_entries = dummy_db._cur.execute("SELECT COUNT(*) FROM orders;").fetchone()[0]

    # Change
    order_in = Order(order_type='some_order_type', entity_id=123)
    _ = dummy_db.add_order(order_in)

    # Final state
    new_num_entries = dummy_db._cur.execute("SELECT COUNT(*) FROM orders;").fetchone()[0]
    last_item_created = (
        dummy_db
        ._cur
        .execute("SELECT order_type, entity_id FROM orders ORDER BY id DESC LIMIT 1")
        .fetchone()
    )
    order_out = Order(order_type=last_item_created[0], entity_id=last_item_created[1])
        
    assert (new_num_entries == ini_num_entries + 1) and order_in.is_like(order_out)


def test_add_order_lines(dummy_db):
    # Initial state
    ini_num_entries = dummy_db._cur.execute("SELECT COUNT(*) FROM order_line;").fetchone()[0]

    # Change
    ol_in = [
        OrderLine(order_id=1, position=1, sku=111, qty_ordered=1),
        OrderLine(order_id=1, position=2, sku=222, qty_ordered=4),
        OrderLine(order_id=1, position=3, sku=333, qty_ordered=9)
    ]
    adnl_entries = dummy_db.add_order_lines(ol_in)

    # Final state
    new_num_entries = dummy_db._cur.execute("SELECT COUNT(*) FROM order_line;").fetchone()[0]
    last_items_created = (
        dummy_db
        ._cur
        .execute("SELECT order_id, position, sku, qty_ordered, qty_delivered FROM order_line ORDER BY id DESC LIMIT 3")
        .fetchall()
    )
    ol_out = [
        OrderLine(order_id=ol_fetched[0], position=ol_fetched[1], sku=ol_fetched[2], qty_ordered=ol_fetched[3])
        for ol_fetched in last_items_created[::-1]
    ]

        
    assert (
        (new_num_entries == adnl_entries == ini_num_entries + 3)
        and all([ol.is_like(ol_out[i]) for i, ol in enumerate(ol_in)])
    )


def test_get_order(dummy_db):
    order_in = Order(order_type='some_order_type', entity_id=123)
    order_no = dummy_db.add_order(order_in)

    order_retrieved = dummy_db.get_order(order_no)
    assert order_retrieved == order_in


def test_get_order_lines(dummy_db):
    order_lines = [
        OrderLine(order_id=1, position=1, sku=111, qty_ordered=1),
        OrderLine(order_id=1, position=2, sku=222, qty_ordered=4),
        OrderLine(order_id=1, position=3, sku=333, qty_ordered=9)
    ]
    adnl_entries = dummy_db.add_order_lines(order_lines)

    ol_fetched = dummy_db.get_order_lines(1)
    assert (adnl_entries == 3) and all([ol.is_like(ol_fetched[i]) for i, ol in enumerate(order_lines)])


def test_set_inventory_level(dummy_db):
    # The change
    sku_qty = [[1, 5], [2, 1], [3, 10]]
    num_records = dummy_db.set_inventory_level(sku_qty)

    # Final state
    entries = dummy_db._cur.execute("SELECT position, sku, qty FROM inventory WHERE sku in (1, 2, 3);").fetchall()
    entries = [list(i[1:]) for i in entries]
    
    assert (num_records == 3) and (sku_qty == entries)

def test_update_inventory_level(dummy_db):
    # Setup
    sku_qty = [[1, 5], [2, 1], [3, 10], [4, 20], [100, 1]]
    dummy_db.set_inventory_level(sku_qty)

    # The change
    changes = [[6, 1], [2, 5]]
    dummy_db.update_inventory_level(changes)

    # Final state
    entries = dummy_db._cur.execute("SELECT position, sku, qty FROM inventory WHERE position in (1, 5);").fetchall()
    entries = [[i[-1], i[0]] for i in entries]

    assert changes == entries

def test_get_inventory_level(dummy_db):
    # Setup
    sku_qty = [[1, 5], [2, 1], [3, 10], [4, 20], [100, 1]]
    dummy_db.set_inventory_level(sku_qty)

    inv_position = dummy_db.get_inventory_level([i[0] for i in sku_qty])
    inv_position = [list(i[1:]) for i in inv_position]

    assert sku_qty == inv_position


def test_change_inventory_101(dummy_db):
    # Define ini state
    sku_qty = [[1, 1], [2, 4], [3, 9]]
    dummy_db.set_inventory_level(sku_qty)

    # The change
    data = [[1, 1], [3, 3], [4, 1], [6, 10]]
    dummy_db.change_inventory('101', data)

    # Final state
    expected_inventory = [[1, 2], [2, 4], [3, 12], [4, 1], [6, 10]]
    new_inv = dummy_db.get_inventory_level([1,2,3,4,6])
    new_inv = [list(item[1:]) for item in new_inv]

    assert new_inv == expected_inventory

