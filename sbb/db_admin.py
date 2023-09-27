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

import sqlite3



DB_TABLES = ['purchase_order', 'po_line', 'sale_order', 'so_line', 'product', 'inventory']


class SBB_DBAdmin():

    def __init__(self, db_name):
        self.con = sqlite3.connect(f'data/{db_name}.db')
        self.cur = self.con.cursor()
        
        if not self.is_db_setup():
            self.setup_db()
        
    
    ##############################
    ########## Regular use #######
    ##############################

    def add_PO(self, supplier_id: str) -> int:
        pass

    def add_POlines(self, PO_lines: dict) -> bool:
        pass

    def edit_POlines(self, PO_lines: dict) -> bool:
        pass

    def add_SO(self, customer_id: str) -> int:
        pass

    def add_SOlines(self, SO_lines: dict) -> bool:
        pass

    def edit_SOlines(self, SO_lines: dict) -> bool:
        pass


    ##############################
    ########## Configuration #####
    ##############################

    def add_supplier(self, supplier_name: str) -> int:
        pass

    def add_customer(self, customer_name: str) -> int:
        pass

    def add_sku(self, sku_desc: str) -> int:
        self.cur.execute("""
                         INSERT INTO product (desc)
                         VALUES
                            (?)
                         """,
                         [(sku_desc)])
        self.con.commit()

        return self.cur.lastrowid
        


    ##############################
    ########## Setup #############
    ##############################

    def close_connection(self) -> None:
        self.con.close()

    def is_db_setup(self) -> bool:
        res = self.cur.execute('SELECT name FROM sqlite_master').fetchall()
        list_tables = [item[0] for item in res]
        return all([expected_table in list_tables for expected_table in DB_TABLES])
    
    def setup_db(self) -> None:
        # Purchase orders
        self.cur.execute("""
CREATE TABLE IF NOT EXISTS purchase_order (
                         id INTEGER PRIMARY KEY,
                         supplier_id INTEGER NOT NULL
);
""")
        
        # Purchase order lines
        self.cur.execute("""
CREATE TABLE IF NOT EXISTS po_line (
                         id INTEGER PRIMARY KEY,
                         po_id INTEGER NOT NULL,
                         sku INTEGER NOT NULL,
                         qty_ordered INTEGER NOT NULL,
                         qty_delivered INTEGER NOT NULL
);
""")
        
        # Sale orders
        self.cur.execute("""
CREATE TABLE IF NOT EXISTS sale_order (
                         id INTEGER PRIMARY KEY,
                         customer_id INTEGER NOT NULL
);
""")
        
        # Purchase order lines
        self.cur.execute("""
CREATE TABLE IF NOT EXISTS so_line (
                         id INTEGER PRIMARY KEY,
                         so_id INTEGER NOT NULL,
                         sku INTEGER NOT NULL,
                         qty_ordered INTEGER NOT NULL,
                         qty_delivered INTEGER NOT NULL
);
""")
        
        # Products
        self.cur.execute("""
CREATE TABLE IF NOT EXISTS product (
                         sku INTEGER PRIMARY KEY,
                         desc TEXT NOT NULL
);
""")
        
        # Inventory positions
        self.cur.execute("""
CREATE TABLE IF NOT EXISTS inventory (
                         sku INTEGER PRIMARY KEY,
                         qty INTEGER NOT NULL
);
""")