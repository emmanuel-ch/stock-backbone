""" sbb.py
Interface to user.

Class StockBackbone - methods:
    make_PO
    receive_PO
    make_SO
    issue_SO

    create_supplier
    create customer
    create_sku
    first_time_setup
"""

from sbb import db_admin


class StockBackbone():

    def __init__(self, db_name):
        self.db = db_admin.SBB_DBAdmin(db_name)


    ##############################
    ########## Regular use #######
    ##############################

    def make_PO(self, supplier_id: str, PO_lines: dict) -> str:
        pass

    def receive_PO(self, PO_id: str) -> bool:
        pass

    def make_SO(self, customer_id: str, SO_lines: dict) -> str:
        pass

    def issue_SO(self, SO_id: str) -> bool:
        pass


    ##############################
    ########## Configuration #####
    ##############################

    def create_supplier(self, supplier_name: str) -> str:
        pass

    def create_customer(self, customer_name: str) -> str:
        pass

    def create_sku(self, sku_desc: str) -> str:
        pass

