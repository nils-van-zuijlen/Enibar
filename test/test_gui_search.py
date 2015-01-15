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
import gui.search_window
import gui.main_window
import api.notes
from PyQt5 import QtTest


class SearchTest(basetest.BaseGuiTest):
    def setUp(self):
        self._reset_db()
        super().setUp()
        self.add_note("test", "abc", "def")
        self.add_note("test1", "bcd", "fgh")
        self.add_note("test2", "rty", "jhg")
        self.main_win = gui.main_window.MainWindow()
        self.search_window = gui.search_window.SearchWindow(self.main_win.menu_bar)

    def test_search_by_firstname(self):
        """ Testing search by firstname
        """
        self.search_window.firstname_input.setText("f")
        self.assertEqual(self.get_items(self.main_win.notes_list), ['test', 'test1'])
        self.search_window.firstname_input.setText("jh")
        self.assertEqual(self.get_items(self.main_win.notes_list), ['test2'])
        api.notes.hide(["test2"])
        self.search_window.firstname_input.setText("jhg")
        self.assertEqual(self.get_items(self.main_win.notes_list), [])

    def test_search_by_lastname(self):
        """ Testing search by lastname
        """
        self.search_window.name_input.setText("bc")
        self.assertEqual(self.get_items(self.main_win.notes_list), ['test', 'test1'])
        self.search_window.name_input.setText("rty")
        self.assertEqual(self.get_items(self.main_win.notes_list), ['test2'])

    def test_regression_114(self):
        """ Testing #114 regression
        """
        self.search_window.firstname_input.setText("z")
        self.search_window.firstname_input.setText("za")
        self.assertEqual(self.get_items(self.main_win.notes_list), [])
        QtTest.QTest.qWait(500)
        self.assertFalse(self.main_win.take_ecocup_btn.isEnabled())
        self.search_window.firstname_input.setText("")
        QtTest.QTest.qWait(500)
        self.assertTrue(self.main_win.take_ecocup_btn.isEnabled())

