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
from database import Cursor


class UtilsTest(unittest.TestCase):
    def setUp(self):
        with Cursor() as cursor:
            cursor.exec("TRUNCATE TABLE products")

    def count_products(self):
        """ Returns the number of products currently in database """
        with Cursor() as cursor:
            cursor.exec("SELECT COUNT(*) FROM products")
            if cursor.next():
                return cursor.record().value(0)

    def test_add(self):
        """ Testing adding products """

        self.assertEqual(products.add("test", "manger"), 1)
        self.assertEqual(products.add("test2", "soft"), 2)
        self.assertEqual(products.add("test3", "alcool"), 3)
        self.assertEqual(products.add("test4", "nope"), -1)
        self.assertEqual(self.count_products(), 3)

    def test_remove(self):
        """ Testing removing products """
        id_ = products.add("test", "manger")

        self.assertTrue(products.remove(id_))
        self.assertEqual(self.count_products(), 0)

    def test_prices(self):
        """ Testing setting prices and get_by_id """
        id_ = products.add("test", "manger")

        self.assertTrue(products.set_prices(id_, 1.25, 2.50))
        self.assertEqual(products.get_by_id(id_), {'category': 'manger',
                                                   'name': 'test',
                                                   'price_demi': 2.5,
                                                   'price_unit': 1.25,
                                                   'price_meter': 0.0,
                                                   'price_pint': 0.0})
        self.assertTrue(products.set_prices(id_, 1.25, 2.50, 3.50, 4.50))
        self.assertEqual(products.get_by_id(id_), {'category': 'manger',
                                                   'name': 'test',
                                                   'price_demi': 2.50,
                                                   'price_unit': 1.25,
                                                   'price_meter': 4.50,
                                                   'price_pint': 3.50})

    def test_get_by_category(self):
        """ Testing get_by_category """
        products.add("test0", "manger")
        products.add("test1", "manger")
        products.add("test2", "manger")
        products.add("test3", "soft")
        products.add("test4", "alcool")

        self.assertEqual(list(products.get_by_category("manger")),
                         [{'category': 'manger',
                           'name': 'test' + str(i),
                           'price_demi': 0.0,
                           'price_unit': 0.0,
                           'price_meter': 0.0,
                           'price_pint': 0.0} for i in range(3)])

    def test_get_by_name(self):
        """ Testing get_by_name """
        products.add("coucou0", "manger")
        products.add("test1", "manger")
        products.add("coucou1", "manger")
        products.add("test2", "manger")
        products.add("coucou2", "manger")

        self.assertEqual(list(products.get_by_name("coucou")),
                         [{'category': 'manger',
                           'name': 'coucou' + str(i),
                           'price_demi': 0.0,
                           'price_unit': 0.0,
                           'price_meter': 0.0,
                           'price_pint': 0.0} for i in range(3)])

