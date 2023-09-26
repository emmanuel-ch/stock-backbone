""" test_dbadmin.py
Tests SBB_DBAdmin methods.
"""

import pytest
from pathlib import Path
from sbb import db_admin


def test_create_db_and_close_connection():
    db_name = 'test_db'
    new_db = db_admin.SBB_DBAdmin(db_name)
    db_path = Path('data') / (db_name + '.db')

    test_db_exists = db_path.is_file()

    new_db.close_connection()
    db_path.unlink()

    assert test_db_exists


def test_missing_table():
    db_name = 'test_db'
    new_db = db_admin.SBB_DBAdmin(db_name)
    db_path = Path('data') / (db_name + '.db')

    new_db.con.execute("DROP TABLE inventory;")

    test_not_detect_missing_table = new_db.is_db_setup()

    new_db.close_connection()
    db_path.unlink()

    assert test_not_detect_missing_table is False


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

