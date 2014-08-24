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

# pylint: disable=no-value-for-parameter

"""
Panels Widget for Main window
=============================

"""

from PyQt5 import QtWidgets, QtCore, uic, QtGui
import collections
import api.panels
import copy


class Panels(QtWidgets.QTabWidget):
    """ Base class for panels
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.build()

    def build(self):
        """ Build panels from panels found in database
        """
        for panel in api.panels.get():
            self.addTab(PanelTab(panel['id']), panel['name'])

    def clear(self):
        """ Clear panels
        """

    def rebuild(self):
        """ Clear panels and build them back
        """


class PanelTab(QtWidgets.QWidget):
    """ Panel widget
    """
    def __init__(self, panel_id):
        super().__init__()
        self.panel_id = panel_id
        uic.loadUi('ui/panel.ui', self)
        b = self.palette().brush(self.backgroundRole())
        self.scroll_area_content.palette().setBrush(self.backgroundRole(), b)
        self.scroll_area_content.panel_id = self.panel_id
        self.scroll_area_content.build()
        self.product_list.setColumnWidth(0, 60)
        self.product_list.setColumnWidth(1, 130)
        self.product_list.setColumnWidth(2, 50)
        self.connect_signals()

    def connect_signals(self):
        products = self.scroll_area_content.products
        for cid, cat in products.items():
            for pid, product in cat['products'].items():
                product['widget'].get_signal().connect(self.product_clicked)

    def product_clicked(self, index=None):
        widget = self.sender()
        if not index and len(widget.prices) == 1:
            price_name, price_value = tuple(iter(widget.prices.items()))[0]
        else:
            price_name = widget.itemText(index)
            price_value = widget.prices[price_name]

        print("Yay", price_name, price_value)

    def add_product(self, name, price):
        pass


class ProductsContainer(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.panel_id = None
        self.products = {}
        self.columns = [Column(), Column(), Column()]

        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)
        for col in self.columns:
            self.layout.addWidget(col)
        self.layout.setContentsMargins(0, 0, 0, 0)

    def build(self):
        self.products = {}
        content = list(api.panels.get_content(panel_id=self.panel_id))
        content = sorted(content, key=lambda x: x['product_name'].lower())
        for product in content:
            cid = product['category_id']
            pid = product['product_id']
            if cid not in self.products:
                self.products[cid] = {
                    'name': product['category_name'],
                    'widget': CategoryContainer(product['category_name']),
                    'products': {}
                }
            if pid not in self.products[cid]['products']:
                prices = self.fetch_prices(pid)
                if not prices:
                    continue
                widget = get_product_widget(
                    cid,
                    pid,
                    product['product_name'],
                    prices,
                )
                self.products[cid]['products'][pid] = {
                    'widget': widget,
                    'name': product['product_name'],
                    'prices': prices,
                }
                self.products[cid]['widget'].layout.addWidget(widget)

        indexes = reversed(sorted(self.products, key=lambda x: len(self.products[x]['products'])))
        for cat in indexes:
            col = self.get_least_filled()
            if not len(self.products[cat]['products']):
                continue
            col.count += len(self.products[cat]['products'])
            col.layout.addWidget(self.products[cat]['widget'])
            self.products[cat]['widget'].finalise()

    def fetch_prices(self, pid):
        prices = collections.OrderedDict()
        for price in api.prices.get(product=pid):
            prices[price['label']] = price['value']
        print(prices)
        return prices

    def get_least_filled(self):
        least = None
        for col in self.columns:
            if not least:
                least = col
                continue
            if col.count < least.count:
                least = col
        return least


class Column(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.count = 0
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(5, 0, 5, 0)
        self.setLayout(self.layout)


class CategoryContainer(QtWidgets.QGroupBox):
    def __init__(self, category_name):
        super().__init__(category_name)
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

    def finalise(self):
        self.spacer = QtWidgets.QSpacerItem(0, 0, vPolicy=QtWidgets.QSizePolicy.Expanding)
        self.layout.addItem(self.spacer)


class BaseProduct:
    def __init__(self, cid, pid, name, prices):
        super().__init__()
        self.cid = cid
        self.pid = pid
        self.name = name
        self.prices = prices

    def get_signal(self):
        raise NotImplementedError


class Button(BaseProduct, QtWidgets.QPushButton):
    def __init__(self, cid, pid, name, prices):
        BaseProduct.__init__(self, cid, pid, name, prices)
        QtWidgets.QPushButton.__init__(self, name)

    def get_signal(self):
        return self.clicked


class ComboBox(BaseProduct, QtWidgets.QComboBox):
    """ Combobox
    This is a combobox which allow to change list state when clicked and reset
    itself when it losed focus or item is clicked. This is used to prompt rapid
    choise of prices for products
    """
    def __init__(self, cid, pid, name, prices):
        QtWidgets.QComboBox.__init__(self)
        BaseProduct.__init__(self, cid, pid, name, prices)
        self.product_view = QtWidgets.QListWidget()
        self.setModel(self.product_view.model())
        self.widgets = []

        self.product_view.addItem(QtWidgets.QListWidgetItem(self.name))
        for p in prices:
            widget = QtWidgets.QListWidgetItem(p)
            widget.setSizeHint(QtCore.QSize(100,35))
            self.product_view.addItem(widget)

        self.setView(self.product_view)
        self.activated.connect(self.callback)

    def get_signal(self):
        return self.activated

    def callback(self, index):
        self.product_view.setRowHidden(0, False)
        self.setCurrentIndex(0)

    def mousePressEvent(self, event):
        self.product_view.setRowHidden(0, True)
        self.setCurrentIndex(1)
        self.showPopup()

    def mouseReleaseEvent(self, event):
        print(event)
        self.product_view.setRowHidden(0, False)
        self.setCurrentIndex(0)

    def wheelEvent(self, event):
        self.parent().wheelEvent(event)

    def hidePopup(self):
        self.product_view.setRowHidden(0, False)
        self.setCurrentIndex(0)
        super().hidePopup()


def get_product_widget(cid, pid, name, prices):
    if len(prices) == 1:
        widget = Button(cid, pid, name, prices)
    else:
        widget = ComboBox(cid, pid, name, prices)

    # Set attributes
    widget.setMinimumSize(QtCore.QSize(100,35))
    return widget
