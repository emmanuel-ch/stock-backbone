""" db_admin.py
Administration of database. The methods below receive requests and interact with database.

Class SBB_DBAdmin - methods:
    add_order
    get_order
    add_order_lines
    get_order_lines
    set_order_lines

    change_inventory
    set_inventory_level
    update_inventory_level
    get_inventory_level

    add_external_entity
    add_sku

    is_entity
    is_sku

    close_connection
    is_db_setup
    setup_db
"""

import sqlite3

from sbb.sbb_objects import Order, OrderLine, StockPosition



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

    def add_order(self, the_order: Order) -> int:
        self._cur.execute("""
                          INSERT INTO orders 
                          (order_type, entity_id)
                          VALUES (?, ?);
                          """,
                          [the_order.order_type, the_order.entity_id])
        self._con.commit()
        return self._cur.lastrowid
    
    def get_order(self, order_id):
        order = (
            self._cur
            .execute("SELECT order_type, entity_id FROM orders WHERE id = ?", [order_id])
            .fetchone()
        )
        return Order(order_type=order[0], entity_id=order[1])


    def add_order_lines(self, order_lines: list) -> int:
        self._cur.executemany("""
                              INSERT INTO order_line 
                              (order_id, position, sku, qty_ordered, qty_delivered)
                              VALUES (?, ?, ?, ?, ?);
                              """,
                              [
                                  [ol.order_id, ol.position, ol.sku, ol.qty_ordered, ol.qty_delivered]
                                  for ol in order_lines
                              ])
        self._con.commit()
        return self._cur.rowcount
    
    def get_order_lines(self, order_id: int) -> list:
        order_lines = (
            self._cur
            .execute("SELECT id, order_id, position, sku, qty_ordered, qty_delivered FROM order_line WHERE order_id = ?", [order_id])
            .fetchall()
        )
        return [OrderLine(*line) for line in order_lines]
    
    def set_order_lines(self, mode: str, data: list) -> None:
        if mode == 'delivered_qty':
            self._cur.executemany("""
                              UPDATE order_line SET
                                  qty_delivered = ?
                              WHERE id = ?
                              """,
                              data)

    def change_inventory(self, change_code, data):
        match change_code:
            case '101':  # Increase inventory because of PO-receipt - data contains List[List[sku, qty], ...]
                inventory_lvl = self.get_inventory_level([i[0] for i in data])  # List[Tuple(position, sku, qty), ...]

                inv_position_to_create = list()
                inv_position_to_update = list()
                for item in data:
                    search_existing_inv = [inv for inv in inventory_lvl if inv[1] == item[0]]
                    if len(search_existing_inv) == 1:
                        inv = search_existing_inv[0]
                        inv_position_to_update.append([inv[2] + item[1], inv[0]])
                    elif len(search_existing_inv) == 1:
                        raise Exception(f'Unexpected number of inventory positions')
                    else:
                        inv_position_to_create.append(item)
                
                success = True
                if len(inv_position_to_create) > 0:
                    new_lines = self.set_inventory_level(inv_position_to_create)
                    success = new_lines == len(inv_position_to_create)
                
                if len(inv_position_to_update) > 0:
                    self.update_inventory_level(inv_position_to_update)

                return success

    
    def set_inventory_level(self, sku_qty: list) -> int:
        self._cur.executemany("""
                              INSERT INTO inventory 
                              (sku, qty)
                              VALUES (?, ?);
                              """,
                              sku_qty)
        self._con.commit()
        return self._cur.rowcount

    def update_inventory_level(self, pos_qty: dict) -> int:
        self._cur.executemany("""
                              UPDATE inventory SET
                                  qty = ?
                              WHERE position = ?
                              """,
                              pos_qty)

    def get_inventory_level(self, skus: list) -> list:
        return (
            self._cur
            .execute(f"SELECT position, sku, qty FROM inventory WHERE sku in ({','.join(len(skus)*['?'])})", skus)
            .fetchall()
        )

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
                              position INTEGER PRIMARY KEY,
                              sku INTEGER NOT NULL,
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
        
