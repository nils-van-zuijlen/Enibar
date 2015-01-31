# Copyright (C) 2014-2015 Bastien Orivel <b2orivel@enib.fr>
# Copyright (C) 2014-2015 Arnaud Levaufre <a2levauf@enib.fr>
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
Barcode Adding Window
====================


"""


from PyQt5 import QtWidgets, uic, QtCore
from gui.douchette_window import AskDouchetteWindow
import gui.utils
import api.prices


class AddingBarcodeWindow(QtWidgets.QDialog):
    """ AddingBarcodeWindow class
    """
    def __init__(self, price_id):
        super().__init__()
        uic.loadUi('ui/barcode_adding_window.ui', self)
        self.price_id = price_id
        self.widgets = []
        self.win = None
        for barcode in api.prices.get_barcodes(price_id):
            self.add_widget(self.price_id, barcode['value'])
        self.show()

    def on_add_click(self):
        """ Called when we click on the add button
        """
        self.win = AskDouchetteWindow(self.on_add_callback)

    def on_add_callback(self, barcode):
        """ Called after the douchette is fired
        """
        if not api.prices.set_barcode(self.price_id, barcode):
            gui.utils.error("Erreur", "Ce code barre est déjà utilisé")
            return
        self.add_widget(self.price_id, barcode)

    def add_widget(self, price_id, barcode):
        w = BarcodeWidget(self.barcodes, price_id, barcode)
        self.barcodes_layout.addWidget(w)
        self.barcodes_layout.setAlignment(w, QtCore.Qt.AlignTop)
        self.widgets.append(w)


class BarcodeWidget(QtWidgets.QWidget):
    def __init__(self, parent, price_id, barcode):
        super().__init__(parent)
        self.price_id = price_id
        self.barcode = barcode
        self.label = QtWidgets.QLabel(str(barcode), self)
        self.del_button = QtWidgets.QPushButton("Supprimer", self)
        self.del_button.clicked.connect(self.on_del_click)
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.del_button)

    def on_del_click(self):
        api.prices.delete_barcode(self.barcode)
        self.setVisible(False)  # Just hide it...

