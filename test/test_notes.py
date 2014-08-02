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
import time
import api.notes as notes
from database import Cursor


class NotesTest(unittest.TestCase):
    def setUp(self):
        with Cursor() as cursor:
            cursor.exec("TRUNCATE TABLE notes")

    def count_notes(self):
        """ Returns the number of notes currently in database """
        with Cursor() as cursor:
            cursor.exec("SELECT COUNT(*) FROM notes")
            if cursor.next():
                return cursor.record().value(0)

    def test_add(self):
        """ Testing adding notes """

        self.assertEqual(notes.add("test1",
            "test1",
            "test1",
            "test@pouette.com",
            "0600000000",
            0,
            '1A',
            ''
        ), 1)
        self.assertEqual(notes.add("test2",
            "test2",
            "test2",
            "test@pouette.com",
            "0600000000",
            0,
            '1A',
            ''
        ), 2)
        self.assertEqual(notes.add("test2",
            15,
            "test2",
            "test@pouette.com",
            "0600000000",
            0,
            '1A',
            ''
        ), -1)
        self.assertEqual(self.count_notes(), 2)

    def test_remove(self):
        """ Testing removing notes """
        id_ = notes.add("test1",
            "test1",
            "test1",
            "test@pouette.com",
            "0600000000",
            0,
            '1A',
            ''
        )

        self.assertTrue(notes.remove(id_))
        self.assertEqual(self.count_notes(), 0)

    def test_get_by_id(self):
        """ Testing get_by_id """
        id_ = notes.add("test1",
            "test",
            "test",
            "test@pouette.com",
            "0600000000",
            0,
            '1A',
            '/coucou.jpg'
        )
        getted = notes.get_by_id(id_)
        self.assertEqual(getted, {'id': id_,
                                 'nickname': 'test1',
                                 'surname': 'test',
                                 'firstname': 'test',
                                 'mail': 'test@pouette.com',
                                 'tel': '0600000000',
                                 'birthdate': 0,
                                 'promo': '1A',
                                 'note': 0,
                                 'overdraft_time': 0,
                                 'ecocups': 0,
                                 'photo_path': '/coucou.jpg',
                                 'hidden': 0})

    def test_get_by_name(self):
        """ Testing get_by_name """
        id1 = notes.add("test0",
            "test",
            "test",
            "test@pouette.com",
            "0600000000",
            0,
            '1A',
            ''
        )
        id2 = notes.add("test1",
            "test",
            "test",
            "test@pouette.com",
            "0600000000",
            0,
            '1A',
            ''
        )
        id3 = notes.add("pouette",
            "test",
            "test",
            "test@pouette.com",
            "0600000000",
            0,
            '1A',
            ''
        )

        self.assertEqual(list(notes.get_by_nickname('test')), [{'id': i + 1,
                                 'nickname': 'test' + str(i),
                                 'surname': 'test',
                                 'firstname': 'test',
                                 'mail': 'test@pouette.com',
                                 'tel': '0600000000',
                                 'birthdate': 0,
                                 'promo': '1A',
                                 'note': 0,
                                 'overdraft_time': 0,
                                 'ecocups': 0,
                                 'photo_path': '',
                                 'hidden': 0} for i in range(2)])

    def test_get_by_minors(self):
        """ Testing get minors """
        time0 = round(time.time() - 19 * 365 * 24 * 3600)
        time1 = round(time.time() - 17 * 365 * 24 * 3600)
        id0 = notes.add("test0",
            "test",
            "test",
            "test@pouette.com",
            "0600000000",
            time0,
            '1A',
            ''
        )
        id1 = notes.add("test1",
            "test",
            "test",
            "test@pouette.com",
            "0600000000",
            time1,
            '1A',
            ''
        )

        self.assertEqual(list(notes.get_minors()), [{'id': id1,
                                 'nickname': 'test1',
                                 'surname': 'test',
                                 'firstname': 'test',
                                 'mail': 'test@pouette.com',
                                 'tel': '0600000000',
                                 'birthdate': time1,
                                 'promo': '1A',
                                 'note': 0,
                                 'overdraft_time': 0,
                                 'ecocups': 0,
                                 'photo_path': '',
                                 'hidden': 0}])

    def test_get_by_majors(self):
        """ Testing get majors """
        time0 = round(time.time() - 19 * 365 * 24 * 3600)
        time1 = round(time.time() - 17 * 365 * 24 * 3600)
        id0 = notes.add("test0",
            "test",
            "test",
            "test@pouette.com",
            "0600000000",
            time0,
            '1A',
            ''
        )
        id1 = notes.add("test1",
            "test",
            "test",
            "test@pouette.com",
            "0600000000",
            time1,
            '1A',
            ''
        )

        self.assertEqual(list(notes.get_majors()), [{'id': id0,
                                 'nickname': 'test0',
                                 'surname': 'test',
                                 'firstname': 'test',
                                 'mail': 'test@pouette.com',
                                 'tel': '0600000000',
                                 'birthdate': time0,
                                 'promo': '1A',
                                 'note': 0,
                                 'overdraft_time': 0,
                                 'ecocups': 0,
                                 'photo_path': '',
                                 'hidden': 0}])

    def test_transaction(self):
        """ Testing transactions """
        id1 = notes.add("test1",
            "test",
            "test",
            "test@pouette.com",
            "0600000000",
            "0",
            '1A',
            ''
        )

        notes.transaction(id1, 10)
        self.assertEqual(notes.get_by_id(id1)['note'], 10)
        notes.transaction(id1, 10)
        self.assertEqual(notes.get_by_id(id1)['note'], 20)
        notes.transaction(id1, -5)
        self.assertEqual(notes.get_by_id(id1)['note'], 15)
        notes.transaction(id1, -15)
        self.assertEqual(notes.get_by_id(id1)['note'], 0)
        notes.transaction(id1, 5)
        notes.transaction(id1, -4.95)
        self.assertEqual(notes.get_by_id(id1)['note'], 0.05)

