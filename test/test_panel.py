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

import basetest
import unittest

import api.products as products
import api.categories as categories
import api.prices as prices
import api.panels as panels
from test_products import ProductsTest
from test_prices import PricesTest
from database import Cursor


class CategoriesTest(unittest.TestCase):
    def setUp(self):
        with Cursor() as cursor:
            # Erf can't truncate this so just partially clean up
            cursor.exec("DELETE FROM panels")
            cursor.exec("DELETE FROM panel_content")

    @classmethod
    def count_panels(cls):
        """ Returns the number of panels currently in database """
        with Cursor() as cursor:
            cursor.exec("SELECT COUNT(*) FROM panels")
            if cursor.next():
                return cursor.record().value(0)

    def test_add_panel(self):
        """ Testing add_panel
        """
        panels.add("Test")
        self.assertEqual(self.count_panels(), 1)
        panels.add("Coucou")
        self.assertEqual(self.count_panels(), 2)
        panels.add("Coucou")
        self.assertEqual(self.count_panels(), 2)

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
        panels.add("Lolilonche")
        panels.add("Lolilonche2")
        self.assertEqual(1, len(list(panels.get(name="Lolilonche"))))

