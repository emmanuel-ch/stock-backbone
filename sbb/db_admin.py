""" db_admin.py
Administration of database. The methods below receive requests and interact with database.

Class SBB_DBAdmin - methods:
    add_order
    get_order
    add_order_lines
    get_order_lines

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

    def add_order(self, order_type: str, entity_id: str) -> int:
        self._cur.execute("""
                          INSERT INTO orders 
                          (order_type, entity_id)
                          VALUES (?, ?);
                          """,
                          [order_type, entity_id])
        self._con.commit()
        return self._cur.lastrowid
    
    def get_order(self, order_id):
        order = (
            self._cur
            .execute("SELECT order_type, entity_id FROM orders WHERE id = ?", [order_id])
            .fetchone()
        )
        return {'order_type': order[0], 'entity_id': order[1]}


    def add_order_lines(self, order_lines: list) -> int:
        self._cur.executemany("""
                              INSERT INTO order_line 
                              (order_id, position, sku, qty_ordered, qty_delivered)
                              VALUES (?, ?, ?, ?, ?);
                              """,
                              order_lines)
        self._con.commit()
        return self._cur.rowcount
    
    def get_order_lines(self, order_id: int) -> list:
        order_lines = (
            self._cur
            .execute("SELECT id, position, sku, qty_ordered, qty_delivered FROM order_line WHERE order_id = ?", [order_id])
            .fetchall()
        )
        return order_lines
    
    def set_order_lines(self, mode: str, data: list) -> None:
        if mode == 'delivered_qty':
            self._cur.executemany("""
                              UPDATE order_line SET
                                  qty_delivered = ?
                              WHERE id = ?
                              """,
                              data)


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
        # Orders
        self._cur.execute("""
                          CREATE TABLE IF NOT EXISTS orders (
                              id INTEGER PRIMARY KEY,
                              order_type TEXT NOT NULL,
                              entity_id INTEGER NOT NULL
                          );
                          """)
        
        # Order lines
        self._cur.execute("""
                          CREATE TABLE IF NOT EXISTS order_line (
                              id INTEGER PRIMARY KEY,
                              order_id INTEGER NOT NULL,
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
        
