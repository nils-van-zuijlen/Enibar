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

import api.transactions as transactions
import api.notes as notes
from PyQt5 import QtCore
from database import Cursor


class TransactionsTest(basetest.BaseTest):
    def setUp(self):
        self._reset_db()
        notes.add("test1",
            "test1",
            "test1",
            "test@pouette.com",
            "0600000000",
            '12/12/2001',
            '1A',
            ''
        )

    @classmethod
    def count_transactions(cls):
        """ Returns the number of transactions currently in database """
        with Cursor() as cursor:
            cursor.exec("SELECT COUNT(*) FROM transactions")
            if cursor.next():
                return cursor.record().value(0)

    def test_log_transaction(self):
        """ Testing log_transaction
        """
        self.assertTrue(transactions.log_transaction(
            "test1",
            "a",
            "b",
            "c",
            "1",
            -1
        ))
        self.assertTrue(transactions.log_transaction(
            "test1",
            "b",
            "d",
            "c",
            "2",
            -5
        ))
        self.assertTrue(transactions.log_transaction(
            "test2",
            "e",
            "f",
            "g",
            "2",
            5
        ))
        self.assertEqual(self.count_transactions(), 3)
        self.assertDictListEqual(list(transactions.get()),
            [{'product': 'b',
              'lastname': 'test1',
              'quantity': 1,
              'firstname': 'test1',
              'id': 1,
              'note': 'test1',
              'price': -1.0,
              'category': 'a',
              'price_name': 'c'},
             {'product': 'd',
              'lastname': 'test1',
              'quantity': 2,
              'firstname': 'test1',
              'id': 2,
              'note': 'test1',
              'price': -5.0,
              'category': 'b',
              'price_name': 'c'},
             {'product': 'f',
              'lastname': '',
              'quantity': 2,
              'firstname': '',
              'id': 3,
              'note': 'test2',
              'price': 5.0,
              'category': 'e',
              'price_name': 'g'}
            ], ignore=["date"]
        )

    def test_log_transactions(self):
        """ Testing log_transactions
        """
        transactions.log_transactions([{'note': "test1",
                                        'category': "a",
                                        'product': "b",
                                        'price_name': "c",
                                        'quantity': 1,
                                        'price': -1},
                                       {'note': "test1",
                                        'category': "b",
                                        'product': "d",
                                        'price_name': "c",
                                        'quantity': 2,
                                        'price': -5},
                                       {'note': "test2",
                                        'category': "e",
                                        'product': "f",
                                        'price_name': "g",
                                        'quantity': 2,
                                        'price': 5}])
        transactions.TRANSACTS_FIELDS_CACHE = {}  # To test the cache making.
        self.assertDictListEqual(list(transactions.get()),
            [{'product': 'b',
              'lastname': 'test1',
              'quantity': 1,
              'firstname': 'test1',
              'id': 1,
              'note': 'test1',
              'price': -1.0,
              'category': 'a',
              'price_name': 'c'},
             {'product': 'd',
              'lastname': 'test1',
              'quantity': 2,
              'firstname': 'test1',
              'id': 2,
              'note': 'test1',
              'price': -5.0,
              'category': 'b',
              'price_name': 'c'},
             {'product': 'f',
              'lastname': '',
              'quantity': 2,
              'firstname': '',
              'id': 3,
              'note': 'test2',
              'price': 5.0,
              'category': 'e',
              'price_name': 'g'}
            ], ignore=["date"]
        )

    def test_rollback_transaction(self):
        """ Testing rollback_transaction
        """
        self.assertFalse(transactions.rollback_transaction(5))
        transactions.log_transaction(
            "test1",
            "a",
            "b",
            "c",
            "1",
            -1
        )
        transactions.log_transaction(
            "test1",
            "b",
            "d",
            "c",
            5,
            -5
        )
        transactions.log_transaction(
            "test2",
            "e",
            "f",
            "g",
            "2",
            5
        )
        transactions.log_transaction(
            "test2",
            "e",
            "f",
            "g",
            "a",
            5
        )
        transactions.log_transaction(
            "test1",
            "e",
            "f",
            "g",
            "a",
            5,
            False
        )

        self.assertEqual(self.count_transactions(), 5)
        self.assertTrue(transactions.rollback_transaction(1))
        self.assertEqual(self.count_transactions(), 4)
        self.assertTrue(transactions.rollback_transaction(2))
        self.assertDictListEqual(list(transactions.get(id=2)),
             [{'product': 'd',
              'lastname': 'test1',
              'quantity': 4,
              'firstname': 'test1',
              'id': 2,
              'note': 'test1',
              'price': -4.0,
              'category': 'b',
              'price_name': 'c'}
             ], ignore=['date']
        )
        self.assertEqual(self.count_transactions(), 4)
        self.assertTrue(transactions.rollback_transaction(2, full=True))
        self.assertEqual(self.count_transactions(), 3)
        self.assertFalse(transactions.rollback_transaction(3))
        self.assertEqual(self.count_transactions(), 3)
        self.assertFalse(transactions.rollback_transaction(4))
        self.assertEqual(self.count_transactions(), 3)
        self.assertFalse(transactions.rollback_transaction(5))

    def test_get_grouped_entries(self):
        """ Testing get_grouped_entries
        """
        transactions.log_transaction(
            "test1",
            "a",
            "b",
            "c",
            "1",
            -1
        )
        transactions.log_transaction(
            "test1",
            "b",
            "d",
            "c",
            5,
            -5
        )
        transactions.log_transaction(
            "test2",
            "e",
            "f",
            "g",
            "2",
            5
        )
        self.assertEqual(list(transactions.get_grouped_entries("note", {'lastname': ""})), ['test2'])
        self.assertEqual(list(transactions.get_grouped_entries("note", {})), ['test1', 'test2'])

    def test_get_reversed(self):
        """ Testing get_reversed
        """
        self.assertEqual(list(transactions.get_reversed()), [])
        self.assertTrue(transactions.log_transaction(
            "test1",
            "a",
            "b",
            "c",
            "1",
            -1
        ))
        self.assertTrue(transactions.log_transaction(
            "test1",
            "b",
            "d",
            "c",
            "2",
            -5
        ))
        self.assertEqual(self.count_transactions(), 2)
        self.assertDictListEqual(list(transactions.get_reversed()),
            [{'product': 'd',
              'lastname': 'test1',
              'quantity': 2,
              'firstname': 'test1',
              'id': 2,
              'note': 'test1',
              'price': -5.0,
              'category': 'b',
              'price_name': 'c'},
             {'product': 'b',
              'lastname': 'test1',
              'quantity': 1,
              'firstname': 'test1',
              'id': 1,
              'note': 'test1',
              'price': -1.0,
              'category': 'a',
              'price_name': 'c'},
            ], ignore=["date"]
        )

