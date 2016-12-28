# Copyright (C) 2014-2016 Bastien Orivel <b2orivel@enib.fr>
# Copyright (C) 2014-2016 Arnaud Levaufre <a2levauf@enib.fr>
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
Consumption managment window
"""

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import uic
import gui.utils
import api.products
import api.categories
import api.prices
import api.validator


class ProductsManagementWindow(QtWidgets.QDialog):
    """ Consumption ManagmentWindow
    This window allow user to add products, productcategories and prices.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('ui/products_management_window.ui', self)
        self.tab_manage_categories.on_change = self.on_change
        self.tab_manage_consumptions.on_change = self.on_change
        self.input_cat.set_validator(api.validator.NAME)
        self.input_product.set_validator(api.validator.NAME)
        self.category = None
        self.products.build()
        self.products.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.color_picker = QtWidgets.QColorDialog(self)
        self.win = None
        self.tabs.currentChanged.connect(self.products.rebuild)
        self.show()

    def on_change(self):
        """ Called when the inputs change
        """
        self.button_cat_add.setDefault(True)
        self.button_product_add.setDefault(True)
        self.button_cat_add.setEnabled(self.input_cat.valid)
        self.button_product_add.setEnabled(self.input_product.valid)

    def add_product(self):
        """ Add product
        Add a new product with the name found in the product name input and
        update the product list displayed on screen.
        """
        pname = self.input_product.text()
        indexes = self.products.selectedIndexes()
        if not len(indexes) == 1:
            gui.utils.error(
                "Impossible de déterminer la catégorie.",
                "Il est impossible de déterminer la catégorie de destination "
                "lorsqu' aucun ou plusieurs produits sont sélectionnés."
            )
            return
        index = indexes[0]
        cat_name = None
        if index.parent().isValid():
            cat_name = index.parent().data()
        elif index.data():
            cat_name = index.data()
        if cat_name and api.products.add(pname, category_name=cat_name):
            self.products.add_product(pname, cat_name)
            self.input_product.setText("")
        elif cat_name:
            gui.utils.error("Impossible d'ajouter le produit")

    def remove_product(self):
        """ Remove product
        Removes all selected products in both database and displayed list.
        """
        indexes = self.products.selectedIndexes()
        for index in reversed(indexes):
            if not index.parent().isValid():
                continue
            parent = self.products.topLevelItem(index.parent().row())
            category = api.categories.get_unique(name=parent.text(0))
            product = api.products.get_unique(
                name=index.data(1),
                category=category['id']
            )
            if api.products.remove(product['id']):
                child = parent.takeChild(index.row())
                del child

    def save_product(self):
        """ Save product
        Save product prices given in the prices sections. This support
        multi-selection in the same category to allow user to update similar
        prices at once (e.g: cans).
        """
        indexes = self.products.selectedIndexes()
        new_prices = []
        for index in indexes:
            if not index.parent().isValid():
                continue
            cat = api.categories.get_unique(name=index.parent().data())
            if not cat:
                continue
            product = api.products.get_unique(
                name=index.data(1),
                category=cat['id']
            )
            if not product:
                continue
            prices = api.prices.get(product=product['id'])
            for price in prices:
                for widget in self.prices.widgets:
                    if widget.label.text() != price['label']:
                        continue
                    new_prices.append({
                        'id': price['id'],
                        'value': widget.input.value(),
                        'percentage': widget.percentage_input.value() if cat['alcoholic'] else 0,
                    })
        if not api.prices.set_multiple_values(new_prices):
            gui.utils.error("Erreur", "Impossible de sauvegarder les nouveaux prix")

        if self.name_input.isEnabled():
            if api.products.rename(product['id'], self.name_input.text()):
                for item in self.products.selectedItems():
                    item.setData(0, 1, self.name_input.text())

        for item in self.products.selectedItems():
            if self.name_input.isEnabled():
                name = self.name_input.text()
            else:
                name = item.data(0, 1)

            if new_prices:
                price = new_prices[0]
                self.products.itemWidget(item, 0).setText('{} <span style="color: grey">[{:.2f}]</span>'.format(name, price['value']))
            else:
                self.products.itemWidget(item, 0).setText(name)

    def select_product(self):
        """ Select product
        verify that selected prducts are all under the same category and allow
        or deny access to price control.
        """
        parent = None
        invalid = False
        indexes = self.products.selectedIndexes()

        if not indexes:
            self.prices.setEnabled(False)
            self.input_product_save.setEnabled(False)
            self.name_input.setEnabled(False)
            return

        if len(indexes) > 1:
            self.name_input.setEnabled(False)
        else:
            self.name_input.setEnabled(True)
            ConsumptionPricesItem.BUTTON_ENABLED = True

        for index in indexes:
            if not index.parent().isValid():
                self.name_input.setEnabled(False)
                continue
            if parent and index.parent() != parent:
                invalid = True
                break
            parent = index.parent()

        item = indexes[-1]
        if item.parent().isValid() and not invalid:
            self.prices.rebuild(item.data(1), item.parent().data())
            self.name_input.setText(item.data(1))
            self.prices.setEnabled(True)
            self.input_product_save.setEnabled(True)
        else:
            self.name_input.setText("")
            self.prices.clean()
            self.prices.setEnabled(False)
            self.input_product_save.setEnabled(False)

    def add_category(self):
        """ Add category to category list.
        """
        cat_name = self.input_cat.text()
        if api.categories.add(cat_name):
            self.categories.add_category(cat_name)
            self.input_cat.setText('')
        else:
            gui.utils.error(
                "Impossible d'ajouter la catégorie.",
                "Le nom d'une catégorie est unique."
            )

    def remove_category(self):
        """ Callback to remove category
        """
        for index in reversed(self.categories.selectedIndexes()):
            if api.categories.remove(index.data()):
                item = self.categories.takeItem(index.row())
                del item

    def save_category(self):
        """ Callback to save category
        """
        cat = api.categories.get_unique(name=self.category.text())

        for widget in self.category_prices.widgets:
            if widget.id_ and widget.input.text():
                api.prices.change_descriptor(widget.id_, widget.input.text(), widget.quantity_input.value())
            elif widget.input.text():
                widget.id_ = api.prices.add_descriptor(
                    widget.input.text(),
                    cat['id'],
                    widget.quantity_input.value())
            else:
                api.prices.remove_descriptor(widget.id_)
        is_alcoholic = self.checkbox_alcoholic.isChecked()
        api.categories.set_alcoholic(cat['id'], is_alcoholic)
        if api.categories.rename(self.category.text(), self.cat_name_input.text()):
            self.category.setText(self.cat_name_input.text())

    def add_category_price(self):
        """ Add category price to category price list
        This is a callback for the button_cat_price
        """
        self.category_prices.add_price()

    def select_category(self, item):
        """ Select category
        This is a callback for changed selection on category list
        """
        self.category = item

        if item:
            cat = api.categories.get_unique(name=item.text())
            if cat:
                self.checkbox_alcoholic.setChecked(cat['alcoholic'])
                self.color_button.setStyleSheet(
                    "background:{}".format(cat['color'])
                )
                color = QtGui.QColor()
                color.setNamedColor(cat['color'])
                self.color_picker.setCurrentColor(color)
                self.category_prices.rebuild(item.text())
                self.cat_name_input.setText(item.text())
                self.category_prices.setEnabled(True)
                self.checkbox_alcoholic.setEnabled(True)
                self.button_cat_save.setEnabled(True)
                self.button_cat_price.setEnabled(True)
                self.category_type.setEnabled(True)
                self.color_button.setEnabled(True)
                self.cat_name_input.setEnabled(True)
                self.button_cat_save.setDefault(True)
                return

        self.category_prices.clean()
        self.category_prices.setEnabled(False)
        self.button_cat_save.setEnabled(False)
        self.button_cat_price.setEnabled(False)
        self.category_type.setEnabled(False)
        self.color_button.setEnabled(False)
        self.checkbox_alcoholic.setEnabled(False)
        self.cat_name_input.setEnabled(False)
        self.button_cat_save.setDefault(False)

    def select_color(self):
        """ Select color, called when color_button is pressed
        """
        color = self.color_picker.getColor()
        if color.isValid() and self.category:
            api.categories.set_color(self.category.text(), color.name())
            self.color_button.setStyleSheet(
                "background:{}".format(color.name())
            )

    def panels_management_fnc(self):
        self.parent().panel_managment_fnc_no_auth()


