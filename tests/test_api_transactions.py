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

import api.transactions as transactions
import api.notes as notes


class TransactionsTest(basetest.BaseTest):
    def setUp(self):
        notes.api.redis.send_message = lambda x, y: [notes.rebuild_note_cache(note) for note in y]
        super().setUp()
        notes.add("test1",
            "test1",
            "test1",
            "test@pouette.com",
            "0600000000",
            '12/12/2001',
            '1A',
            '',
            True,
            True
        )
        notes.add("test2",
            "test2",
            "test2",
            "test2@pouette.com",
            "0600000002",
            '12/12/2002',
            '2A',
            '',
            True,
            True
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
              'lastname': 'test2',
              'quantity': 2,
              'firstname': 'test2',
              'id': 3,
              'note': 'test2',
              'price': 5.0,
              'category': 'e',
              'price_name': 'g'}
            ], ignore=["date", "percentage", "liquid_quantity"]
        )

    def test_rollback_transaction(self):
        """ Testing rollback_transaction
        """
        self.assertFalse(transactions.rollback_transaction(5))
        self.assertTrue(transactions.log_transactions([{
            'note': "test1",
            'category': "a",
            'product': "b",
            'price_name': "c",
            'quantity': 1,
            'price': -1
        }]))
        self.assertTrue(transactions.log_transactions([{
            'note': "test1",
            'category': "b",
            'product': "d",
            'price_name': "c",
            'quantity': 5,
            'price': -5
        }]))
        self.assertTrue(transactions.log_transactions([{
            'note': "test2",
            'category': "e",
            'product': "f",
            'price_name': "g",
            'quantity': 2,
            'price': 5
        }]))
        self.assertTrue(transactions.log_transactions([{
            'note': "test2",
            'category': "e",
            'product': "f",
            'price_name': "g",
            'quantity': 1,
            'price': 5
        }]))
        self.assertTrue(transactions.log_transactions([{
            'note': "test1",
            'category': "e",
            'product': "f",
            'price_name': "g",
            'quantity': 1,
            'price': 5,
            'deletable': False
            }]
        ))

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
             ], ignore=["date", "percentage", "liquid_quantity"]
        )
        self.assertEqual(self.count_transactions(), 4)
        self.assertTrue(transactions.rollback_transaction(2, full=True))
        self.assertEqual(self.count_transactions(), 3)
        notes.remove(["test2"])
        notes.rebuild_cache()
        self.assertEqual(self.count_transactions(), 4)
        self.assertFalse(transactions.rollback_transaction(4))
        self.assertEqual(self.count_transactions(), 4)
        self.assertFalse(transactions.rollback_transaction(5))
        self.assertEqual(self.count_transactions(), 4)
        self.assertFalse(transactions.rollback_transaction(6))

    def test_get_grouped_entries(self):
        """ Testing get_grouped_entries
        """
        transactions.log_transactions([{
            'note': "test1",
            'category': "a",
            'product': "b",
            'price_name': "c",
            'quantity': 1,
            'price': -1
        }])
        transactions.log_transactions([{
            'note': "test1",
            'category': "b",
            'product': "d",
            'price_name': "c",
            'quantity': 5,
            'price': -5
        }])
        transactions.log_transactions([{
            'note': "test2",
            'category': "e",
            'product': "f",
            'price_name': "g",
            'quantity': 2,
            'price': 5
        }])
        self.assertEqual(list(transactions.get_grouped_entries("note", {'lastname': "test2"})), ['test2'])
        self.assertEqual(list(transactions.get_grouped_entries("note", {})), ['test1', 'test2'])

    def test_get_gt(self):
        """ Testing __gt """
        transactions.log_transactions([{
            'note': "test1",
            'category': "a",
            'product': "b",
            'price_name': "c",
            'quantity': 1,
            'price': -1
        }])
        transactions.log_transactions([{
            'note': "test1",
            'category': "b",
            'product': "d",
            'price_name': "c",
            'quantity': 5,
            'price': -5
        }])
        transactions.log_transactions([{
            'note': "test2",
            'category': "e",
            'product': "f",
            'price_name': "g",
            'quantity': 2,
            'price': 5
        }])
        self.assertEqual(len(list(transactions.get(id__gt=1))), 2)
