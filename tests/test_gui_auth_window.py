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

from PyQt5 import QtWidgets, QtCore
import basetest
from gui.auth_prompt_window import ask_auth
import settings


def callback_for_func():
    """ We need to define this outside of the class because python won't let us
        use self in a decorator of a method
    """
    TestAuthPrompt.callback_called = True


class TestAuthPrompt(basetest.BaseGuiTest):
    def setUp(self):
        super().setUp()
        TestAuthPrompt.callback_called = False
        self.func_called = False

    @ask_auth("manage_products")
    def func(self):
        self.func_called = True

    @ask_auth("inexistant_right")
    def func_inexistant(self):
        self.func_called = True

    @ask_auth("manage_products", fail_callback=callback_for_func)
    def func_callback(self):
        self.func_called = True

    @ask_auth("manage_products", pass_performer=True)
    def func_performer(self, _performer):
        self.func_called = True
        self.assertEqual(_performer, "azerty")

    def test_debug(self):
        """ Testing debug
        """
        settings.DEBUG = True
        self.func()
        self.assertTrue(self.func_called)
        settings.DEBUG = False

    def fill_fail_auth(self, callback):
        """ Used to fill the window
        """
        QtCore.QTimer.singleShot(1000, callback)
        win = self.app.activeWindow()
        win.pass_input.setText("coucuo")
        win.accept()

    def test_no_allowed(self):
        """ Testing no people allowed auth
        """
        def callback():
            win = self.app.activeWindow()
            self.assertIsInstance(win, QtWidgets.QMessageBox)
            self.assertIn("Personne n'a", win.informativeText())
            win.accept()
            self.assertFalse(self.func_called)
        QtCore.QTimer.singleShot(200, callback)
        self.func_inexistant()

    def test_bad_passwd(self):
        """ Testing bad password auth
        """
        def callback():
            """ used to make verif
            """
            win = self.app.activeWindow()
            self.assertIsInstance(win, QtWidgets.QMessageBox)
            self.assertIn("Erreur d'auth", win.informativeText())
            win.accept()
            self.assertFalse(self.func_called)
        QtCore.QTimer.singleShot(200, lambda: self.fill_fail_auth(callback))

    def test_fail_callback(self):
        """ Testing fail callback in auth
        """
        def callback():
            win = self.app.activeWindow()
            self.assertFalse(self.func_called)
            win.accept()

        QtCore.QTimer.singleShot(1000, lambda: self.fill_fail_auth(callback))
        self.func_callback()

    def test_pass_performer(self):
        """ Testing pass_performer in auth
        """
        def callback():
            win = self.app.activeWindow()
            win.pass_input.setText("azerty")
            win.accept()
        QtCore.QTimer.singleShot(200, callback)
        self.func_performer()

