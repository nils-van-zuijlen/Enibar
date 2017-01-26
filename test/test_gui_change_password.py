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

from PyQt5 import QtCore, QtWidgets
import api.users
import basetest
import gui.password_management_window


class ChangePasswordTest(basetest.BaseGuiTest):
    def setUp(self):
        self._reset_db()
        super().setUp()
        self.win = gui.password_management_window.PasswordManagementWindow()

    def test_ok(self):
        """ Test changing password
        """
        self.win.pseudo_input.setText("azerty")
        self.win.old_password_input.setText("azerty")
        self.win.new_password_input.setText("qsdfgh")
        self.win.accept()
        self.assertTrue(api.users.is_authorized("azerty", "qsdfgh"))

    def test_not_ok(self):
        """ Test changing password with bad auth
        """
        def callback():
            win = self.app.activeWindow()
            self.assertIsInstance(win, QtWidgets.QMessageBox)
            self.assertIn("L'authentification", win.informativeText())
            win.accept()
            self.assertFalse(api.users.is_authorized("azerty", "qsdfgh"))
        self.win.pseudo_input.setText("azerty")
        self.win.old_password_input.setText("qsdfgh")
        self.win.new_password_input.setText("osef")
        QtCore.QTimer.singleShot(1000, callback)
        self.win.accept()

