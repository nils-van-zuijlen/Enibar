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

import api.users as users
from database import Cursor


class UsersTest(unittest.TestCase):
    def setUp(self):
        with Cursor() as cursor:
            cursor.exec("TRUNCATE TABLE admins")

    def count_admins(self):
        """ Test helper, returns the number of admins currently in database """
        with Cursor() as cursor:
            cursor.exec("SELECT COUNT(*) FROM admins")
            if cursor.next():
                return cursor.record().value(0)

    def test_add_user(self):
        """ Test adding an user  """
        self.assertTrue(users.add("test", "test"))
        self.assertTrue(users.add("test2", "test"))
        self.assertFalse(users.add("test", "test"))
        self.assertEqual(self.count_admins(), 2)

    def test_remove_user(self):
        """ Test removing an user """
        users.add("test", "test")

        self.assertTrue(users.remove("test"))
        self.assertEqual(self.count_admins(), 0)

    def test_change_password(self):
        """ Testing changing password """
        users.add("test", "test")

        self.assertTrue(users.change_password("test", "coucou"))
        self.assertTrue(users.is_authorized("test", "coucou"))
        self.assertFalse(users.is_authorized("test", "test"))

    def test_is_authorized(self):
        """ Testing authorization """
        users.add("test", "test")

        self.assertTrue(users.is_authorized("test", "test"))
        self.assertFalse(users.is_authorized("test2", "test"))
        self.assertFalse(users.is_authorized("test", "test2"))

    def test_get_lit(self):
        """ Testing users.get_list """
        users.add("test", "test")
        users.add("test1", "test")
        users.add("test2", "test")

        self.assertEqual(list(users.get_list()), ["test", "test1", "test2"])

    def test_rights(self):
        """ Testing rights """

        id1 = users.add("test", "test")
        id2 = users.add("test2", "test")

        self.assertTrue(users.set_rights("test", {'manage_users': True,
                                  'manage_notes': False,
                                  'manage_products': False}))

        self.assertEqual(users.get_rights("test"), {'manage_users': True,
                                                    'manage_notes': False,
                                                    'manage_products': False})

        self.assertEqual(users.get_rights("test2"), {'manage_users': False,
                                                     'manage_notes': False,
                                                     'manage_products': False})

    def test_issue_24(self):
        """ Testing issue #24 regression.
        """
        id1 = users.add("test", "test")
        id2 = users.add("test2", "test")
        id3 = users.add("test3", "test")
        users.set_rights("test", {'manage_users': True,
                                  'manage_notes': False,
                                  'manage_products': False})
        users.set_rights("test2", {'manage_users': True,
                                  'manage_notes': False,
                                  'manage_products': False})
        self.assertTrue(users.remove("test"))
        users.remove("test2")
        self.assertEqual(list(users.get_list()), ["test2", "test3"])
        users.remove("test3")
        self.assertEqual(list(users.get_list()), ["test2"])

