""" test_dbadmin.py
Tests SBB_DBAdmin methods.
"""

from typing import Callable
import pytest
from pathlib import Path

from sbb import db_admin


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


def test_is_sku_with_existing_sku(dummy_db):
    product_desc = 'product desc'
    sku = dummy_db.add_sku(product_desc)
    assert dummy_db.is_sku(sku)

def test_is_sku_with_notexisting_sku(dummy_db):
    product_desc = 'product desc'
    sku = dummy_db.add_sku(product_desc)
    assert not dummy_db.is_sku(sku + 1)


def test_add_PO(dummy_db):
    # Initial state
    ini_num_entries = dummy_db._cur.execute("SELECT COUNT(*) FROM purchase_order;").fetchone()[0]

    # Change
    details = (123,)
    dummy_db.add_PO(*details)

    # Final state
    new_num_entries = dummy_db._cur.execute("SELECT COUNT(*) FROM purchase_order;").fetchone()[0]
    last_item_created = (
        dummy_db
        ._cur
        .execute("SELECT supplier_id FROM purchase_order ORDER BY id DESC LIMIT 1")
        .fetchone()
    )
        
    assert (new_num_entries == ini_num_entries + 1) and (last_item_created == details)


def test_add_PO_lines(dummy_db):
    # Initial state
    ini_num_entries = dummy_db._cur.execute("SELECT COUNT(*) FROM po_line;").fetchone()[0]

    # Change
    details = [(1, 111, 1, 0), (5, 222, 2, 0), (5, 333, 3, 0)]
    adnl_entries = dummy_db.add_POlines([*details])

    # Final state
    new_num_entries = dummy_db._cur.execute("SELECT COUNT(*) FROM po_line;").fetchone()[0]
    last_items_created = (
        dummy_db
        ._cur
        .execute("SELECT po_id, sku, qty_ordered, qty_delivered FROM po_line ORDER BY id DESC LIMIT 3")
        .fetchall()
    )
        
    assert (new_num_entries == adnl_entries == ini_num_entries + 3) and (last_items_created[::-1] == details)


def test_add_SO(dummy_db):
    # Initial state
    ini_num_entries = dummy_db._cur.execute("SELECT COUNT(*) FROM sale_order;").fetchone()[0]

    # Change
    details = (123,)
    dummy_db.add_SO(*details)

    # Final state
    new_num_entries = dummy_db._cur.execute("SELECT COUNT(*) FROM sale_order;").fetchone()[0]
    last_item_created = (
        dummy_db
        ._cur
        .execute("SELECT customer_id FROM sale_order ORDER BY id DESC LIMIT 1")
        .fetchone()
    )
        
    assert (new_num_entries == ini_num_entries + 1) and (last_item_created == details)


def test_add_SO_lines(dummy_db):
    # Initial state
    ini_num_entries = dummy_db._cur.execute("SELECT COUNT(*) FROM so_line;").fetchone()[0]

    # Change
    details = [(1, 111, 1, 0), (5, 222, 2, 0), (5, 333, 3, 0)]
    adnl_entries = dummy_db.add_SOlines([*details])

    # Final state
    new_num_entries = dummy_db._cur.execute("SELECT COUNT(*) FROM so_line;").fetchone()[0]
    last_items_created = (
        dummy_db
        ._cur
        .execute("SELECT so_id, sku, qty_ordered, qty_delivered FROM so_line ORDER BY id DESC LIMIT 3")
        .fetchall()
    )
        
    assert (new_num_entries == adnl_entries == ini_num_entries + 3) and (last_items_created[::-1] == details)


# def test_edit_POlines():
#     assert False

# def test_edit_SOlines():
#     assert False

