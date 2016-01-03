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

import basetest

import api.products as products
import api.categories as categories
import api.panels as panels


class CategoriesTest(basetest.BaseTest):
    def setUp(self):
        self._reset_db()
        self.cat_eat = categories.add("Manger")
        self.cat_drink = categories.add("Boire")
        self.banana = products.add("Banane", category_name="Manger")
        self.bier = products.add("Biere", category_name="Boire")

    def test_add_panel(self):
        """ Testing add_panel
        """
        panels.add("Test")
        self.assertEqual(self.count_panels(), 1)
        panels.add("Coucou")
        self.assertEqual(self.count_panels(), 2)
        panels.add("Coucou")
        self.assertEqual(self.count_panels(), 2)

    def test_hide_show(self):
        """ Testing hiding/showing panels
        """
        panels.add("Coucou")
        self.assertFalse(panels.get_unique(name="Coucou")["hidden"])
        panels.hide("Coucou")
        self.assertTrue(panels.get_unique(name="Coucou")["hidden"])
        panels.show("Coucou")
        self.assertFalse(panels.get_unique(name="Coucou")["hidden"])

    def test_remove_panel(self):
        """ Testing remove_category
        """
        panels.add("Test1")
        panels.add("Test2")

        self.assertTrue(panels.remove("Test1"))
        self.assertEqual(1, self.count_panels())

    def test_get(self):
        """ Testing get_panels
        """
        panels.add("Test0")
        panels.add("Test1")
        panels.add("Test2")
        self.assertEqual(len(list(panels.get())), 3)
        for i, category in enumerate(panels.get()):
            self.assertEqual("Test{}".format(i), category['name'])
            self.assertFalse(category['hidden'])
        panels.add("Lolilonche")
        panels.add("Lolilonche2")
        self.assertEqual(1, len(list(panels.get(name="Lolilonche"))))

    def test_add_product(self):
        """ Testing add_product
        """
        pan = panels.add("Test")
        pan2 = panels.add("Test2")
        pro = products.add("coucou", category_name="Manger")
        self.assertTrue(panels.add_product(pan, pro))
        self.assertTrue(panels.add_product(pan2, pro))
        self.assertEqual(list(panels.get_content(panel_id=pan)), [{'category_id': self.cat_eat,
            'product_name': 'coucou', 'panel_id': pan, 'category_name': "Manger", 'product_id': pro}])

    def test_add_products(self):
        """ Testing add_products
        """
        pan = panels.add("Test")
        panels.add("Test2")
        pro = products.add("coucou", category_name="Manger")
        pro2 = products.add("coucou", category_name="Boire")
        panels.add_products(pan, [pro, pro2])
        self.assertEqual(list(panels.get_content(panel_id=pan)), [{'category_id': self.cat_eat,
            'product_name': 'coucou', 'panel_id': pan, 'category_name': "Manger", 'product_id': pro},
            {'category_id': self.cat_drink, 'product_name': 'coucou', 'panel_id': pan, 'category_name': "Boire", 'product_id': pro2}, ])

    def test_delete_product(self):
        """ Testing delete_product
        """
        pan = panels.add("Test")
        pro = products.add("coucou", category_name="Manger")
        panels.add_product(pan, pro)
        panels.delete_product(pan, pro)
        self.assertEqual(list(panels.get_content(panel_id=pan)), [])

    def test_delete_products(self):
        """ Testing delete_products
        """
        pan = panels.add("Test")
        pro = products.add("coucou", category_name="Manger")
        pro2 = products.add("coucou", category_name="Boire")
        panels.add_products(pan, [pro, pro2])
        panels.delete_products(pan, [pro, pro2])
        self.assertEqual(list(panels.get_content(panel_id=pan)), [])

