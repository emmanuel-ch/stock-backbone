""" test_sbb.py
Tests StockBackbone and StockBackbone_Admin methods
"""

import pytest
from pathlib import Path

from sbb.sbb import StockBackbone, validate_text_input


# @pytest.fixture
# def dummy_sbb():
#     db_name = 'test_db'
#     sbb_object = StockBackbone(db_name)
#     db_path = Path('data') / (db_name + '.db')

#     yield (sbb_object, db_path)

#     sbb_object.db.close_connection()
#     db_path.unlink()


@pytest.mark.parametrize("field_type,test_input,expected_outcome", [
    ('db name', 'a_good_name', True),
    ('db name', 'not / acceptable', False) ,
    ('sku desc', 'acceptable 1 (2)_3 -_.,()[]', True),
    ('sku desc', 'not["acc]/ept@ble{*!?&#\+=}', False),
    ('external entity name', 'acceptable 1 (2)_3 -_.,()[]', True),
    ('external entity name', 'not["acc]/ept@ble{*!?&#\+=}', False)
    ])
def test_validate_text_input(field_type, test_input, expected_outcome):
    assert validate_text_input(test_input, field_type) == expected_outcome
    

# def test_create_sku(dummy_sbb):
#     assert False

# def test_make_PO():
#     assert False

# def test_receive_PO():
#     assert False

# def test_make_SO():
#     assert False

# def test_issue_SO():
#     assert False

# def test_create_supplier():
#     assert False

# def test_create_customer():
#     assert False
    
