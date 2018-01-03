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

from PyQt5 import QtWidgets, QtCore
import basetest
from gui.panels_management_window import PanelsManagementWindow
from gui.products_management_window import ProductsManagementWindow
from gui.main_window import MenuBar, MainWindow
import api.panels as panels
import api.categories as categories
import api.products as products
import api.prices as prices
import settings
import mock


class TestPanelsManagementWindow(basetest.BaseGuiTest):
    def setUp(self):
        super().setUp()
        panels.add("a")
        panels.add("b")
        panels.hide("b")
        panels.add("c")

        categories.add("cat1")
        categories.add("cat2")
        products.add("prod1_cat1", category_name="cat1")
        products.add("prod2_cat1", category_name="cat1")
        products.add("prod1_cat2", category_name="cat2")
        products.add("prod2_cat2", category_name="cat2")

        self.default_products_tree = [{('cat1',): [{('prod1_cat1',): []}, {('prod2_cat1',): []}]}, {('cat2',): [{('prod1_cat2',): []}, {('prod2_cat2',): []}]}]
        self.main = MainWindow()
        self.menu = MenuBar(self.main)
        self.win = PanelsManagementWindow(self.menu)

    def test_adding_panel(self):
        self.assertFalse(self.win.add_button.isEnabled())
        self.win.name_input.setText("d")
        self.assertTrue(self.win.add_button.isEnabled())
        self.win.add_button.click()
        self.assertEqual(self.get_items(self.win.panels), ["a", "b", "c", "d"])

    def test_adding_already_existing_panel(self):
        self.win.name_input.setText("a")

        def verif():
            win = self.app.activeWindow()
            self.assertIsInstance(win, QtWidgets.QMessageBox)
            self.assertIn("Impossible", win.informativeText())
            win.accept()

        QtCore.QTimer.singleShot(200, verif)
        self.win.add_button.click()

    def test_deleting_panel(self):
        self.win.panels.item(0).setSelected(True)
        self.win.panels.item(1).setSelected(True)
        self.win.delete_button.click()
        self.assertEqual(self.get_items(self.win.panels), ["c"])
        self.win.panels.item(0).setSelected(True)
        self.win.delete_button.click()
        self.assertEqual(self.get_items(self.win.panels), [])

    def test_showing_hiding_panel(self):
        self.win.panels.setCurrentRow(0)
        self.win.hidden.toggle()
        panel = panels.get_unique(name="a")
        self.assertTrue(panel['hidden'])
        self.win.hidden.toggle()
        panel = panels.get_unique(name="a")
        self.assertFalse(panel['hidden'])

    def test_adding__removing_products_to_panel(self):
        self.win.panels.setCurrentRow(0)
        self.assertEqual(self.get_tree(self.win.product_list), self.default_products_tree)
        self.assertEqual(self.get_tree(self.win.panel_content), [])

        tree = self.win.product_list
        # Select the second category
        tree.topLevelItem(tree.topLevelItemCount() - 1).setSelected(True)
        self.win.move_right.click()
        self.assertEqual(self.get_tree(self.win.product_list), [{('cat1',): [{('prod1_cat1',): []}, {('prod2_cat1',): []}]}])
        self.assertEqual(self.get_tree(self.win.panel_content), [{('cat2',): [{('prod1_cat2',): []}, {('prod2_cat2',): []}]}])

        # Select the first product of the first category
        cat = tree.topLevelItem(0)
        cat.setExpanded(True)
        prod1 = cat.child(0)
        prod1.setSelected(True)
        self.win.move_right.click()
        self.assertEqual(self.get_tree(self.win.product_list), [{('cat1',): [{('prod2_cat1',): []}]}])
        self.assertEqual(self.get_tree(self.win.panel_content), [{('cat1',): [{('prod1_cat1',): []}]}, {('cat2',): [{('prod1_cat2',): []}, {('prod2_cat2',): []}]}])

        self.win.panels.setCurrentRow(1)
        self.assertEqual(self.get_tree(self.win.product_list), self.default_products_tree)
        self.assertEqual(self.get_tree(self.win.panel_content), [])

        self.win.panels.setCurrentRow(0)
        tree = self.win.panel_content

        # Select the second category
        tree.topLevelItem(tree.topLevelItemCount() - 1).setSelected(True)
        self.win.move_left.click()
        self.assertEqual(self.get_tree(self.win.panel_content), [{('cat1',): [{('prod1_cat1',): []}]}])
        self.assertEqual(self.get_tree(self.win.product_list), [{('cat1',): [{('prod2_cat1',): []}]}, {('cat2',): [{('prod1_cat2',): []}, {('prod2_cat2',): []}]}])

        # Select the first product of the first category
        cat = tree.topLevelItem(0)
        cat.setExpanded(True)
        prod1 = cat.child(0)
        prod1.setSelected(True)
        self.win.move_left.click()
        self.assertEqual(self.get_tree(self.win.panel_content), [])
        self.assertEqual(self.get_tree(self.win.product_list), self.default_products_tree)

    def test_panel_hidden_on_selection(self):
        self.assertFalse(self.win.hidden.isChecked())
        self.win.panels.setCurrentRow(1)
        self.assertTrue(self.win.hidden.isChecked())

    def test_click_on_buttons_when_no_panel_selected(self):
        self.win.move_right.click()
        self.win.move_left.click()
        self.win.delete_button.click()

    def test_expanded_items_stay_expanded(self):
        self.win.panels.setCurrentRow(0)
        self.win.product_list.topLevelItem(0).setSelected(True)
        self.win.move_right.click()
        self.win.panels.setCurrentRow(1)
        self.win.product_list.topLevelItem(0).setSelected(True)
        self.win.move_right.click()

        self.win.product_list.topLevelItem(0).setExpanded(True)
        self.win.panel_content.topLevelItem(0).setExpanded(True)
        self.assertTrue(self.win.product_list.topLevelItem(0).isExpanded())
        self.assertTrue(self.win.panel_content.topLevelItem(0).isExpanded())

        self.win.panels.setCurrentRow(0)

        self.assertTrue(self.win.product_list.topLevelItem(0).isExpanded())
        self.assertTrue(self.win.panel_content.topLevelItem(0).isExpanded())

    def test_product_management_button(self):
        def verif():
            win = self.app.activeWindow()
            self.assertIsInstance(win, ProductsManagementWindow)
            win.close()

        QtCore.QTimer.singleShot(1000, verif)
        self.win.products_management_button.click()
