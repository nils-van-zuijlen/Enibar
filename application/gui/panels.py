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
from .auth_prompt import ask_auth


def fail_callback_dummy():
    """ Dummy callback. Because a classmethod cannot be a callback
    """
    Panels.fail_callback()


class Panels(QtWidgets.QTabWidget):
    """ Base class for panels
    """
    _parent = None

    def __init__(self, parent):
        super().__init__(parent)
        Panels._parent = self.parent()
        self.main_window = parent.parent()
        self.panels = []

    def build(self):
        """ Build panels from panels found in database
        """
        for panel in api.panels.get(hidden=False):
            widget = PanelTab(panel['id'], self.main_window)
            self.panels.append(widget)
            self.addTab(widget, panel['name'])

    @ask_auth("manage_products", fail_callback=fail_callback_dummy)
    def change_alcohol(self, _):
        """ Dummy fnction. Only here to ask a password on alcohol view state
            change.
        """
        self.rebuild()

    def rebuild(self):
        """ Clear panels and build them back
        """
        self.clear()
        self.build()

    @classmethod
    def fail_callback(cls):
        """ called when the auth to hide alcochol fails
        """
        hide_alcohol = cls._parent.parent().hide_alcohol
        hide_alcohol.setChecked(not hide_alcohol.isChecked())


class PanelTab(QtWidgets.QWidget):
    """ Panel widget
    """
    def __init__(self, panel_id, main_window):
        super().__init__()
        self.panel_id = panel_id
        self.main_window = main_window
        uic.loadUi('ui/panel.ui', self)
        self.scroll_area_content.panel_id = self.panel_id
        self.scroll_area_content.build()
        self.connect_signals()

    def connect_signals(self):
        """ Connect signals of products widgets with product_clicked
        """
        products = self.scroll_area_content.products
        for cat in products.values():
            for product in cat['products'].values():
                product['widget'].get_signal().connect(self.product_clicked)
                product['widget'].connect_mouse_wheel(self.product_wheeled)

    def product_clicked(self, index=None):
        """ Product clicked
        used to connect with products widgets clicked action. as they can be of
        two types (qpushbutton or qcombobox) we will be connected to a clicked
        or activated slot. the first one will not give us any argument but as
        the price list contain only one item it's easy to handle the second one
        give use selected index in the combobox and so we must fetch which
        price it refers to.

        :param int index: Optional selected index.
        """
        widget = self.sender()

        if not index and len(widget.prices) == 1:
            price_name, price_value = tuple(iter(widget.prices.items()))[0]
        else:
            price_name = widget.itemText(index)
            price_value = widget.prices[price_name]
        self.main_window.product_list.add_product(
            widget.category_name,
            widget.name,
            price_name,
            price_value
        )

    def product_wheeled(self, event, category, name, price, value):
        """ Wheel callback

        :param QWheelEvent event: qt wheel event
        :param str category: category name
        :param str name: product name
        :param str price: product price name
        :param float value: product price
        """
        # pylint: disable=too-many-arguments
        if event.angleDelta().y() >= 0:
            self.main_window.product_list.add_product(
                category,
                name,
                price,
                value
            )
        else:
            self.main_window.product_list.del_product(
                category,
                name,
                price,
                value
            )


class ProductList(QtWidgets.QTreeWidget):
    """ Product list
    This is the product list for the main window, whihc is used to build a
    transaction. This this file may not be the right one for this class.
    """
    # pylint: disable=too-many-public-methods
    def __init__(self, parent):
        super().__init__(parent)
        self.products = []
        self.setColumnWidth(0, 60)
        self.setColumnWidth(1, 130)
        self.setColumnWidth(2, 50)

    def add_product(self, category_name, product_name, price_name, price):
        """ Add product to list
        """
        name = "{} ({}) - {}".format(product_name, price_name, category_name)
        for product in self.products:
            if product['name'] == name:
                product['price'] += price
                product['price'] = round(product['price'], 2)
                product['count'] += 1
                product['widget'].setText(0, str(product['count']))
                product['widget'].setText(2, str(product['price']))
                break
        else:
            product = {
                'name': name,
                'price': price,
                'count': 1,
                'category': category_name,
                'product': product_name,
                'price_name': price_name,
            }
            widget = QtWidgets.QTreeWidgetItem(['1', name, str(price)])
            self.addTopLevelItem(widget)
            product['widget'] = widget
            self.products.append(product)
        self.update_total()

    def del_product(self, category_name, product_name, price_name, price):
        """ Delete product from product list
        """
        name = "{} ({}) - {}".format(product_name, price_name, category_name)
        for i, product in enumerate(self.products):
            if product['name'] == name:
                if product['count'] > 1:
                    product['price'] -= price
                    product['price'] = round(product['price'], 2)
                    product['count'] -= 1
                    product['widget'].setText(0, str(product['count']))
                    product['widget'].setText(2, str(product['price']))
                else:
                    self.takeTopLevelItem(i)
                    del self.products[i]

        self.update_total()

    def clear(self):
        """ Clear the list
        """
        super().clear()
        self.products = []
        main_window = self.parent().parent().parent()
        main_window.eco_diff = 0
        main_window.refresh_ecocups()
        main_window.total.setText("0.00 €")
        main_window.notes_list.setFocus()

    def get_total(self):
        """ Sum up all prices in the list

        :return float: total
        """
        total = sum(item["price"] for item in self.products)
        return round(total, 2)

    def update_total(self):
        """ Update main window total
        """
        main_window = self.parent().parent().parent()
        text = "{:.2f} €".format(self.get_total())
        main_window.total.setText(text)


