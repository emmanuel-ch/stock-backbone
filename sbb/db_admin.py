""" db_admin.py
Administration of database. The methods below receive requests and interact with database.

Class SBB_DBAdmin - methods:
    add_PO
    add_POlines
    edit_POlines
    add_SO
    add_SOlines
    edit_SOlines

    add_external_entity
    add_sku

    is_entity
    is_sku

    close_connection
    is_db_setup
    setup_db
"""

import sqlite3



DB_TABLES = ['purchase_order', 'po_line', 'sale_order', 'so_line', 
             'product', 'inventory', 'external_entity']


class SBB_DBAdmin():

    def __init__(self, db_name: str) -> None:
        if db_name == ':memory:':
            self._con = sqlite3.connect(':memory:')
        else:
            self._con = sqlite3.connect(f'data/{db_name}.db')
        self._cur = self._con.cursor()
        
        if not self.is_db_setup():
            self.setup_db()
        
    
    ##############################
    ########## Regular use #######
    ##############################

    def add_PO(self, supplier_id: str) -> int:
        self._cur.execute("""
                          INSERT INTO purchase_order 
                          (supplier_id)
                          VALUES (?);
                          """,
                          [supplier_id])
        self._con.commit()
        return self._cur.lastrowid
    
    def get_PO(self, po_id):
        po_info = (
            self._cur
            .execute("SELECT supplier_id FROM purchase_order WHERE id = ?", [(po_id)])
            .fetchone()
        )
        return {'supplier_id': po_info[0]}


    def add_POlines(self, PO_lines: list) -> int:
        self._cur.executemany("""
                              INSERT INTO po_line 
                              (po_id, position, sku, qty_ordered, qty_delivered)
                              VALUES (?, ?, ?, ?, ?);
                              """,
                              PO_lines)
        self._con.commit()
        return self._cur.rowcount
    
    def get_POlines(self, po_id):
        po_lines = (
            self._cur
            .execute("SELECT position, sku, qty_ordered, qty_delivered FROM po_line WHERE po_id = ?", [(po_id)])
            .fetchall()
        )
        return po_lines

    def edit_POlines(self, PO_lines: dict) -> bool:
        pass

    def add_SO(self, customer_id: str) -> int:
        self._cur.execute("""
                          INSERT INTO sale_order 
                          (customer_id)
                          VALUES (?);
                          """,
                          [customer_id])
        self._con.commit()
        return self._cur.lastrowid

    def add_SOlines(self, SO_lines: list) -> int:
        self._cur.executemany("""
                              INSERT INTO so_line 
                              (so_id, position, sku, qty_ordered, qty_delivered)
                              VALUES (?, ?, ?, ?, ?);
                              """,
                              SO_lines)
        self._con.commit()
        return self._cur.rowcount

    def edit_SOlines(self, SO_lines: dict) -> bool:
        pass


    ##############################
    ########## Configuration #####
    ##############################

    def add_external_entity(self, supplier_name: str, entity_type: str) -> int:
        self._cur.execute("""
                          INSERT INTO external_entity 
                          (name, entity_type)
                          VALUES (?, ?);
                          """,
                          [supplier_name, entity_type])
        self._con.commit()
        return self._cur.lastrowid

    def add_sku(self, sku_desc: str) -> int:
        self._cur.execute("""
                          INSERT INTO product (desc)
                          VALUES (?);
                          """,
                          [(sku_desc)])
        self._con.commit()
        return self._cur.lastrowid
        

    ##############################
    ########## Support ###########
    ##############################

    def is_entity(self, entity_id: int) -> bool:
        checker = (
            self
            ._cur
            .execute("SELECT name FROM external_entity WHERE id=?", [(entity_id)])
            .fetchone()
        )
        if checker is None:
            return False
        elif len(checker) == 1:
            return True
        raise Exception(f'Unexpected exception: More than 1 external entity found for id: {entity_id}')
    
    def is_sku(self, sku: int) -> bool:
        checker = (
            self
            ._cur
            .execute("SELECT desc FROM product WHERE sku=?", [sku])
            .fetchone()
        )
        if checker is None:
            return False
        elif len(checker) == 1:
            return True
        raise Exception(f'Unexpected exception: More than 1 sku for: {sku}')

    ##############################
    ########## Setup #############
    ##############################

    def close_connection(self) -> None:
        self._con.close()

    def is_db_setup(self) -> bool:
        res = self._cur.execute("SELECT name FROM sqlite_master").fetchall()
        list_tables = [item[0] for item in res]
        return all([expected_table in list_tables for expected_table in DB_TABLES])
    
    def setup_db(self) -> None:
        # Purchase orders
        self._cur.execute("""
                          CREATE TABLE IF NOT EXISTS purchase_order (
                              id INTEGER PRIMARY KEY,
                              supplier_id INTEGER NOT NULL
                          );
                          """)
        
        # Purchase order lines
        self._cur.execute("""
                          CREATE TABLE IF NOT EXISTS po_line (
                              id INTEGER PRIMARY KEY,
                              po_id INTEGER NOT NULL,
                              position INTEGER NOT NULL,
                              sku INTEGER NOT NULL,
                              qty_ordered INTEGER NOT NULL,
                              qty_delivered INTEGER NOT NULL
                          );
                          """)
        
        # Sale orders
        self._cur.execute("""
                          CREATE TABLE IF NOT EXISTS sale_order (
                              id INTEGER PRIMARY KEY,
                              customer_id INTEGER NOT NULL
                          );
                          """)
        
        # Sale order lines
        self._cur.execute("""
                          CREATE TABLE IF NOT EXISTS so_line (
                              id INTEGER PRIMARY KEY,
                              so_id INTEGER NOT NULL,
                              position INTEGER NOT NULL,
                              sku INTEGER NOT NULL,
                              qty_ordered INTEGER NOT NULL,
                              qty_delivered INTEGER NOT NULL
                          );
                          """)
        
        # Products
        self._cur.execute("""
                          CREATE TABLE IF NOT EXISTS product (
                              sku INTEGER PRIMARY KEY,
                              desc TEXT NOT NULL
                          );
                          """)
        
        # Inventory positions
        self._cur.execute("""
                          CREATE TABLE IF NOT EXISTS inventory (
                              sku INTEGER PRIMARY KEY,
                              qty INTEGER NOT NULL
                          );
                          """)
        
        # Suppliers + Customers
        self._cur.execute("""
                          CREATE TABLE IF NOT EXISTS external_entity (
                              id INTEGER PRIMARY KEY,
                              name TEXT NOT NULL,
                              entity_type TEXT NOT NULL
                          );
                          """)
        