#
# Consumption
#


class ConsumptionPrices(QtWidgets.QGroupBox):
    """ Consumption prices.
    List all the prices for the current selected product. This class is used
    for gui managment only, no actions such as adding price will be done in
    database.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.widgets = []

    def add_price(self, id_, name, value, percentage):
        """ Add price to product's price list

        :param int id_: Price id
        :param str name: Price name
        :param float value: Price value
        :param float percentage: Alochol percentage
        """
        item = ConsumptionPricesItem(id_, name, value, percentage)
        self.layout().insertWidget(len(self.widgets), item)
        self.widgets.append(item)

    def clean(self):
        """ Clean all prices from the view
        """
        for _ in range(len(self.widgets)):
            widget = self.widgets.pop()
            widget.setVisible(False)
            del widget

    def rebuild(self, product, category):
        """ Rebuild the view to match selected product's prices

        :param str product: Product name
        :param str category: Category name
        """
        self.clean()
        self.build(product, category)

    def build(self, pname, cname):
        """ Build the view to match selected product's prices

        :param str pname: Product name
        :param str cname: Category name
        """
        category = api.categories.get_unique(name=cname)
        if not category:
            return
        product = api.products.get_unique(name=pname, category=category['id'])
        if not product:
            return

        for price in api.prices.get(product=product['id']):
            self.add_price(price['id'], price['label'], price['value'], price['percentage'] if category['alcoholic'] else None)


class ConsumptionPricesItem(QtWidgets.QWidget):
    """ Simple widget wrapper to handle each label, price pair as a unique item
    """
    BUTTON_ENABLED = True

    def __init__(self, id_, name, value, percentage):
        super().__init__()
        self.id_ = id_
        self.name = name
        self.value = value
        self.win = None
        self.percentage = percentage

        self.label = QtWidgets.QLabel(name)
        self.input = QtWidgets.QDoubleSpinBox()
        self.input.setSuffix("€")

        if percentage is not None:
            self.percentage_input = QtWidgets.QDoubleSpinBox()
            self.percentage_input.setSuffix("°")
        self.input.setMaximum(999.99)
        self.input.setLocale(QtCore.QLocale('English'))
        self.label.setBuddy(self.input)
        self._build()

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.input)
        if percentage is not None:
            self.layout.addWidget(self.percentage_input)

    def _build(self):
        """ Fill the inputs with walues
        """
        self.label = QtWidgets.QLabel(self.name)
        self.input.setValue(self.value)
        if self.percentage is not None:
            self.percentage_input.setValue(self.percentage)


class ConsumptionList(QtWidgets.QTreeWidget):
    """ Consumption list
    List all consumption in their respective categories
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.categories = []
        self.products = []

    def clean(self):
        """ Clean up the list
        """
        for i in range(len(self.categories) - 1, -1, -1):
            widget = self.takeTopLevelItem(i)
            del widget

    def rebuild(self):
        """ Rebuild the list
        """
        self.clean()
        self.build()

    def build(self):
        """ Build the list
        """
        self.categories = []
        self.products = []
        for cat in api.categories.get():
            self.add_category(cat['name'], cat['id'])

    def add_product(self, name, category):
        """ Add product to consumption list

        :param str name: Product name
        :param str category: Category Name
        """
        # Find category widget
        cat_widget = None
        for cat in self.categories:
            if category == cat.text(0):
                cat_widget = cat
        if not cat_widget:
            return

        prod_widget = QtWidgets.QTreeWidgetItem()
        cat_widget.addChild(prod_widget)
        self.products.append(prod_widget)

        # XXX: This is slow, maybe add dome caching ?
        cid = api.categories.get_unique(name=category)['id']
        pid = api.products.get_unique(name=name, category=cid)['id']
        prices = list(api.prices.get(product=pid))

        if not prices:
            prod_label = QtWidgets.QLabel(name)
        else:
            price = prices[0]
            prod_label = QtWidgets.QLabel('{} <span style="color: grey">[{:.2f}]</span>'.format(name, price['value']))
        prod_widget.setData(0, 1, name)
        self.setItemWidget(prod_widget, 0, prod_label)

    def add_category(self, name, id_):
        """ Add product category to product list.
        This function can't add product to database.

        :param str name: Category name
        :param int id_: Category id
        """
        cat_widget = QtWidgets.QTreeWidgetItem(self, [name])
        self.categories.append(cat_widget)
        for prod in api.products.get(category=id_):
            self.add_product(prod['name'], name)


