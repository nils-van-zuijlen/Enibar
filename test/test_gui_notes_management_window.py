# Copyright (C) 2014-2016 Bastien Orivel <b2orivel@enib.fr>
# Copyright (C) 2014-2016 Arnaud Levaufre <a2levauf@enib.fr>
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
from PyQt5 import QtCore, QtWidgets
import gui.notes_management_window
import api.notes
import api.note_categories


class NotesManagementWindowTest(basetest.BaseGuiTest):
    def setUp(self):
        self._reset_db()
        super().setUp()
        self.add_note("test")
        self.add_note("test2")
        api.note_categories.add("cat1")
        api.note_categories.add("cat2")
        api.notes.rebuild_cache()
        self.win = gui.notes_management_window.NotesManagementWindow(None)

    def test_notes_list(self):
        self.assertEqual(self.get_items(self.win.note_list), ["test", "test2"])

    def _test_add_remove_categories(self):
        self.assertEqual(self.get_items(self.win.category_list), [])
        self.assertEqual(self.win.category_selector.currentText(), "cat1")
        self.win.add_category_button.click()
        self.assertEqual(self.win.category_selector.currentText(), "cat2")
        self.assertEqual(self.get_items(self.win.category_list), ["cat1"])
        self.win.add_category_button.click()
        self.assertEqual(self.get_items(self.win.category_list), ["cat1", "cat2"])
        self.assertEqual(self.win.category_selector.currentText(), "")
        self.win.remove_category_button.click()

        self.win.category_list.setCurrentRow(1)
        self.win.remove_category_button.click()
        self.assertEqual(self.win.category_selector.currentText(), "cat2")
        self.assertEqual(self.get_items(self.win.category_list), ["cat1"])
        self.win.category_list.setCurrentRow(0)
        self.win.remove_category_button.click()
        self.win.category_selector.setCurrentIndex(1)
        self.assertEqual(self.win.category_selector.currentText(), "cat1")
        self.assertEqual(self.get_items(self.win.category_list), [])
        self.win.remove_category_button.click()

    def test_add_remove_category_to_note(self):
        self.win.note_list.setCurrentRow(0)
        self._test_add_remove_categories()

    def test_add_remove_category_to_note_when_adding(self):
        self.win.add_button.click()
        self._test_add_remove_categories()
        self.win.add_category_button.click()
        self.win.nickname_input.setText("test3")
        self.win.first_name_input.setText("test3")
        self.win.name_input.setText("test3")
        self.win.birthdate_input.setText("29/03/1994")
        self.win.mail_input.setText("cououc@coucou.rf")
        self.win.phone_input.setText("0565656451")
        self.win.save_button.click()

        def verif():
            self.assertEqual(self.get_items(self.win.note_list), ["test", "test2", "test3"])
            note = api.note.get(lambda x: x['nickname'] == "test3")[0]
            self.assertEqual(note["categories"], ["test1"])

        QtCore.QTimer.singleShot(200, verif)

