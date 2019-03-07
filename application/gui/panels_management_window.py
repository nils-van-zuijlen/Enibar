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
PanelManagment Window
=====================


"""


from PyQt5 import QtWidgets, uic, QtCore

import api.panels
import api.validator
import gui.utils
from .products_management_window import ConsumptionList


class PanelsManagementWindow(QtWidgets.QDialog):
    """ PanelsManagementWindow class """
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('ui/panels_management_window.ui', self)
        self.panel_list = []
        self.name_input.set_validator(api.validator.NAME)
        self.product_list.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.panel_content.sortByColumn(0, QtCore.Qt.AscendingOrder)

        self.create_panel_list()
        self.show()

    def create_panel_list(self):
        """ Create the list of panels on the left.
        """
        self.panel_list = []
        for panel in api.panels.get():
            self.panel_list.append(QtWidgets.QListWidgetItem(
                panel["name"], self.panels))

    def accept(self):
        """ Called when "Ajouter" is clicked
        """
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
            api.panels.remove(index.data())
            item = self.panels.takeItem(index.row())
            del item

    def on_selection(self):
        """ Called when a panel is selected
        """
        selected = self.panels.selectedIndexes()
        if len(selected) != 1:
            self.product_list.setEnabled(False)
            self.panel_content.setEnabled(False)
            self.move_left.setEnabled(False)
            self.move_right.setEnabled(False)
            self.hidden.setEnabled(False)
        else:
            panel = self.get_current_panel()
            if not panel:
                return
            if panel["hidden"]:
                self.hidden.setChecked(True)
            else:
                self.hidden.setChecked(False)
            self.hidden.setEnabled(True)
            self.rebuild(selected[0].data())
            self.product_list.setEnabled(True)
            self.panel_content.setEnabled(True)
            self.move_left.setEnabled(True)
            self.move_right.setEnabled(True)

    def get_current_panel(self):
        """ Return the current panel or None.
        """
        currentItem = self.panels.currentItem()
        if not currentItem:
            return
        return api.panels.get_unique(name=currentItem.text())

    def on_hide(self, state):
        """ Toggle the hidden parameter in database. Called when "Panel cache"
            is clicked
        """
        panel = self.get_current_panel()

        if state:
            api.panels.hide(panel["name"])
        else:
            api.panels.show(panel["name"])

    def add_product(self):
        """ Called when ">>>>>" is clicked
        """
        panel = self.get_current_panel()
        if not panel:
            return

        products_added = []
        category = None
        for index in self.product_list.selectedIndexes():
            if index.parent().isValid():
                cat_name = index.parent().data()
                category = api.categories.get_unique(name=cat_name)
                product = api.products.get_unique(
                    category=category['id'],
                    name=index.data()
                )
                products_added.append(product['id'])
            else:
                cat_name = index.data()
                category = api.categories.get_unique(name=cat_name)
                for product in api.products.get(category=category['id']):
                    products_added.append(product['id'])

        # Add all products at once
        if category and products_added:
            api.panels.add_products(panel['id'], products_added)

        self.rebuild(panel['name'])

    def delete_product(self):
        """ Called when "<<<<<" is clicked
        """
        if not self.panels.currentItem():
            return
        panel = api.panels.get_unique(name=self.panels.currentItem().text())

        products_deleted = []
        category = None
        for index in self.panel_content.selectedIndexes():
            if index.parent().isValid():
                cat_name = index.parent().data()
                category = api.categories.get_unique(name=cat_name)
                product = api.products.get_unique(
                    category=category['id'],
                    name=index.data()
                )
                products_deleted.append(product['id'])
            else:
                cat_name = index.data()
                category = api.categories.get_unique(name=cat_name)
                for product in api.products.get(category=category['id']):
                    products_deleted.append(product['id'])

        # Add all products at once
        if category and products_deleted:
            api.panels.delete_products(panel['id'], products_deleted)

        self.rebuild(panel['name'])

    def rebuild(self, panel_name):
        """ Rebuild the two right lists
        """
        global_opened = []
        panel_opened = []

        for widget in self.panel_content.categories:
            if widget.isExpanded():
                panel_opened.append(widget.text(0))

        for widget in self.product_list.categories:
            if widget.isExpanded():
                global_opened.append(widget.text(0))

        panel = api.panels.get_unique(name=panel_name)
        self.panel_content.rebuild(panel['id'])
        self.product_list.rebuild_from_panel(self.panel_content)

        for widget in self.panel_content.categories:
            if widget.text(0) in panel_opened:
                widget.setExpanded(True)

        for widget in self.product_list.categories:
            if widget.text(0) in global_opened:
                widget.setExpanded(True)

    def on_change(self):
        """ Set the status of the name input
        """
        self.add_button.setEnabled(self.name_input.valid)

    def consumption_management_fnc(self):
        self.parent().consumption_management_fnc_no_auth()


class PanelList(ConsumptionList):
    """ Base class for the two panels
    """

    def __init__(self, parent):
        super().__init__(parent)

    def add_product(self, pname, cname, _):
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

        pro_widget = QtWidgets.QTreeWidgetItem(cat_widget, [pname])
        self.products.append(pro_widget)


class GlobalConsumptionList(PanelList):
    """ List containing all products NOT in the panel
    """
    def __init__(self, parent):
        super().__init__(parent)

    def rebuild_from_panel(self, panel_content):
        """ Rebuild list base on the content of the panel.

        :param PanelConsumptionList panel_content: Panel content list
        """
        self.clean()
        self.build_from_panel(panel_content)

    def build_from_panel(self, panel_content):
        """ Build the list
        """
        self.categories = []
        self.products = []
        names = {}
        for cat in panel_content.categories:
            products = []
            for product in panel_content.products:
                if product.parent() == cat:
                    products.append(product.text(0))
            names[cat.text(0)] = products

        for cat in api.categories.get():
            if cat['name'] in names:
                for product in api.products.get(category=cat['id']):
                    if not product['name'] in names[cat['name']]:
                        self.add_product(product['name'], cat['name'], product['percentage'])
            else:
                self.add_category(cat['name'], cat['id'])


class PanelConsumptionList(PanelList):
    """ List the content of the panel
    """
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
                product['category_name'],
                product['product_percentage']
            )

    def rebuild(self, paid):
        """ Rebuilt list

        :param int paid: Panel id
        """
        self.clean()
        self.build(paid)
