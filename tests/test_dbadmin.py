""" test_dbadmin.py
Tests SBB_DBAdmin methods.
"""

import pytest
from pathlib import Path
from sbb import db_admin


@pytest.fixture
def create_dummy_db():
    db_name = 'test_db'
    new_db = db_admin.SBB_DBAdmin(db_name)
    db_path = Path('data') / (db_name + '.db')

    yield (new_db, db_path)

    new_db.close_connection()
    db_path.unlink()


def test_create_db_and_close_connection2(create_dummy_db):
    assert create_dummy_db[1].is_file()


def test_missing_table(create_dummy_db):
    create_dummy_db[0].con.execute("DROP TABLE inventory;")
    assert create_dummy_db[0].is_db_setup() is False


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

