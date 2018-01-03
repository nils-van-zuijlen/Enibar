# Copyright (C) 2014-2018 Bastien Orivel <b2orivel@enib.fr>
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

import api.stats as stats
import api.notes as notes
import api.transactions as transactions
import api.redis


class StatsTests(basetest.BaseTest):
    def setUp(self):
        super().setUp()
        api.redis.send_message = lambda x, y: [notes.rebuild_note_cache(note) for note in y]
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
        self.add_transaction(["test1", ], -7)
        notes.add("test2",
            "test2",
            "test2",
            "test@pouette.com",
            "0600000000",
            '12/12/2001',
            '1A',
            '',
            True,
            True
        )
        self.add_transaction(["test2", ], 10)
        notes.add("test3",
            "test3",
            "test3",
            "test@pouette.com",
            "0600000000",
            '12/12/2001',
            '1A',
            '',
            True,
            True
        )
        self.add_transaction(["test3", ], -10)
        notes.add("test4",
            "test4",
            "test4",
            "test@pouette.com",
            "0600000000",
            '12/12/2001',
            '1A',
            '',
            True,
            True
        )
        self.add_transaction(["test4", ], 8)
        notes.add("test12",
            "test12",
            "test12",
            "test@pouette.com",
            "0600000000",
            '12/12/2001',
            '1A',
            '',
            False,
            True
        )

        # History

        transactions.log_transactions([{
            'note': "test1",
            'category': "a",
            'product': "b",
            'price_name': "c",
            'quantity': 1,
            'price': -1,
        }])
        transactions.log_transactions([{
            'note': "test2",
            'category': "a",
            'product': "b",
            'price_name': "c",
            'quantity': 1,
            'price': -1,
        }])
        transactions.log_transactions([{
            'note': "test1",
            'category': "d",
            'product': "e",
            'price_name': "f",
            'quantity': 1,
            'price': -2,
        }])

    def test_get_stats(self):
        self.assertCountEqual(list(stats.get_notes_stats()),
            [{'nickname': 'test1', 'product': 'test', 'price_name': 'test', 'price': -7.0, 'category': 'Test', 'quantity': 1},
             {'nickname': 'test3', 'product': 'test', 'price_name': 'test', 'price': -10.0, 'category': 'Test', 'quantity': 1},
             {'nickname': 'test2', 'product': 'test', 'price_name': 'test', 'price': 10.0, 'category': 'Test', 'quantity': 1},
             {'nickname': 'test4', 'product': 'test', 'price_name': 'test', 'price': 8.0, 'category': 'Test', 'quantity': 1},
             {'price_name': 'c', 'category': 'a', 'nickname': 'test1', 'price': -1.0, 'quantity': 1.0, 'product': 'b'},
             {'price_name': 'f', 'category': 'd', 'nickname': 'test1', 'price': -2.0, 'quantity': 1.0, 'product': 'e'},
             {'price_name': 'c', 'category': 'a', 'nickname': 'test2', 'price': -1.0, 'quantity': 1.0, 'product': 'b'},
            ]
        )

    def test_red_sum(self):
        red = api.stats.get_red_sum()
        self.assertEqual((2, -20), red)

    def test_green_sum(self):
        green = api.stats.get_green_sum()
        self.assertEqual((2, 17), green)

    def test_red_notes(self):
        red_notes = api.stats.get_red_notes()
        self.assertEqual([('test3', -10.0), ('test1', -10.0)], list(red_notes))

    def test_ecocups_nb(self):
        api.notes.change_ecocups("test1", 5)
        api.notes.change_ecocups("test2", 7)
        ecocups = api.stats.get_ecocups_nb()
        self.assertEqual(ecocups, 12)

