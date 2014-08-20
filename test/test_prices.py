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
import api.prices
import api.products
import api.categories

from database import Cursor


class PricesTest(unittest.TestCase):
    @classmethod
    def count_descriptors(cls):
        with Cursor() as cursor:
            cursor.exec("SELECT COUNT(*) FROM price_description")
            if cursor.next():
                return cursor.record().value(0)

    @classmethod
    def count_prices(cls):
        with Cursor() as cursor:
            cursor.exec("SELECT COUNT(*) FROM prices")
            if cursor.next():
                return cursor.record().value(0)

    def setUp(self):
        with Cursor() as cursor:
            # Erf can't truncate this so just partially clean up
            cursor.exec("DELETE FROM products")
            cursor.exec("DELETE FROM categories")
            cursor.exec("DELETE FROM prices")
            cursor.exec("DELETE FROM price_description")
        self.cat_eat = api.categories.add("Manger")
        self.cat_drink = api.categories.add("Boire")
        self.cat_soft = api.categories.add("Soft")

    def test_add_descriptor(self):
        """ Testing adding price descriptor """
        self.assertIsNotNone(api.prices.add_descriptor("Unité", self.cat_drink))
        self.assertIsNotNone(api.prices.add_descriptor("Demi", self.cat_drink))
        self.assertIsNotNone(api.prices.add_descriptor("Unité", self.cat_eat))
        self.assertIsNone(api.prices.add_descriptor("Unité", self.cat_eat))
        self.assertEqual(self.count_descriptors(), 3)

    def test_add_descriptor_extended(self):
        """ Testing extended features of add_descriptor """
        pid0 = api.products.add("Lapin", category_id=self.cat_eat)
        pid1 = api.products.add("Lapinne", category_id=self.cat_drink)
        self.assertTrue(api.prices.add_descriptor("Unité", self.cat_eat))
        prices = list(api.prices.get(product=pid0))
        self.assertEqual(len(prices), 1)
        prices = list(api.prices.get(product=pid1))
        self.assertEqual(len(prices), 0)

    def test_remove_description(self):
        """ Testing removing descriptor """
        id_ = api.prices.add_descriptor("Unité", self.cat_drink)
        self.assertEqual(self.count_descriptors(), 1)
        self.assertTrue(api.prices.remove_descriptor(id_))
        self.assertEqual(self.count_descriptors(), 0)

    def test_remove_description_extended(self):
        """ Testing advanced feature of description removing """
        did1 = api.prices.add_descriptor("Unité", self.cat_eat)
        pid10 = api.prices.add(None, did1, 0.0)
        pid11 = api.prices.add(None, did1, 0.0)

        did2 = api.prices.add_descriptor("Unité", self.cat_drink)
        pid20 = api.prices.add(None, did2, 0.0)
        pid21 = api.prices.add(None, did2, 0.0)

        self.assertEqual(self.count_prices(), 4)
        self.assertTrue(api.prices.remove_descriptor(did1))
        self.assertEqual(self.count_prices(), 2)

    def test_rename_description(self):
        """ Testing renaming price descriptor """
        id_ = api.prices.add_descriptor("Unité", self.cat_drink)
        self.assertTrue(api.prices.rename_descriptor(id_, "Demi"))
        price_descs = list(api.prices.get_descriptor(label="Demi"))
        self.assertEqual(len(price_descs), 1)
        self.assertEqual(id_, price_descs[0]['id'])

    def test_get(self):
        """ Testing price get function """
        self.assertEqual(list(api.prices.get()), [])
        price_desc_id = api.prices.add_descriptor("Unité", self.cat_drink)
        price_id = api.prices.add(None, price_desc_id, 3.14)
        self.assertEqual(list(api.prices.get()), [{
            'id': price_id,
            'label': "Unité",
            'value': 3.14,
            'product': 0,
            'category': self.cat_drink
        }])
        api.prices.add(None, price_desc_id, 0.00)
        self.assertTrue(self.count_prices(), 2)


