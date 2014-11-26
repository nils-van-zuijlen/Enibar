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

from database import Cursor
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
            ''
        )
        notes.transaction("test1", -7)
        notes.add("test2",
            "test1",
            "test1",
            "test@pouette.com",
            "0600000000",
            '12/12/2001',
            '1A',
            ''
        )
        notes.transaction("test2", 10)
        notes.add("test3",
            "test1",
            "test1",
            "test@pouette.com",
            "0600000000",
            '12/12/2001',
            '1A',
            ''
        )
        notes.transaction("test3", -10)
        notes.add("test4",
            "test1",
            "test1",
            "test@pouette.com",
            "0600000000",
            '12/12/2001',
            '1A',
            ''
        )
        notes.transaction("test4", 8)

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

    def test_get_red(self):
        self.assertEqual(stats.get_red(), {"total_red": -17, 'nb_notes': 2})

    def test_get_green(self):
        self.assertEqual(stats.get_green(), {"total_green": 18, 'nb_notes': 2})

    def test_get_sold(self):
        self.assertEqual(list(stats.get_sold_items()),
            [{'product': 'b', 'nb': 2, 'price_name': 'c', 'category': 'a'},
             {'product': 'e', 'nb': 1, 'price_name': 'f', 'category': 'd'}]
        )

    def test_get_consumers(self):
        self.assertEqual(list(stats.get_consumers()),
            [{'refilled': 0.0, 'bought': 3.0, 'note': 'test1'},
             {'refilled': 0.0, 'bought': 1.0, 'note': 'test2'}]
        )

