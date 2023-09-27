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
    dummy_db[0].con.execute("DROP TABLE inventory;")
    assert dummy_db[0].is_db_setup() is False


def test_add_sku(dummy_db):
    ini_num_sku = dummy_db[0].cur.execute("SELECT COUNT(*) FROM product;").fetchone()[0]
    sku_desc = 'test_sku_name'
    dummy_db[0].add_sku(sku_desc)
    new_num_sku = dummy_db[0].cur.execute("SELECT COUNT(*) FROM product;").fetchone()[0]

    last_sku_desc_created = dummy_db[0].cur.execute("SELECT desc FROM product ORDER BY sku DESC LIMIT 1").fetchone()[0]

    assert (new_num_sku == ini_num_sku + 1) and (last_sku_desc_created == sku_desc) 

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

# def test_add_supplier():
#     assert False

# def test_add_customer():
#     assert False

# def test_add_sku():
#     assert False

