""" test_dbadmin.py
Tests SBB_DBAdmin methods.
"""

import pytest
from pathlib import Path

from sbb import db_admin


@pytest.fixture
def dummy_db():
    db_name = 'test_db'
    new_db = db_admin.SBB_DBAdmin(db_name)
    db_path = Path('data') / (db_name + '.db')

    yield (new_db, db_path)

    new_db.close_connection()
    db_path.unlink()


def test_create_db_and_close_connection2(dummy_db):
    assert dummy_db[1].is_file()

def test_missing_table(dummy_db):
    dummy_db[0]._cur.execute("DROP TABLE inventory;")
    assert not dummy_db[0].is_db_setup()


def test_add_sku(dummy_db):
    ini_num_sku = dummy_db[0]._cur.execute("SELECT COUNT(*) FROM product;").fetchone()[0]
    sku_desc = 'test_sku_name'
    dummy_db[0].add_sku(sku_desc)
    new_num_sku = dummy_db[0]._cur.execute("SELECT COUNT(*) FROM product;").fetchone()[0]

    last_sku_desc_created = (
        dummy_db[0]
        ._cur
        .execute("SELECT desc FROM product ORDER BY sku DESC LIMIT 1")
        .fetchone()[0]
    )

    assert (new_num_sku == ini_num_sku + 1) and (last_sku_desc_created == sku_desc)


def test_add_external_entity(dummy_db):
    # Initial state
    ini_num_entity = dummy_db[0]._cur.execute("SELECT COUNT(*) FROM external_entity;").fetchone()[0]

    # Change
    entity_details = ('entity name', 'type_of_entity')
    dummy_db[0].add_external_entity(*entity_details)

    # Final state
    new_num_entity = dummy_db[0]._cur.execute("SELECT COUNT(*) FROM external_entity;").fetchone()[0]
    last_entity_created = (
        dummy_db[0]
        ._cur
        .execute("SELECT name, entity_type FROM external_entity ORDER BY id DESC LIMIT 1")
        .fetchone()
    )
        
    assert (new_num_entity == ini_num_entity + 1) and (last_entity_created == entity_details)


def test_is_entity_with_existing_entity(dummy_db):
    entity_details = ('entity name', 'type_of_entity')
    entity_id = dummy_db[0].add_external_entity(*entity_details)
    assert dummy_db[0].is_entity(entity_id)

def test_is_entity_with_notexisting_entity(dummy_db):
    entity_details = ('entity name', 'type_of_entity')
    entity_id = dummy_db[0].add_external_entity(*entity_details)
    assert not dummy_db[0].is_entity(entity_id + 1)


def test_is_sku_with_existing_sku(dummy_db):
    product_desc = 'product desc'
    sku = dummy_db[0].add_sku(product_desc)
    assert dummy_db[0].is_sku(sku)

def test_is_sku_with_notexisting_sku(dummy_db):
    product_desc = 'product desc'
    sku = dummy_db[0].add_sku(product_desc)
    assert not dummy_db[0].is_sku(sku + 1)


# def test_add_PO():
#     assert False

# def test_add_POlines():
#     assert False

# def test_edit_POlines():
#     assert False

# def test_add_SO():
#     assert False

# def test_add_SOlines():
#     assert False

# def test_edit_SOlines():
#     assert False

# def test_add_sku():
#     assert False

