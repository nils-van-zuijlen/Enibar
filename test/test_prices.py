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
        pid11 = api.products.add("Lapin", category_id=self.cat_eat)
        pid12 = api.products.add("Lapine", category_id=self.cat_eat)

        did2 = api.prices.add_descriptor("Unité", self.cat_drink)
        pid21 = api.products.add("Lapon", category_id=self.cat_drink)
        pid22 = api.products.add("Lapone", category_id=self.cat_drink)

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

    def test_add(self):
        """ Testing adding prices """
        desc_id = api.prices.add_descriptor("Unité", self.cat_eat)
        pid = api.products.add("Lapin", category_id=self.cat_eat)
        test = api.products.add("Lapin", category_id=self.cat_eat)
        self.assertIsNone(test)
        self.assertIsNone(api.prices.add(None, None, 0))
        self.assertIsNotNone(api.prices.add(pid, desc_id, 0))
        # We should have two prices as product insertion creates one
        self.assertEqual(self.count_prices(), 2)

    def test_get(self):
        """ Testing get price function """
        self.assertEqual(list(api.prices.get()), [])
        price_desc_id = api.prices.add_descriptor("Unité", self.cat_drink)
        pid = api.products.add("Lapin", category_id=self.cat_drink)

        price_id = None
        with Cursor() as cursor:
            cursor.prepare("SELECT id FROM prices WHERE product=?")
            cursor.addBindValue(pid)
            self.assertTrue(cursor.exec_())
            if cursor.next():
                price_id = cursor.record().value('id')
        self.assertIsNotNone(price_id)

        self.assertEqual(list(api.prices.get()), [{
            'id': price_id,
            'label': "Unité",
            'value': 0,
            'product': pid,
            'category': self.cat_drink
        }])
        api.prices.add(None, price_desc_id, 0)
        self.assertTrue(self.count_prices(), 2)
        self.assertEqual(list(api.prices.get(id=price_id)), [{
            'id': price_id,
            'label': "Unité",
            'value': 0,
            'product': pid,
            'category': self.cat_drink
        }])

    def test_get_unique(self):
        """ Testing get unique """
        pid = api.products.add("Lapin", category_id=self.cat_eat)
        desc_id1 = api.prices.add_descriptor("Unité", self.cat_eat)
        desc_id2 = api.prices.add_descriptor("Kilo", self.cat_eat)
        id1 = api.prices.add(pid, desc_id1, 0)
        id2 = api.prices.add(pid, desc_id2, 0)
        self.assertIsNone(api.prices.get_unique(value=0))
        self.assertEqual(api.prices.get_unique(id=id1), {
            'id': id1,
            'label': "Unité",
            'value': 0,
            'product': pid,
            'category': self.cat_eat
        })

    def test_set_value(self):
        """ Testing setting price value """
        desc_id = api.prices.add_descriptor("Unité", self.cat_eat)
        product = api.products.add("Lapin", category_id=self.cat_eat)
        pid = api.prices.add(product, desc_id, 0)
        self.assertTrue(api.prices.set_value(pid, 12.34))
        self.assertEqual(api.prices.get_unique(id=pid)['value'], 12.34)

    def test_set_multiple_value(self):
        """ Testing setting multiple values """
        desc_id = api.prices.add_descriptor("Unité", self.cat_eat)
        product = api.products.add("Lapin", category_id=self.cat_eat)
        prices = []
        for i in range(10):
            id_ = api.prices.add(product, desc_id, 0)
            prices.append({'id': id_, 'value': i})
        self.assertTrue(api.prices.set_multiple_values(prices))
        for price in api.prices.get():
            id_, value = price['id'], price['value']
            for price in prices:
                if price['id'] == id_:
                    self.assertEqual(value, price['value'])
        # The extra length of api.prices.get is due to product creation
        self.assertEqual(len(prices), len(list(api.prices.get())) - 1)



