# Copyright (C) 2014-2015 Bastien Orivel <b2orivel@enib.fr>
# Copyright (C) 2014-2015 Arnaud Levaufre <a2levauf@enib.fr>
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


class StatsTests(basetest.BaseTest):
    def setUp(self):
        self._reset_db()
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
        notes.transactions(["test1", ], -7)
        notes.add("test2",
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
        notes.transactions(["test2", ], 10)
        notes.add("test3",
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
        notes.transactions(["test3", ], -10)
        notes.add("test4",
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
        notes.transactions(["test4", ], 8)
        notes.add("test12",
            "test1",
            "test1",
            "test@pouette.com",
            "0600000000",
            '12/12/2001',
            '1A',
            '',
            False,
            True
        )

        # Hitory

        transactions.log_transaction(
            "test1",
            "a",
            "b",
            "c",
            "1",
            -1
        )
        transactions.log_transaction(
            "test2",
            "a",
            "b",
            "c",
            "1",
            -1
        )
        transactions.log_transaction(
            "test1",
            "d",
            "e",
            "f",
            "1",
            -2
        )

    def test_get_stats(self):
        self.assertEqual(list(stats.get_notes_stats()),
            [{'price_name': 'c', 'category': 'a', 'nickname': 'test1', 'price': -1.0, 'quantity': 2.0, 'product': 'b'},
             {'price_name': 'f', 'category': 'd', 'nickname': 'test1', 'price': -2.0, 'quantity': 1.0, 'product': 'e'},
             {'price_name': 'c', 'category': 'a', 'nickname': 'test2', 'price': -1.0, 'quantity': 2.0, 'product': 'b'},
             {'price_name': 'f', 'category': 'd', 'nickname': 'test2', 'price': -2.0, 'quantity': 1.0, 'product': 'e'},
             {'price_name': 'c', 'category': 'a', 'nickname': 'test3', 'price': -1.0, 'quantity': 2.0, 'product': 'b'},
             {'price_name': 'f', 'category': 'd', 'nickname': 'test3', 'price': -2.0, 'quantity': 1.0, 'product': 'e'},
             {'price_name': 'c', 'category': 'a', 'nickname': 'test4', 'price': -1.0, 'quantity': 2.0, 'product': 'b'},
             {'price_name': 'f', 'category': 'd', 'nickname': 'test4', 'price': -2.0, 'quantity': 1.0, 'product': 'e'}]
        )