class ProductsContainer(QtWidgets.QWidget):
    """ Product Container
    This is the main product container. It's a scrollable area which contain
    columns to create a nice and optimised layout for displaying products in
    their categories.
    before calling build one must set the panel_id attribute to the panel id
    you want to build product container.
    """
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
        """ Build
        Build the product list with all categories and products of the given
        panel. All products of the panel are fetched from database and are
        sorted in their respectives categories. Widgets used to insert
        categores and products are build on the fly.  Then all categories are
        sorted into columns in an oprimised maner.
        """
        try:
            if self.parent().parent().parent().main_window.\
               hide_alcohol.isChecked():
                alcoholic_categories = [item['id'] for item in
                                        api.categories.get(alcoholic=True)]
            else:
                alcoholic_categories = []
        except AttributeError:  # The first time, the menu does not exist...
            alcoholic_categories = []

        if not self.panel_id:
            raise Exception(
                "{} attribute plane_id must not be None when "
                "calling build method.".format(str(self))
            )
        self.products = {}
        content = list(api.panels.get_content(panel_id=self.panel_id))
        content = sorted(content, key=lambda x: x['product_name'].lower())
        for product in content:
            cid = product['category_id']
            if cid in alcoholic_categories:
                continue
            pid = product['product_id']
            if cid not in self.products:
                self.products[cid] = {
                    'name': product['category_name'],
                    'widget': CategoryContainer(product['category_name']),
                    'products': {}
                }
            if pid not in self.products[cid]['products']:
                prices = self.fetch_prices(pid)
                price_sum = sum([price for _, price in prices.items()])
                if not prices or not price_sum:
                    continue
                widget = get_product_widget(
                    cid,
                    pid,
                    product['product_name'],
                    product['category_name'],
                    prices,
                )
                self.products[cid]['products'][pid] = {
                    'widget': widget,
                    'name': product['product_name'],
                    'prices': prices,
                }
                self.products[cid]['widget'].layout.addWidget(widget)

        indexes = reversed(sorted(
            self.products,
            key=lambda x: len(self.products[x]['products'])
        ))
        for cat in indexes:
            col = self.get_least_filled()
            if not len(self.products[cat]['products']):
                continue
            col.count += len(self.products[cat]['products'])
            col.layout.addWidget(self.products[cat]['widget'])
            self.products[cat]['widget'].finalise()

    @staticmethod
    def fetch_prices(pid):
        """ Fetch prices
        Fetch prices of the given id

        :param int pid: Product id
        :return OrderedDict: prices
        """
        prices = collections.OrderedDict()
        for price in api.prices.get(product=pid):
            prices[price['label']] = price['value']
        return prices

    def get_least_filled(self):
        """ Get least filled
        Get the least filled column according to the value of their count
        attribute

        :return Column: least filled column
        """
        least = None
        for col in self.columns:
            if not least:
                least = col
                continue
            if col.count < least.count:
                least = col
        return least


class Column(QtWidgets.QWidget):
    """ Column
    Used to set a nice and optimised layout to display categories in an
    optimised way.  Each aded category incresed the count attribute by the
    number of product it contains.
    """
    def __init__(self):
        super().__init__()
        self.count = 0
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(5, 0, 5, 0)
        self.setLayout(self.layout)


class CategoryContainer(QtWidgets.QGroupBox):
    """ Catgory container
    QGroupBox which contain all products of a given category
    """
    def __init__(self, category_name):
        super().__init__(category_name)
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        self.spacer = None

        cat = api.categories.get_unique(name=category_name)
        if not cat:
            return

        self.setStyleSheet(
            "QGroupBox{{background-color: {}}}".format(cat['color'])
        )

    def finalise(self):
        """ Finalise
        Add a spacer at the bottom of the QGroupBox layout
        """
        policy = QtWidgets.QSizePolicy.Expanding
        self.spacer = QtWidgets.QSpacerItem(0, 0, vPolicy=policy)
        self.layout.addItem(self.spacer)


class BaseProduct:
    """ base Product
    Abstract class inherited by Button and ComboBox which store all required
    products information on the destination widget.
    """
    # pylint: disable=too-few-public-methods
    # pylint: disable=too-many-arguments
    def __init__(self, cid, pid, name, cat_name, prices):
        super().__init__()
        self.cid = cid
        self.pid = pid
        self.name = name
        self.category_name = cat_name
        self.prices = prices

    def get_signal(self):
        """ Get signal
        Abstract method which should be implemented by child classes to give a
        signal on which you can connect to receive when a product is clicked or
        selected.
        """
        raise NotImplementedError

    def connect_mouse_wheel(self, _):
        """ Connect mouse wheel to the product so it add or removes product
        easely. It must be implemented in all child classes.
        """
        raise NotImplementedError


