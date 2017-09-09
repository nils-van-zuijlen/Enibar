# Copyright (C) 2014-2017 Bastien Orivel <b2orivel@enib.fr>
# Copyright (C) 2014-2017 Arnaud Levaufre <a2levauf@enib.fr>
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

import basetest
import gui.products_management_window
import api.categories
import api.products
import api.prices
from PyQt5 import QtWidgets, QtCore


class CategoryManagementTest(basetest.BaseGuiTest):
    def setUp(self):
        super().setUp()
        api.categories.add('test')
        self.win = gui.products_management_window.ProductsManagementWindow()
        self.win.tabs.setCurrentWidget(self.win.tab_manage_categories)

    def test_adding_category(self):
        """ Testing adding a category
        """
        self.assertFalse(self.win.button_cat_add.isEnabled())
        self.win.input_cat.setText("coucou")
        self.assertTrue(self.win.button_cat_add.isEnabled())
        self.win.button_cat_add.click()
        self.assertFalse(self.win.button_cat_add.isEnabled())
        self.assertEqual(self.win.input_cat.text(), "")
        self.assertEqual(self.get_items(self.win.categories), ['test', 'coucou'])
        self.assertEqual(list(api.categories.get()),
            [{'alcoholic': 0, 'color': '#FFFFFF', 'id': 1, 'name': 'test'},
             {'alcoholic': 0, 'color': '#FFFFFF', 'id': 2, 'name': 'coucou'}]
        )

    def test_add_existing_category(self):
        """ Testing adding an already existant category
        """
        def callback():
            win = self.app.activeWindow()
            self.assertIsInstance(win, QtWidgets.QMessageBox)
            self.assertIn("unique", win.informativeText())
            self.assertEqual(list(api.categories.get()),
                [{'alcoholic': 0, 'color': '#FFFFFF', 'id': 1, 'name': 'test'}])
            win.accept()
        self.win.input_cat.setText("test")
        QtCore.QTimer.singleShot(200, callback)
        self.win.button_cat_add.click()

    def test_remove_category(self):
        """ Testing removing a category
        """
        self.win.categories.setCurrentRow(0)
        self.win.button_cat_del.click()
        self.assertEqual(self.get_items(self.win.categories), [])
        self.assertEqual(list(api.categories.get()), [])

    def test_add_price_descriptor(self):
        """ Testing adding price descriptor
        """
        self.win.categories.setCurrentRow(0)
        self.win.button_cat_price.click()
        self.win.category_prices.widgets[0].input.setText("price1")
        self.win.category_prices.widgets[0].quantity_input.setValue(100)
        self.win.button_cat_save.click()
        self.assertEqual(list(api.prices.get_descriptor(category=1)), [{'category': 1, 'label': 'price1', 'id': 1, 'quantity': 100}])


class TestProductsManagement(basetest.BaseGuiTest):
    def setUp(self):
        super().setUp()
        api.categories.add('test')
        self.win = gui.products_management_window.ProductsManagementWindow()

    def test_add_product(self):
        """ Testing addding a product
        """
        test_cat = self.win.products.findItems("test", QtCore.Qt.MatchExactly)[0]
        self.win.products.setCurrentItem(test_cat)
        self.win.input_product.setText("test")
        self.win.button_product_add.click()
        self.assertEqual(list(api.products.get()), [{'category': 1, 'id': 1, 'name': 'test', 'percentage': 0.0}])
        self.assertEqual(self.get_tree(self.win.products, getter=lambda x, i: x.data(0, 1) or x.data(0, 0)), [{('test',): [{('test',): []}]}])
        self.win.products.setCurrentItem(test_cat.child(0))
        self.win.input_product.setText("test2")
        self.win.button_product_add.click()
        self.assertEqual(list(api.products.get()), [{'category': 1, 'id': 1, 'name': 'test', 'percentage': 0.0}, {'category': 1, 'id': 2, 'name': 'test2', 'percentage': 0.0}])
        self.assertEqual(self.get_tree(self.win.products, getter=lambda x, i: x.data(0, 1) or x.data(0, 0)), [{('test',): [{('test',): []}, {('test2',): []}]}])

    def test_add_product_no_cat(self):
        """ Testing adding a product with no category selected
        """
        def callback():
            self.assertEqual(list(api.products.get()), [])
            self.assertEqual(self.get_tree(self.win.products), [{('test', ): []}])
            win = self.app.activeWindow()
            self.assertIn("catégorie", win.informativeText())
            win.accept()
        self.win.input_product.setText("test")
        QtCore.QTimer.singleShot(200, callback)
        self.win.button_product_add.click()

    def test_add_product_double(self):
        """ Testing adding a product in double
        """
        def callback():
            win = self.app.activeWindow()
            self.assertIsInstance(win, QtWidgets.QMessageBox)
            self.assertIn("Impossible", win.text())
            win.accept()
        test_cat = self.win.products.findItems("test", QtCore.Qt.MatchExactly)[0]
        self.win.products.setCurrentItem(test_cat)
        self.win.input_product.setText("test")
        self.win.button_product_add.click()
        self.win.input_product.setText("test")
        QtCore.QTimer.singleShot(200, callback)
        self.win.button_product_add.click()

    def test_remove_product(self):
        """ Testing removing a product
        """
        test_cat = self.win.products.findItems("test", QtCore.Qt.MatchExactly)[0]
        self.win.products.setCurrentItem(test_cat)
        self.win.input_product.setText("couou")
        self.win.button_product_add.click()
        test_pro = test_cat.child(0)
        self.win.products.setCurrentItem(test_pro)
        self.win.button_product_del.click()
        self.assertEqual(self.get_tree(self.win.products), [{('test', ): []}])

    def test_remove_product_cat_selected(self):
        """ Testing removing a product when a category is selected
        """
        test_cat = self.win.products.findItems("test", QtCore.Qt.MatchExactly)[0]
        self.win.products.setCurrentItem(test_cat)
        self.win.input_product.setText("couou")
        self.win.button_product_add.click()
        self.win.button_product_del.click()
        self.assertEqual(self.get_tree(self.win.products, getter=lambda x, i: x.data(0, 1) or x.data(0, 0)), [{('test',): [{('couou',): []}]}])


