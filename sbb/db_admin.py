""" db_admin.py
Administration of database. The methods below receive requests and interact with database.

Class SBB_DBAdmin - methods:
    add_PO
    add_POlines
    edit_POlines
    add_SO
    add_SOlines
    edit_SOlines

    add_supplier
    add_customer
    add_sku
    first_time_setup
"""


class SBB_DBAdmin():

    def __init__(self):
        pass
    
    ##############################
    ########## Regular use #######
    ##############################

    def add_PO(self, supplier_id: str) -> str:
        pass

    def add_POlines(self, PO_lines: dict) -> bool:
        pass

    def edit_POlines(self, PO_lines: dict) -> bool:
        pass

    def add_SO(self, customer_id: str) -> str:
        pass

    def add_SOlines(self, SO_lines: dict) -> bool:
        pass

    def edit_SOlines(self, SO_lines: dict) -> bool:
        pass


    ##############################
    ########## Setup use #########
    ##############################

    def add_supplier(self, supplier_name: str) -> str:
        pass

    def add_customer(self, customer_name: str) -> str:
        pass

    def add_sku(self, sku_desc: str) -> str:
        pass
    
    def first_time_setup(self) -> bool:
        pass

