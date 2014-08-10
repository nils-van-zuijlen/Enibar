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
from PyQt5 import uic
import gui.utils
import api.products


class ConsumptionManagmentWindow(QtWidgets.QDialog):
    """
    Consumption managment window
    """
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/consumptionmanagment.ui', self)
        self.categories = {
            'manger': 'Nourriture',
            'soft': 'Boisson soft',
            'alcool_boutielle': 'Boisson alcolisé / bouteille',
            'alcool_pression': 'Boisson alcolisé / pression',
        }
        self.products = []

        for product in api.products.get_all():
            self.products.append(
                QtWidgets.QListWidgetItem(product['name'], self.product_list)
            )
        try:
            self.selected = self.products[0]
            self.update_inputs()
        except IndexError:
            self.selected = None
        self.show()

    def update_inputs(self):
        """ update value of all inputs
        """
        if self.selected:  # Bullshit
            product = api.products.get_by_name(self.selected.text())
            self.price_half = product['price_demi']
            self.price_unit = product['price_unit']
            self.price_pint = product['price_pint']
            self.price_meter = product['price_meter']
        else:
            pass

    def get_category_from_combobox(self):
        """ Get current category from selected combobox item
        """
        result = None
        for key, value in self.categories.items():
            if value == self.category_list.currentText():
                result = key
        if not result:
            raise Exception(
                "Unkown product category from QComboBox value {}".format(
                    self.category_list.currentText()
                )
            )
        return result

    def add(self):
        """ Add product
        """
        if not self.add_name.text():
            gui.utils.error(
                "Aucun nom pour la nouvelle consommation",
                "Le champ nom est obligatoire pour ajouter une consommation"
            )
            return
        category = self.get_category_from_combobox()
        name = self.add_name.text()
        if api.products.add(name, category):
            QtWidgets.QListWidgetItem(name, self.product_list)
            self.add_name.setText("")
        else:
            gui.utils.error("Impossible d'ajouter cette consommation")

    def save(self):
        """ Save product
        """
        for index in self.product_list.selectedIndex():
            succeed = api.products.set_prices(
                index.data(),
                unit=self.price_unit.text(),
                demi=self.price_half.text(),
                pint=self.price_pint.text(),
                meter=self.price_meter.text()
            )
            if not succeed:
                gui.utils.error(
                    "Impossible de changer le prix pour la"
                    "consomation {}".format(index.data())
                )
            succeed = api.products.set_category(
                name,
                self.get_category_from_combobox()
            )
            if not succeed:
                gui.utils.error(
                    "Impossible de modifier la catégorie de la"
                    "consommation {}".format(index.data())
                )

    def delete(self):
        """ Delete product
        """
        # reverse is required to delete items from list without
        # breaking it
        for index in reversed(self.product_list.selectedIndexes()):
            if api.products.remove(index.data()):
                item = self.product_list.takeItem(index.row())
                del item
            else:
                gui.utils.error(
                    "Impossible de suppimer la consomation {}".format(
                        index.data()
                    )
                )

