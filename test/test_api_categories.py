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
import api.prices as prices


class CategoriesTest(basetest.BaseTest):
    def setUp(self):
        self._reset_db()

    def test_add_category(self):
        """ Testing add_category
        """
        categories.add("Test")
        self.assertEqual(self.count_categories(), 1)
        categories.add("Coucou")
        self.assertEqual(self.count_categories(), 2)
        categories.add("Coucou")
        self.assertEqual(self.count_categories(), 2)
        categories.add("")
        self.assertEqual(self.count_categories(), 2)

    def test_remove_category(self):
        """ Testing remove_category
        """
        id1 = categories.add("Test1")
        id2 = categories.add("Test2")

        prices.add_descriptor("A", id1, 100)
        prices.add_descriptor("B", id1, 100)
        prices.add_descriptor("C", id2, 100)
        prices.add_descriptor("D", id2, 100)

        products.add("Coucou", category_id=id1)
        products.add("Coucou2", category_id=id1)
        products.add("Coucou3", category_id=id2)

        self.assertEqual(2, self.count_categories())
        self.assertEqual(6, self.count_prices())
        self.assertEqual(4, self.count_descriptors())
        self.assertEqual(3, self.count_products())

        self.assertTrue(categories.remove("Test1"))

        self.assertEqual(1, self.count_categories())
        self.assertEqual(2, self.count_prices())
        self.assertEqual(1, self.count_products())
        self.assertEqual(2, self.count_descriptors())

    def test_get(self):
        """ Testing get_category
        """
        categories.add("Test0")
        categories.add("Test1")
        categories.add("Test2")
        self.assertEqual(len(list(categories.get())), 3)
        for i, category in enumerate(categories.get()):
            self.assertEqual("Test{}".format(i), category['name'])
        categories.add("Lolilonche")
        categories.add("Lolilonche2")
        self.assertEqual(1, len(list(categories.get(name="Lolilonche"))))

    def test_set_color(self):
        """ Testing set_color
        """
        categories.add("Test")
        categories.set_color("Test", "555555")
        self.assertEqual("555555", list(categories.get(name='Test'))[0]['color'])
        categories.set_color("Test", "555556")
        self.assertEqual("555556", list(categories.get(name='Test'))[0]['color'])

    def test_rename(self):
        """ Testing rename
        """
        categories.add("Test")
        self.assertEqual("Test", list(categories.get(name='Test'))[0]['name'])
        categories.rename("Test", "Coucou")
        self.assertEqual("Coucou", list(categories.get(name='Coucou'))[0]['name'])
        self.assertEqual(1, self.count_categories())
        self.assertFalse(categories.rename("Coucou", " "))
        self.assertEqual("Coucou", list(categories.get(name='Coucou'))[0]['name'])

    def test_set_alcoholic(self):
        """ Testing set_alcoholic
        """
        categories.set_alcoholic(categories.add("Test"), True)
        categories.set_alcoholic(categories.add("Test2"), False)
        categories.add("Test3")

        for result in categories.get():
            if result["name"] == "Test":
                self.assertTrue(result['alcoholic'])
            elif result["name"] == "Test2":
                self.assertFalse(result['alcoholic'])
            else:
                self.assertFalse(result['alcoholic'])

