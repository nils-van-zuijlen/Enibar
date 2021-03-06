# copyright (c) 2014-2018 bastien orivel <b2orivel@enib.fr>
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

import basetest

import api.products as products
import api.categories as categories


class ProductsTest(basetest.BaseTest):
    def setUp(self):
        super().setUp()
        self.cat_eat = categories.add("Manger")
        self.cat_drink = categories.add("Boire")
        self.cat_soft = categories.add("Soft")

    def test_add_with_cat_name(self):
        """ Testing adding products with category name """
        self.assertIsNone(products.add("Banane"))
        self.assertIsNotNone(products.add("Banane", category_name="Manger"))
        self.assertIsNotNone(products.add("Biere", category_name="Boire"))
        self.assertIsNone(products.add("Cidre", category_name="Terroir"))
        self.assertEqual(self.count_products(), 2)

    def test_add_with_cat_id(self):
        """ Testing adding products with category id """
        self.assertIsNotNone(products.add("Banane", category_id=self.cat_eat))
        self.assertIsNotNone(products.add("Biere", category_id=self.cat_drink))
        self.assertIsNone(products.add("Cidre", category_id=2685240))
        self.assertEqual(self.count_products(), 2)

    def test_percentage(self):
        pid = products.add("Banane", category_id=self.cat_eat, percentage=2.5)
        self.assertEqual(list(products.get()), [{"id": pid, "category": self.cat_eat, "name": "Banane", "percentage": 2.5}])
        self.assertTrue(products.set_percentage(pid, "5"))
        self.assertEqual(list(products.get()), [{"id": pid, "category": self.cat_eat, "name": "Banane", "percentage": 5.0}])

    def test_remove(self):
        """ Testing removing products """
        id_ = products.add("test", category_name="Manger")
        self.assertTrue(products.remove(id_))
        self.assertEqual(self.count_products(), 0)

    def test_get(self):
        """ Testing get
        """
        id1 = products.add("Banane", category_id=self.cat_eat)
        id2 = products.add("Banana split", category_id=self.cat_eat)
        self.assertEqual(list(products.get()),
            [{'id': id1, 'category': self.cat_eat, 'name': "Banane", "percentage": 0.0},
             {'id': id2, 'category': self.cat_eat, 'name': "Banana split", "percentage": 0.0}]
        )

    def test_rename(self):
        """ Testing renaming a product
        """
        id1 = products.add("Banane", category_id=self.cat_eat)
        products.rename(id1, "Lapin")
        self.assertEqual(list(products.get()),
            [{'id': id1, 'category': self.cat_eat, 'name': "Lapin", "percentage": 0.0}]
        )
        self.assertFalse(products.rename(id1, " "))
        self.assertEqual(list(products.get()),
            [{'id': id1, 'category': self.cat_eat, 'name': "Lapin", "percentage": 0.0}]
        )