class Button(BaseProduct, QtWidgets.QPushButton):
    """ Button
    Button used to display products which contain a single price.
    """
    # pylint: disable=too-many-arguments
    def __init__(self, cid, pid, name, cat_name, prices):
        BaseProduct.__init__(self, cid, pid, name, cat_name, prices)
        QtWidgets.QPushButton.__init__(self, name)
        self.wheel_callback = None
        self.price_name, self.price_value = tuple(iter(prices.items()))[0]

    def connect_mouse_wheel(self, func):
        self.wheel_callback = func

    def wheelEvent(self, event):
        """ WheelEvent
        """
        # pylint: disable=invalid-name
        if self.wheel_callback:
            self.wheel_callback(
                event,
                self.category_name,
                self.name,
                self.price_name,
                self.price_value
            )
        else:
            self.ignore()

    def get_signal(self):
        return self.clicked


class ComboBox(BaseProduct, QtWidgets.QComboBox):
    """ Combobox
    ComboBox used to display products which contain multiple prices. It allow
    to change list state when clicked and reset itself when it loses focus or
    item is clicked so product name is allways displayed while you can still
    select a given price
    """
    # pylint: disable=too-many-arguments
    def __init__(self, cid, pid, name, cat_name, prices):
        QtWidgets.QComboBox.__init__(self)
        BaseProduct.__init__(self, cid, pid, name, cat_name, prices)
        self.product_view = QtWidgets.QListWidget()
        self.product_view.wheelEvent = self.caca
        self.setModel(self.product_view.model())
        self.widgets = []
        self.call = None

        self.product_view.addItem(QtWidgets.QListWidgetItem(self.name))
        for price in prices:
            widget = QtWidgets.QListWidgetItem(price)
            widget.setSizeHint(QtCore.QSize(100, 35))
            self.product_view.addItem(widget)

        self.setView(self.product_view)
        self.activated.connect(self.callback)

    def caca(self, event):
        """ Call back when wheel is used
        """
        current_price = self.product_view.currentItem().text()
        self.call(
            event,
            self.category_name,
            self.name,
            current_price,
            self.prices[current_price]
        )

    def get_signal(self):
        return self.activated

    def connect_mouse_wheel(self, func):
        self.call = func

    def callback(self, _):
        """ Activated callback.
        Reset ComboxBox state when item is clicked
        """
        self.product_view.setRowHidden(0, False)
        self.setCurrentIndex(0)

    def mousePressEvent(self, _):
        """ Overwrite qt mouse press event for the ComboBox so product name is
        hidden and user can only click on prices.
        """
        # pylint: disable=invalid-name
        self.product_view.setRowHidden(0, True)
        self.setCurrentIndex(1)
        self.showPopup()

    def mouseReleaseEvent(self, _):
        """ Overwrite qt mouse release event for the ComboBox so product name
        is displayed and selected when mouse is released.
        """
        # pylint: disable=invalid-name
        self.product_view.setRowHidden(0, False)
        self.setCurrentIndex(0)

    def wheelEvent(self, _):
        """ Overwrite qt mouse wheel event so the selection do not change when
        using wheel.
        """
        # pylint: disable=invalid-name
        # pylint: disable=no-self-use
        return

    def keyPressEvent(self, event):
        """ Overwrite qt key press event
        """
        # pylint: disable=invalid-name
        # pylint: disable=no-self-use
        event.ignore()

    def keyReleaseEvent(self, event):
        """ Overwrite qt key release event
        """
        event.ignore()

    def hidePopup(self):
        """ Overwrite qt hidePopup event so product name is displayed and
        selected again on the combobox.
        """
        # pylint: disable=invalid-name
        self.product_view.setRowHidden(0, False)
        self.setCurrentIndex(0)
        super().hidePopup()


def get_product_widget(cid, pid, name, cat_name, prices):
    """ Get prduct widget
    Select best widget between Button and ComboBox to use regarding the price
    list. If prices are set to 0 they will not be displayed. Knowing that, you
    must be sure to provide at least one price in the prices list (by filtering
    products which have no prices at all and/or product which prices sum is
    equal to 0).

    :param int cid: Category id
    :param int pid: Product id
    :param str name: Product name
    :param OrderedDict prices: Products prices.
    :return BaseProduct: Widget
    """
    valid_prices = collections.OrderedDict()
    for price, value in prices.items():
        if value != 0:
            valid_prices[price] = value

    if len(valid_prices) == 1:
        widget = Button(cid, pid, name, cat_name, valid_prices)
    else:
        widget = ComboBox(cid, pid, name, cat_name, valid_prices)

    # Set attributes
    widget.setMinimumSize(QtCore.QSize(100, 35))
    return widget

