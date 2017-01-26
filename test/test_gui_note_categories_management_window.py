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

from PyQt5 import QtWidgets, QtCore, QtGui
import basetest
import gui.note_categories_management_window
import api.notes as notes


class TestNotecategoriesManagementWindow(basetest.BaseGuiTest):
    def setUp(self):
        super().setUp()
        self._reset_db()
        self.note0 = notes.add("test0",
            "test",
            "test",
            "test@pouette.com",
            "0600000000",
            '12/12/2001',
            '1A',
            '',
            True,
            True
        )
        self.note1 = notes.add("test1",
            "test1",
            "test1",
            "test@pouette.com",
            "0600000000",
            '12/12/2001',
            '1A',
            '../test/resources/coucou.jpg',
            True,
            True
        )
        notes.rebuild_cache()
        self.win = gui.note_categories_management_window.NoteCategoriesManagementWindow()

    def test_add_note_categories(self):
        self.win.add_note_category_input.setText("test1")
        self.app.sendEvent(self.win.add_note_category_input, QtGui.QKeyEvent(QtGui.QKeyEvent.KeyPress, QtCore.Qt.Key_Return, QtCore.Qt.NoModifier))

        self.assertEqual(self.win.add_note_category_input.text(), "")
        self.assertEqual(self.get_items(self.win.shown_note_categories_list), ['test1'])
        self.assertEqual(self.get_items(self.win.hidden_note_categories_list), [])

        self.win.add_note_category_input.setText("test2")
        self.win.add_note_category_button.click()

        self.assertEqual(self.win.add_note_category_input.text(), "")
        self.assertEqual(self.get_items(self.win.shown_note_categories_list), ['test1', 'test2'])
        self.assertEqual(self.get_items(self.win.hidden_note_categories_list), [])

        self.win.add_note_category_input.setText("test2")

        def verif():
            win = self.app.activeWindow()
            self.assertIsInstance(win, QtWidgets.QMessageBox)
            win.accept()
        QtCore.QTimer.singleShot(200, verif)
        self.win.add_note_category_button.click()

    def test_hide_show_note_category(self):
        self.win.add_note_category_input.setText("test1")
        self.win.add_note_category_button.click()
        self.win.add_note_category_input.setText("test2")
        self.win.add_note_category_button.click()

        self.win.shown_note_categories_list.setCurrentRow(0)
        self.win.hide_note_category_button.click()
        self.assertEqual(self.get_items(self.win.shown_note_categories_list), ['test2'])
        self.assertEqual(self.get_items(self.win.hidden_note_categories_list), ['test1'])

        self.win.hidden_note_categories_list.setCurrentRow(0)
        self.win.show_note_category_button.click()
        self.assertEqual(self.get_items(self.win.shown_note_categories_list), ['test1', 'test2'])

    def test_delete_note_category(self):
        self.win.add_note_category_input.setText("test1")
        self.win.add_note_category_button.click()
        self.win.add_note_category_input.setText("test2")
        self.win.add_note_category_button.click()

        self.win.shown_note_categories_list.setCurrentRow(0)
        self.win.delete_note_category_button.click()
        self.assertEqual(self.get_items(self.win.shown_note_categories_list), ['test2'])
        self.assertEqual(self.get_items(self.win.hidden_note_categories_list), [])

    def test_add_remove_note_in_category(self):
        self.win.add_note_category_input.setText("test1")
        self.win.add_note_category_button.click()
        self.win.add_note_category_input.setText("test2")
        self.win.add_note_category_button.click()

        self.win.tabWidget.setCurrentIndex(1)

        self.assertEqual(self.get_items(self.win.notes_not_in_category_list), ['test0', 'test1'])
        self.win.notes_not_in_category_list.setCurrentRow(0)
        self.win.add_notes_in_category_btn.click()
        self.assertEqual(self.get_items(self.win.notes_not_in_category_list), ['test1'])
        self.assertEqual(self.get_items(self.win.notes_in_category_list), ['test0'])

        self.win.note_categories_selector.setCurrentIndex(1)
        self.assertEqual(self.get_items(self.win.notes_not_in_category_list), ['test0', 'test1'])
        self.assertEqual(self.get_items(self.win.notes_in_category_list), [])

        self.win.note_categories_selector.setCurrentIndex(0)
        self.assertEqual(self.get_items(self.win.notes_not_in_category_list), ['test1'])
        self.win.notes_in_category_list.setCurrentRow(0)
        self.win.remove_notes_from_category_btn.click()
        self.assertEqual(self.get_items(self.win.notes_not_in_category_list), ['test0', 'test1'])
