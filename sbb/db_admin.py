""" db_admin.py
Administration of database.
The methods below receive requests and interact with database.

Class SBB_DBAdmin - methods:
    add_order
    get_order
    add_order_lines
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

from sbb.sbb_objects import Order, OrderLine, StockPosition, StockChange


class SBB_DBAdmin():
    DB_TABLES = [
        'purchase_order', 'po_line', 'sale_order', 'so_line', 
        'product', 'inventory', 'external_entity'
    ]

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
    
    def get_order(self, order_id: int) -> Order:
        order = (
            self._cur
            .execute("""
                     SELECT
                        orders.id, orders.order_type, orders.entity_id,
                        ol.position, ol.sku, ol.qty_ordered, ol.qty_delivered
                     FROM orders
                     LEFT JOIN order_line AS ol
                     WHERE orders.id = ?
                     """, [order_id])
            .fetchall()
        )
        return Order(
            id=order[0][0],
            order_type=order[0][1],
            entity_id=order[0][2],
            lines=[
                OrderLine(position=ol[3], sku=ol[4], 
                          qty_ordered=ol[5], qty_delivered=ol[6])
                for ol in order
            ]
        )

    def add_order_lines(self, order_lines: list[OrderLine]) -> int:
        self._cur.executemany("""
            INSERT INTO order_line 
            (order_id, position, sku, qty_ordered, qty_delivered)
            VALUES (?, ?, ?, ?, ?);
                              """,
                              [
                                  [ol.order_id, ol.position, ol.sku,
                                   ol.qty_ordered, ol.qty_delivered]
                                  for ol in order_lines
                              ])
        self._con.commit()
        return self._cur.rowcount
    
    def set_order_lines(self, mode: str, data: list) -> None:
        if mode == 'delivered_qty':
            self._cur.executemany("""
                              UPDATE order_line SET
                                  qty_delivered = ?
                              WHERE id = ?
                              """,
                              [
                                  [ol.qty_delivered, ol.position]
                                  for ol in data
                              ])


    def change_inventory(self, change_code: str,
                         data: list[StockChange | StockPosition]) -> bool:
        match change_code:
            case '101':  # Increase inventory because of PO-receipt
                inventory_levels = self.get_inventory_level(
                    [item.sku for item in data]
                )  # List[StockPosition, ...]
                inv_pos_to_create = list()
                inv_position_to_update = list()
                for item in data:
                    search_existing_inv = [
                        inv for inv in inventory_levels
                        if inv.sku == item.sku
                    ]
                    if len(search_existing_inv) == 1:
                        inv = search_existing_inv[0]
                        inv_position_to_update.append(StockChange(
                            position=inv.position, qty=inv.qty + item.qty
                        ))
                    elif len(search_existing_inv) == 1:
                        raise Exception(f'Unexpected number of inv. positions')
                    else:
                        inv_pos_to_create.append(StockPosition(
                            sku=item.sku, qty=item.qty
                        ))
                
                success = True
                if len(inv_pos_to_create) > 0:
                    new_lines = self.set_inventory_level(inv_pos_to_create)
                    success = new_lines == len(inv_pos_to_create)
                
                if len(inv_position_to_update) > 0:
                    self.update_inventory_level(inv_position_to_update)

                return success
            
            case '201':  # Decrease inventory because of SO-issue
                self.update_inventory_level(data)
    
    def set_inventory_level(self, new_positions: list[StockPosition]) -> int:
        self._cur.executemany("""
                              INSERT INTO inventory 
                              (sku, qty)
                              VALUES (?, ?);
                              """,
                              [
                                  [position.sku, position.qty]
                                  for position in new_positions
                              ])
        self._con.commit()
        return self._cur.rowcount

    def update_inventory_level(self, 
                               position_changes: list[StockChange]) -> None:
        self._cur.executemany("""
                              UPDATE inventory SET
                                  qty = ?
                              WHERE position_id = ?
                              """,
                              [
                                  [position.qty, position.position]
                                  for position in position_changes
                              ])

    def get_inventory_level(self, skus: list[int]) -> list[StockPosition]:
        lines = (
            self._cur
            .execute(f"""
                     SELECT position_id, sku, qty FROM inventory
                     WHERE sku in ({','.join(len(skus)*['?'])})""",
                     skus)
            .fetchall()
        )

        return [
            StockPosition(position=line[0], sku=line[1], qty=line[2])
            for line in lines
            ]

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
            .execute("SELECT name FROM external_entity WHERE id=?",
                     [(entity_id)])
            .fetchone()
        )
        if checker is None:
            return False
        elif len(checker) == 1:
            return True
        raise Exception((
            f'Unexpected exception: ',
            f'More than 1 external entity found for id: {entity_id}'
            ))
    
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
        return all([
            expected_table in list_tables
            for expected_table in SBB_DBAdmin.DB_TABLES
            ])
    
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
                              position_id INTEGER PRIMARY KEY,
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
        