#
# Category
#


class CategoryPrices(QtWidgets.QGroupBox):
    """ List of the prices description in category
    Note that this class is only use to manage ui, no action are done in
    database
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.widgets = []

    def add_price(self, id_=None, name="", quantity=0):
        """ Add price description to price list

        :param int id_: Price descriptor id
        :param str name: Price descriptor name
        """
        widget = CategoryPriceItem(id_, name, quantity)
        self.layout().insertWidget(len(self.widgets), widget, stretch=0)
        self.widgets.append(widget)

    def clean(self):
        """ Clean up the list
        """
        for _ in range(len(self.widgets)):
            widget = self.widgets.pop()
            widget.setVisible(False)
            del widget

    def rebuild(self, category_name):
        """ Rebuild the list according to the selected category

        :param str category_name: Selected category name
        """
        self.clean()
        self.build(category_name)

    def build(self, category_name):
        """ Build the list according to the selected category

        :param str category_name: Selected category name
        """
        cat = api.categories.get_unique(name=category_name)
        if cat:
            for desc in api.prices.get_descriptor(category=cat['id']):
                self.add_price(desc['id'], desc['label'], desc["quantity"])
        else:
            gui.utils.error("La catégorie sélectionnée n'existe pas.")


class CategoryPriceItem(QtWidgets.QWidget):
    """ Wrapper to handle input, button pair as a single widget
    """
    def __init__(self, id_, name="", quantity=0):
        super().__init__()
        self.id_ = id_
        self.input = QtWidgets.QLineEdit()
        self.quantity_input = QtWidgets.QSpinBox()
        self.quantity_input.setRange(0, 9999)
        self.quantity_input.setValue(quantity)
        self.quantity_input.setSuffix(" mL")
        self.input.setText(name)
        self.button = QtWidgets.QPushButton("Supprimer")
        self.button.clicked.connect(self.remove)
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.addWidget(self.input)
        self.layout.addWidget(self.quantity_input)
        self.layout.addWidget(self.button)

    def remove(self):
        """ Remove item from list
        """
        self.setVisible(False)
        self.input.setText("")  # Will be removed when saved


class CategoryList(QtWidgets.QListWidget):
    """ Category list
    Note that no modification are made to database when member method are called
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.categories = []
        for cat in api.categories.get():
            self.add_category(cat['name'])

        self.itemChanged.connect(self.item_changed)

    def add_category(self, cat_name):
        """ Add category to list

        :param str cat_name: Category name
        """
        widget = CategoryListItem(cat_name, self)
        widget.setFlags(
            QtCore.Qt.ItemIsEditable |
            QtCore.Qt.ItemIsEnabled |
            QtCore.Qt.ItemIsSelectable
        )
        self.currentTextChanged.connect(self.item_changed)
        self.categories.append(widget)

    def item_changed(self, item):
        """ Item changed. Connected to self.itemChanged
        Used to detect when a category is renamed and so update database.

        :param item: Text or item if text is new. (Yay that's qt)
        """

        if type(item) is CategoryListItem:
            item.rename()


class CategoryListItem(QtWidgets.QListWidgetItem):
    """ Category list item
    Used to build the category list.
    """
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.name = name

    def rename(self):
        """ Rename
        Rename category with the new name set by user.
        """
        if api.categories.rename(self.name, self.text()):
            self.name = self.text()

