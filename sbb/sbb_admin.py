""" sbb_admin.py
Administration of software. Class to be inherited.

Class StockBackbone_Admin - methods:
    create_supplier
    create customer
    create_sku
    first_time_setup
"""


class StockBackbone_Admin():

    def create_supplier(self, supplier_name: str) -> str:
        pass

    def create_customer(self, customer_name: str) -> str:
        pass

    def create_sku(self, sku_desc: str) -> str:
        pass

    def first_time_setup(self) -> bool:
        pass