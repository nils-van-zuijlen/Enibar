# Copyright (C) 2014-2018 Bastien Orivel <b2orivel@enib.fr>
# Copyright (C) 2014-2018 Arnaud Levaufre <a2levauf@enib.fr>
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
Panels Widget for Main window
=============================

"""

from PyQt5 import QtWidgets, QtCore, uic
import api.panels
import settings
from .auth_prompt_window import ask_auth
import api.redis
import rapi
import operator


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
        for name, panel in sorted(rapi.panels.get_all().items()):
            if settings.SHOWN_PANELS and name not in settings.SHOWN_PANELS:
                continue
            widget = PanelTab(panel, self.main_window)
            if not widget.empty:
                self.panels.append(widget)
                self.addTab(widget, name)

    @ask_auth("manage_products", fail_callback=fail_callback_dummy)
    def change_alcohol(self, _):
        """ Dummy fnction. Only here to ask a password on alcohol view state
            change.
        """
        def callback():
            api.redis.send_message("enibar-alcohol", "")
        api.redis.set_key("alcohol",
                          str(int(not self.parent().parent().hide_alcohol.isChecked())),
                          callback)

    def rebuild(self):
        """ Clear panels and build them back
        """
        selected = self.currentIndex()
        self.clear()
        self.build()
        self.setCurrentIndex(selected)

    @classmethod
    def fail_callback(cls):
        """ called when the auth to hide alcochol fails
        """
        hide_alcohol = cls._parent.parent().hide_alcohol
        hide_alcohol.setChecked(not hide_alcohol.isChecked())


class PanelTab(QtWidgets.QWidget):
    """ Panel widget
    """
    def __init__(self, panel, main_window):
        super().__init__()
        self.main_window = main_window
        uic.loadUi('ui/panel_widget.ui', self)
        self.scroll_area_content.build(panel)
        self.connect_signals()

    @property
    def empty(self):
        return self.scroll_area_content.empty

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
        if not widget.should_accept_adding_products:
            return

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
        widget.should_accept_adding_products = True

    def product_wheeled(self, event, category, name, price, value):
        """ Wheel callback

        :param QWheelEvent event: qt wheel event
        :param str category: category name
        :param str name: product name
        :param str price: product price name
        :param float value: product price
        """
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
    def __init__(self, parent):
        super().__init__(parent)
        self.products = []
        self.setColumnWidth(0, 60)
        self.setColumnWidth(1, 130)
        self.setColumnWidth(2, 50)

    def add_product(self, cname, pname, price_name, price):
        """ Add product to list

        :param str cname: Category name
        :param str pname: Product name
        :param str price_name: Price name
        :param float price: Price value
        """
        name = "{} ({}) - {}".format(pname, price_name, cname)
        for product in self.products:
            if product['name'] == name:
                product['price'] += price
                product['price'] = product['price']
                product['count'] += 1
                product['widget'].setText(0, str(product['count']))
                product['widget'].setText(2, str(round(product['price'], 2)))
                break
        else:
            product = {
                'name': name,
                'price': price,
                'count': 1,
                'category': cname,
                'product': pname,
                'price_name': price_name,
                'deletable': False if pname == settings.ECOCUP_NAME else True,
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
                    product['price'] = product['price']
                    product['count'] -= 1
                    product['widget'].setText(0, str(product['count']))
                    product['widget'].setText(2, str(round(product['price'], 2)))
                else:
                    self.takeTopLevelItem(i)
                    del self.products[i]

                if product['product'] == settings.ECOCUP_NAME and \
                   product['category'] == settings.ECOCUP_CATEGORY:
                    if product['price_name'] == settings.ECOCUP_PRICE_TYPES['take']:
                        self.parent().parent().parent().eco_diff -= 1
                    else:
                        self.parent().parent().parent().eco_diff += 1
                    self.parent().parent().parent().refresh_ecocup_button()
                break

        self.update_total()

    def keyPressEvent(self, event):
        """ We need to rewrite this to allow deletion of products
        """
        item = self.currentItem()
        if not item:
            return

        index = self.indexOfTopLevelItem(item)
        product = self.products[index]

        if event.key() == QtCore.Qt.Key_Delete:
            if event.modifiers() == QtCore.Qt.ShiftModifier:
                for _ in range(product['count']):
                    self.del_product(
                        product['category'],
                        product['product'],
                        product['price_name'],
                        round(product['price'] / product['count'], 2)
                    )
            else:
                self.del_product(
                    product['category'],
                    product['product'],
                    product['price_name'],
                    round(product['price'] / product['count'], 2)
                )
        else:
            return super().keyPressEvent(event)

    def clear(self):
        """ Clear the list
        """
        super().clear()
        self.products = []
        main_window = self.parent().parent().parent()
        main_window.eco_diff = 0
        main_window.refresh_ecocup_button()
        main_window.total.setText("0.00 €")
        main_window.notes_list.setFocus()

    def get_total(self):
        """ Sum up all prices in the list

        :return float: total
        """
        total = sum(item["price"] for item in self.products)
        return total

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
    """
    def __init__(self):
        super().__init__()
        self.products = {}
        self.columns = [Column(), Column(), Column()]

        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)
        for col in self.columns:
            self.layout.addWidget(col)
        self.layout.setContentsMargins(0, 0, 0, 0)

    def build(self, content):
        """ Build
        Build the product list with all categories and products of the given
        panel. All products of the panel are fetched from database and are
        sorted in their respective categories. Widgets used to insert
        categories and products are built on the fly.  Then all categories are
        sorted into columns in an optimised manner.
        """
        show_alcohols = not self.parent().parent().parent().main_window.hide_alcohol.isChecked()

        self.products = {}
        for category_name, category in sorted(content.items()):
            if not show_alcohols and category['alcoholic']:
                continue
            cid = category['category_id']

            self.products[cid] = {
                'name': category_name,
                'widget': CategoryContainer(category_name, category['color']),
                'products': {}
            }

            for product_name, product in sorted(
                    category['products'].items(),
                    key=lambda x: x[0].replace('&', '')):
                pid = product['product_id']

                widget = get_product_widget(
                    cid,
                    pid,
                    product_name,
                    category_name,
                    product['prices'],
                    product['percentage']
                )
                self.products[cid]['products'][pid] = {
                    'widget': widget,
                    'name': product_name,
                    'prices': product['prices'],
                }
                self.products[cid]['widget'].layout.addWidget(widget)

        indexes = reversed(sorted(
            self.products,
            key=lambda x: len(self.products[x]['products'])
        ))
        for cat in indexes:
            col = self.get_least_filled()
            if not self.products[cat]['products']:
                continue
            col.count += len(self.products[cat]['products'])
            col.layout.addWidget(self.products[cat]['widget'])
            self.products[cat]['widget'].finalise()

    @property
    def empty(self):
        return not bool(self.products)

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
    def __init__(self, category_name, category_color):
        super().__init__(category_name)
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        self.spacer = None

        self.setStyleSheet(
            "QGroupBox{{background-color: {}}}".format(category_color)
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


def underline(word):
    new_word = ""
    i = 0
    while i < len(word):
        c = word[i]
        if c == '&' and word[i + 1] == '&':
            new_word += '&'
            i += 2
            continue
        elif c == '&':
            new_word += "<span style=\"text-decoration: underline\">{}</span>".format(word[i + 1])
            i += 2
            continue
        new_word += c
        i += 1
    return new_word


class Button(BaseProduct, QtWidgets.QPushButton):
    """ Button
    Button used to display products which contain a single price.
    """
    def __init__(self, cid, pid, name, cat_name, prices, percentage=None):
        BaseProduct.__init__(self, cid, pid, name, cat_name, prices)
        QtWidgets.QPushButton.__init__(self, name)
        shortcut = self.shortcut()
        self.setText("")
        self.setShortcut(shortcut)
        name = underline(name)
        self.setText("")

        self.label_layout = QtWidgets.QGridLayout(self)
        if percentage:
            self.label = QtWidgets.QLabel(
                f"{name} <span style=\"color: red; font-size: 7px\">{percentage:.2f} °</span>",
                self)
        else:
            self.label = QtWidgets.QLabel(name, self)

        def mousePressEvent(e):
            self.mousePressEvent(e)

        def mouseReleaseEvent(e):
            self.mouseReleaseEvent(e)

        self.label.mousePressEvent = mousePressEvent
        self.label.mouseReleaseEvent = mouseReleaseEvent
        self.label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.label_layout.addWidget(self.label, 0, 0)

        self.wheel_callback = None
        self.price_name, self.price_value = list(prices.items())[0]
        self.should_accept_adding_products = True

    def connect_mouse_wheel(self, func):
        self.wheel_callback = func

    def wheelEvent(self, event):
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
    item is clicked so product name is always displayed while you can still
    select a given price.

    To avoid adding 2 products when we press on enter, we use the
    should_accept_adding_products variable. It's True when we wheel over
    something or when we click it but not when we press enter.
    """
    def __init__(self, cid, pid, name, cat_name, prices, percentage=None):
        QtWidgets.QComboBox.__init__(self)
        BaseProduct.__init__(self, cid, pid, name, cat_name, prices)
        self.product_view = QtWidgets.QListWidget()
        self.product_view.wheelEvent = self.on_wheel
        self.setModel(self.product_view.model())
        self.widgets = []
        self.call = None
        self.should_accept_adding_products = False

        self.name_item = QtWidgets.QListWidgetItem("")
        self.name_layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.name_layout)

        if percentage:
            self.name_label = QtWidgets.QLabel(
                f"{name} <span style=\"color: red; font-size: 7px\">{percentage:.2f} °</span>",
                self)
        else:
            self.name_label = QtWidgets.QLabel(name)
        self.name_label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.name_layout.addWidget(self.name_label)

        self.product_view.addItem(self.name_item)

        for price_label in sorted(prices, key=operator.itemgetter(1)):
            widget = QtWidgets.QListWidgetItem(price_label)
            widget.setTextAlignment(QtCore.Qt.AlignHCenter |
                                    QtCore.Qt.AlignVCenter)
            widget.setSizeHint(QtCore.QSize(100, 35))
            self.product_view.addItem(widget)

        self.setView(self.product_view)
        self.activated.connect(self.callback)
        self.product_view.pressed.connect(self.on_click)

    def on_click(self, _):
        """ Called when we click on an item to close the QComboBox and not when
            we press enter. It allows us to add a product only in this case
        """
        self.should_accept_adding_products = True

    def on_wheel(self, event):
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
        self.should_accept_adding_products = False

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
        self.should_accept_adding_products = False
        self.product_view.setRowHidden(0, True)
        self.setCurrentIndex(1)
        self.showPopup()

    def mouseReleaseEvent(self, _):
        """ Overwrite qt mouse release event for the ComboBox so product name
        is displayed and selected when mouse is released.
        """
        self.product_view.setRowHidden(0, False)
        self.setCurrentIndex(0)

    def wheelEvent(self, _):
        """ Overwrite qt mouse wheel event so the selection do not change when
        using wheel.
        """
        return

    def keyPressEvent(self, event):
        """ Overwrite qt key press event
        """
        event.ignore()

    def keyReleaseEvent(self, event):
        """ Overwrite qt key release event
        """
        event.ignore()

    def hidePopup(self):
        """ Overwrite qt hidePopup event so product name is displayed and
        selected again on the combobox.
        """
        self.product_view.setRowHidden(0, False)
        self.setCurrentIndex(0)
        super().hidePopup()


def get_product_widget(cid, pid, name, cat_name, prices, percentage=None):
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
    if len(prices) == 1:
        widget = Button(cid, pid, name, cat_name, prices, percentage)
    else:
        widget = ComboBox(cid, pid, name, cat_name, prices, percentage)

    # Set attributes
    widget.setMinimumSize(QtCore.QSize(100, 35))
    return widget
