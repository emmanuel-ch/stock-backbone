""" sbb.py
Interface to user.

Class StockBackbone - methods:
    make_PO
    receive_PO
    make_SO
    issue_SO
"""

import sbb_admin


class StockBackbone(sbb_admin.StockBackbone_Admin):

    def __init__(self):
        pass

    def make_PO(self, supplier_id: str, PO_lines: dict) -> str:
        pass

    def receive_PO(self, PO_id: str) -> bool:
        pass

    def make_SO(self, customer_id: str, SO_lines: dict) -> str:
        pass

    def issue_SO(self, SO_id: str) -> bool:
        pass

