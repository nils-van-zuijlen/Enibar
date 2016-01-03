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

from PyQt5 import QtCore, QtWidgets
from database import Cursor
import basetest
import gui.users_management_window
import api.users


class UsersManagementTest(basetest.BaseGuiTest):
    def setUp(self):
        super().setUp()
        self._reset_db()
        api.users.add("test", "test")  # Test user
        self.win = gui.users_management_window.UsersManagementWindow()

    def select_user(self, user):
        user_widget = self.win.user_list.findItems(user, QtCore.Qt.MatchExactly)[0]
        self.win.user_list.setCurrentItem(user_widget)

    def delete_users(self):
        with Cursor() as cursor:
            cursor.prepare("DELETE FROM admins")
            cursor.exec_()

    def test_add_user(self):
        """ Testing adding an user
        """
        def callback():
            def verif():
                self.assertTrue(api.users.is_authorized("coucou", "coucou"))
                self.assertEqual(self.get_items(self.win.user_list), ['azerty', 'coucou'])
            win = self.app.activeWindow()
            self.assertIsInstance(win, gui.users_management_window.AddUserPrompt)
            win.username_input.setText("coucou")
            win.password_input.setText("coucou")
            win.validation_button.click()
            QtCore.QTimer.singleShot(200, verif)
        QtCore.QTimer.singleShot(200, callback)
        self.win.add_button.click()

    def test_remove_user(self):
        """ Testing removing an user
        """
        self.assertEqual(self.get_items(self.win.user_list), ['azerty', 'test'])
        self.select_user("test")
        self.win.delete_button.click()
        self.assertFalse(api.users.is_authorized("test", "test"))
        self.assertEqual(self.get_items(self.win.user_list), ['azerty'])

    def test_set_rights(self):
        """ Testing setting rights
        """
        self.select_user("test")
        self.win.manage_users.setChecked(True)
        self.win.manage_notes.setChecked(True)
        self.win.save_button.click()
        self.assertEqual(api.users.get_rights("test"), {"manage_users": True,
                                                        "manage_notes": True,
                                                        "manage_products": False})

    def test_add_user_error(self):
        """ Testing adding an existant user
        """
        def callback():
            def verif():
                win = self.app.activeWindow()
                self.assertIsInstance(win, QtWidgets.QMessageBox)
                self.assertIn("déjà pris", win.informativeText())
                win.accept()
            win = self.app.activeWindow()
            self.assertIsInstance(win, gui.users_management_window.AddUserPrompt)
            win.username_input.setText("test")
            win.password_input.setText("coucou")
            QtCore.QTimer.singleShot(1500, verif)
            win.validation_button.click()
            self.win.close()
            win.close()
        api.users.add('test', 'test')
        QtCore.QTimer.singleShot(200, callback)
        self.win.add_button.click()

    def test_save_no_user(self):
        """ Testing saving with no user
        """
        def callback():
            win = self.app.activeWindow()
            self.assertIsInstance(win, QtWidgets.QMessageBox)
            self.assertIn("Aucun", win.informativeText())
            win.accept()
        self.delete_users()
        self.win = gui.users_management_window.UsersManagementWindow()
        QtCore.QTimer.singleShot(200, callback)
        self.win.save_button.click()

    def test_delete_no_user(self):
        """ Testing deleting with no user
        """
        def callback():
            win = self.app.activeWindow()
            self.assertIsInstance(win, QtWidgets.QMessageBox)
            self.assertIn("Aucun", win.informativeText())
            win.accept()
        self.delete_users()
        self.win = gui.users_management_window.UsersManagementWindow()
        QtCore.QTimer.singleShot(200, callback)
        self.win.delete_button.click()
