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
PanelManagment Window
=====================


"""


from PyQt5 import QtWidgets, QtCore, QtGui, uic

import api.panels
import api.validator
import gui.utils
from .consumptionmanagment import ConsumptionList


class PanelManagment(QtWidgets.QDialog):
    # pylint: disable=too-many-instance-attributes
    """ AddNote window class """
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/paneladmin.ui', self)
        self.panel_list = []

        self.create_panel_list()
        self.show()

    def create_panel_list(self):
        self.panel_list = []
        for panel in api.panels.get():
            self.panel_list.append(QtWidgets.QListWidgetItem(
                panel["name"], self.panels))

    def accept(self):
        if self.name_input.text():
            if not api.panels.add(self.name_input.text()):
                gui.utils.error("Erreur", "Impossible d'ajouter le panel")
            else:
                self.panel_list.append(QtWidgets.QListWidgetItem(
                    self.name_input.text(), self.panels))
            self.name_input.setText("")

    def delete(self):
        """ Callback to remove panel
        """
        for index in reversed(self.panels.selectedIndexes()):
            if api.panels.remove(index.data()):
                item = self.panels.takeItem(index.row())
                del item
            else:
                gui.utils.error(
                    "Impossible de suppimer le panel {}".format(
                        index.data()
                    )
                )

    def on_selection(self):
        selected = self.panels.selectedIndexes()
        if len(selected) != 1:
            self.product_list.setEnabled(False)
            self.panel_content.setEnabled(False)
        else:
            self.rebuild(selected[0].data())
            self.product_list.setEnabled(True)
            self.panel_content.setEnabled(True)

    def add_product(self):
        if not self.panels.currentItem():
            return
        panel = api.panels.get_unique(name=self.panels.currentItem().text())
        if not panel:
            return

        products_added = []
        for index in self.product_list.selectedIndexes():
            if index.parent().isValid():
                cat_name = index.parent().data()
                category = api.categories.get_unique(name=cat_name)
                if not category:
                    continue
                product = api.products.get_unique(
                    category=category['id'],
                    name=index.data()
                )
                if not product:
                    # Error
                    continue
                products_added.append(product['id'])
            else:
                cat_name = index.data()
                category = api.categories.get_unique(name=cat_name)
                if not category:
                    continue
                for product in api.products.get(category=category['id']):
                    products_added.append(product['id'])

        # Add all products at once
        if category and products_added:
            api.panels.add_products(panel['id'], products_added)

        self.rebuild(panel['name'])

    def delete_product(self):
        if not self.panels.currentItem():
            return
        panel = api.panels.get_unique(name=self.panels.currentItem().text())
        if not panel:
            return

        products_deleted = []
        category = None
        for index in self.panel_content.selectedIndexes():
            if index.parent().isValid():
                cat_name = index.parent().data()
                category = api.categories.get_unique(name=cat_name)
                if not category:
                    continue
                product = api.products.get_unique(
                    category=category['id'],
                    name=index.data()
                )
                if not product:
                    # Error
                    continue
                products_deleted.append(product['id'])
            else:
                cat_name = index.data()
                category = api.categories.get_unique(name=cat_name)
                if not category:
                    continue
                for product in api.products.get(category=category['id']):
                    products_deleted.append(product['id'])

        # Add all products at once
        if category and products_deleted:
            api.panels.delete_products(panel['id'], products_deleted)

        self.rebuild(panel['name'])

    def rebuild(self, panel_name):
        panel = api.panels.get_unique(name=panel_name)
        self.panel_content.rebuild(panel['id'])
        self.product_list.rebuild(panel['id'], self.panel_content)
        pass


class PanelList(ConsumptionList):
    def __init__(self, parent):
        super().__init__(parent)

    def add_product(self, pname, cname):
        """ Add product

        :param str pname: Product name
        :param str cname: Category name
        """
        cat_widget = None
        for widget in self.categories:
            if widget.text(0) == cname:
                cat_widget = widget
        if not cat_widget:
            cat_widget = QtWidgets.QTreeWidgetItem(self, [cname])
            self.categories.append(cat_widget)

        if cname not in [widget.text(0) for widget in self.products]:
            pro_widget = QtWidgets.QTreeWidgetItem(cat_widget, [pname])
            self.products.append(pro_widget)


class GlobalConsumptionList(PanelList):
    def __init__(self, parent):
        super().__init__(parent)

    def rebuild(self, paid, panel_content):
        """ Rebuild list

        :param int paid: Panel id
        :param PanelConsumptionList panel_content: Panel content list
        """
        self.clean()
        self.build(paid, panel_content)

    def build(self, paid, panel_content):
        self.categories = []
        self.products = []
        names = {}
        for cat in panel_content.categories:
            products = []
            for product in panel_content.products:
                products.append(product.text(0))
            names[cat.text(0)] = products

        for cat in api.categories.get_all():
            if cat['name'] in names:
                for product in api.products.get(category=cat['id']):
                    if not product['name'] in names[cat['name']]:
                        self.add_product(product['name'], cat['name'])
            else:
                self.add_category(cat['name'], cat['id'])


class PanelConsumptionList(PanelList):
    def __init__(self, parent):
        super().__init__(parent)

    def build(self, paid):
        """ Build list

        :param int paid: Panel id
        """
        self.categories = []
        self.products = []
        for product in api.panels.get_content(panel_id=paid):
            self.add_product(
                product['product_name'],
                product['category_name']
            )

    def rebuild(self, paid):
        """ Rebuilt list

        :param int paid: Panel id
        """
        self.clean()
        self.build(paid)

