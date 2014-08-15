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
Consumption managment window
"""

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import uic
import gui.utils
import api.products
import api.categories
import api.prices


#class ConsumptionManagmentWindow(QtWidgets.QDialog):
#    """
#    Consumption managment window
#    """
#    def __init__(self):
#        super().__init__()
#        uic.loadUi('ui/consumptionmanagment.ui', self)
#        self.categories = {
#            'manger': 'Nourriture',
#            'soft': 'Boisson soft',
#            'alcool_boutielle': 'Boisson alcolisé / bouteille',
#            'alcool_pression': 'Boisson alcolisé / pression',
#        }
#        self.products = []
#
#        for product in api.products.get_all():
#            self.products.append(
#                QtWidgets.QListWidgetItem(product['name'], self.product_list)
#            )
#        try:
#            self.selected = self.products[0]
#            self.update_inputs()
#        except IndexError:
#            self.selected = None
#        self.show()
#
#    def update_inputs(self):
#        """ update value of all inputs
#        """
#        if self.selected:  # Bullshit
#            product = api.products.get_by_name(self.selected.text())
#            self.price_half = product['price_demi']
#            self.price_unit = product['price_unit']
#            self.price_pint = product['price_pint']
#            self.price_meter = product['price_meter']
#        else:
#            pass
#
#    def get_category_from_combobox(self):
#        """ Get current category from selected combobox item
#        """
#        result = None
#        for key, value in self.categories.items():
#            if value == self.category_list.currentText():
#                result = key
#        if not result:
#            raise Exception(
#                "Unkown product category from QComboBox value {}".format(
#                    self.category_list.currentText()
#                )
#            )
#        return result
#
#    def add(self):
#        """ Add product
#        """
#        if not self.add_name.text():
#            gui.utils.error(
#                "Aucun nom pour la nouvelle consommation",
#                "Le champ nom est obligatoire pour ajouter une consommation"
#            )
#            return
#        category = self.get_category_from_combobox()
#        name = self.add_name.text()
#        if api.products.add(name, category):
#            QtWidgets.QListWidgetItem(name, self.product_list)
#            self.add_name.setText("")
#        else:
#            gui.utils.error("Impossible d'ajouter cette consommation")
#
#    def save(self):
#        """ Save product
#        """
#        for index in self.product_list.selectedIndex():
#            succeed = api.products.set_prices(
#                index.data(),
#                unit=self.price_unit.text(),
#                demi=self.price_half.text(),
#                pint=self.price_pint.text(),
#                meter=self.price_meter.text()
#            )
#            if not succeed:
#                gui.utils.error(
#                    "Impossible de changer le prix pour la"
#                    "consomation {}".format(index.data())
#                )
#            succeed = api.products.set_category(
#                name,
#                self.get_category_from_combobox()
#            )
#            if not succeed:
#                gui.utils.error(
#                    "Impossible de modifier la catégorie de la"
#                    "consommation {}".format(index.data())
#                )
#
#    def delete(self):
#        """ Delete product
#        """
#        # reverse is required to delete items from list without
#        # breaking it
#        for index in reversed(self.product_list.selectedIndexes()):
#            if api.products.remove(index.data()):
#                item = self.product_list.takeItem(index.row())
#                del item
#            else:
#                gui.utils.error(
#                    "Impossible de suppimer la consomation {}".format(
#                        index.data()
#                    )
#                )


class ConsumptionManagmentWindow(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/untitled.ui', self)
        self.show()

    def add_product(self):
        pass

    def remove_product(self):
        pass

    def save_product(self):
        pass

    def add_category(self):
        cat_name = self.input_cat.text()
        if not cat_name:
            return
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
            else:
                gui.utils.error(
                    "Impossible de suppimer la categorie {}".format(
                        index.data()
                    )
                )

    def save_category(self):
        """ Callback to save category
        """
        if not self.category:
            return
        for widget in self.category_prices.widgets:
            if widget.id_ and widget.input.text():
                api.prices.rename_descriptor(widget.id_, widget.input.text())
            elif widget.id_:
                api.prices.remove_descriptor(widget.id_)
            elif widget.input.text():
                cat = api.categories.get_by_name(self.category.text())
                try:
                    widget.id_ = api.prices.add_descriptor(
                        widget.input.text(),
                        cat['id']
                    )
                except IndexError:
                    # FIXME Trigger error saying there is no category
                    pass


    def add_category_price(self):
        self.category_prices.add_price()

    def select_category(self, item):
        # TODO remove if useless
        self.category = item
        self.category_prices.rebuild(item.text())

#
# Consumption
#


class ConsumptionPrices(QtWidgets.QGroupBox):
    def __init__(self, parent):
        super().__init__(parent)


class ConsumptionList(QtWidgets.QTreeView):
    def __init__(self, parent):
        super().__init__(parent)

#
# Category
#


class CategoryPrices(QtWidgets.QGroupBox):
    def __init__(self, parent):
        super().__init__(parent)
        self.widgets = []

    def add_price(self, name="", id_=None):
        widget = CategoryPriceItem(name, id_)
        self.layout().insertWidget(len(self.widgets), widget, stretch=0)
        self.widgets.append(widget)

    def rebuild(self, category_name):
        for i in range(len(self.widgets)):
            widget = self.widgets.pop()
            widget.setVisible(False)
            del widget
        self.build(category_name)

    def build(self, category_name):
        cat = api.categories.get_by_name(category_name)
        if cat:
            for desc in api.prices.get_decriptor(category=cat['id']):
                self.add_price(desc['label'], desc['id'])
        else:
            # TODO error message category no longer exists
            pass

        pass


class CategoryPriceItem(QtWidgets.QWidget):
    def __init__(self, name="", id_=None):
        super().__init__()
        self.id_ = id_
        self.input = QtWidgets.QLineEdit()
        self.input.setText(name)
        self.button = QtWidgets.QPushButton("Supprimer")
        self.button.clicked.connect(self.remove)
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.addWidget(self.input)
        self.layout.addWidget(self.button)

    def remove(self):
        self.setVisible(False)
        if self.id_:
            if not api.prices.remove_descriptor(self.id_):
                # TODO error message can't delete
                pass


class CategoryList(QtWidgets.QListWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.categories = []
        for cat in api.categories.get_all():
            print(cat)
            self.add_category(cat['name'])

    def add_category(self, cat_name):
        self.categories.append(QtWidgets.QListWidgetItem(cat_name, self))
