# Copyright (C) 2014 Bastien Orivel <b2orivel@enib.fr>
# Copyright (C) 2014 Arnaud Levaufre <a2levauf@enib.fr>
#
# This file is part of Enibar.
#
# Enibar is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Enibar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Enibar.  If not, see <http://www.gnu.org/licenses/>.

"""
Transaction hisotry window.
"""

from PyQt5 import QtWidgets, uic
from .auth_prompt import ask_auth
import api.transactions
import re


class TransactionHistory(QtWidgets.QDialog):
    """ Base class for panels
    """
    def __init__(self, parent):
        super().__init__(parent)
        uic.loadUi('ui/history.ui', self)
        self.widgets = []
        self.transactions = list(api.transactions.get())
        self.transaction_list.setColumnWidth(0, 120)
        self.transaction_list.setColumnWidth(1, 120)
        self.transaction_list.setColumnWidth(2, 120)
        self.transaction_list.setColumnWidth(3, 120)
        self.transaction_list.setColumnWidth(4, 120)
        self.transaction_list.setColumnWidth(5, 75)
        self.transaction_list.setColumnWidth(6, 50)
        self.transaction_list.setColumnWidth(7, 50)
        self.transaction_list.setColumnWidth(8, 50)
        self.build()
        self.show()

    def build(self):
        """ Buildhistory list
        """
        for transaction in self.transactions:
            if transaction['price'] >= 0:
                credit = transaction['price']
                debit = "-"
            else:
                credit = "-"
                debit = -transaction['price']

            widget = QtWidgets.QTreeWidgetItem(self.transaction_list, [
                transaction['date'].toString("yyyy/MM/dd HH:mm:ss"),
                transaction['note'],
                transaction['category'],
                transaction['product'],
                transaction['price_name'],
                str(transaction['quantity']),
                str(credit),
                str(debit),
                str(transaction['id'])
            ])
            self.widgets.append(widget)
            self.transaction_list.addTopLevelItem(widget)

    def update_list(self, _):
        filter_ = [
            self.input_note.text(),
            self.input_category.text(),
            self.input_product.text(),
        ]
        for widget in self.widgets:
            show = True
            for index, regex in enumerate(filter_):
                if regex.lower() not in widget.text(index + 1).lower():
                    show = False

                if show:
                    widget.setHidden(False)
                else:
                    widget.setHidden(True)

    @ask_auth("manage_notes")
    def delete(self, _):
        widget = self.transaction_list.currentItem()
        if api.transactions.rollback_transaction(widget.text(8)):
            try:
                quantity = int(widget.text(5))
            except ValueError:
                quantity = 1

            if quantity > 1:
                widget.setText(5, str(quantity - 1))
                if widget.text(6) != "-":
                    credit = float(widget.text(6))
                    credit -= credit / quantity
                    credit = round(credit, 2)
                    widget.setText(6, str(credit))
                elif widget.text(7) != "-":
                    debit = float(widget.text(7))
                    debit -= debit / quantity
                    debit = round(debit, 2)
                    widget.setText(7, str(debit))
            else:
                index = self.transaction_list.indexOfTopLevelItem(widget)
                self.transaction_list.takeTopLevelItem(index)
        else:
            print("Pas supprimé")
