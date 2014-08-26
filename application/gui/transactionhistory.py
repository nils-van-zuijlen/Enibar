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
import api.transactions


class TransactionHistory(QtWidgets.QDialog):
    """ Base class for panels
    """
    def __init__(self, parent):
        super().__init__(parent)
        uic.loadUi('ui/history.ui', self)
        self.transaction_list.setColumnWidth(0, 120)
        self.transaction_list.setColumnWidth(1, 120)
        self.transaction_list.setColumnWidth(2, 120)
        self.transaction_list.setColumnWidth(3, 120)
        self.transaction_list.setColumnWidth(4, 120)
        self.transaction_list.setColumnWidth(5, 75)
        self.transaction_list.setColumnWidth(6, 50)
        self.transaction_list.setColumnWidth(7, 50)
        self.build()
        self.show()

    def build(self):
        """ Buildhistory list
        """
        for transaction in api.transactions.get():
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
                str(debit)
            ])
            self.transaction_list.addTopLevelItem(widget)

