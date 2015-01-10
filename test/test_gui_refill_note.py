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
from PyQt5 import QtCore, QtWidgets
import api.notes
import gui.refill_note_window
import gui.validation_window
import settings


class RefillNoteTest(basetest.BaseGuiTest):
    def setUp(self):
        self._reset_db()
        super().setUp()
        self.add_note("test")
        self.win = gui.refill_note_window.RefillNoteWindow("test", "azerty")

    def test_refill_note(self):
        """ Testing refill note
        """
        def callback():
            def verif():
                self.assertEqual(api.notes.get(lambda x: x['nickname'] == "test")[0]['note'], 20)
            validation = self.app.activeWindow()
            self.assertIsInstance(validation, gui.validation_window.ValidationWindow)
            timer = QtCore.QTimer.singleShot(200, verif)
            validation.accept()
        self.win.to_add.setText("20")
        self.win.reason.setText("coucou")
        timer = QtCore.QTimer.singleShot(200, callback)
        self.win.accept()

    def test_refill_note_bad_value(self):
        """ Testing refill note with bad value
        """
        def callback():
            def verif():
                self.assertEqual(api.notes.get(lambda x: x['nickname'] == "test")[0]['note'], 0)
            win = self.app.activeWindow()
            self.assertIsInstance(win, QtWidgets.QMessageBox)
            self.assertIn("superieur", win.informativeText())
            timer = QtCore.QTimer.singleShot(200, verif)
            win.accept()
        self.win.to_add.setText("0.001")
        self.win.reason.setText("coucou")
        timer = QtCore.QTimer.singleShot(200, callback)
        self.win.accept()


class RefillNoteMultiTest(basetest.BaseGuiTest):
    def setUp(self):
        self._reset_db()
        super().setUp()
        self.win = gui.refill_note_window.MultiRefillNoteWindow("azerty")

    def test_refill_notes(self):
        """ Testing multi refill note
        """
        def callback():
            def verif():
                self.assertEqual(self.win.to_add_value, 20)
            valid = self.app.activeWindow()
            timer = QtCore.QTimer.singleShot(200, verif)
            valid.accept()

        self.win.to_add.setText("20")
        self.win.reason.setText("coucou")
        timer = QtCore.QTimer.singleShot(200, callback)
        self.win.accept()

    def test_refill_notes_bad_value(self):
        """ Testing refill note with bad value
        """
        def callback():
            def verif():
                self.assertEqual(0, self.win.to_add_value)
            win = self.app.activeWindow()
            self.assertIsInstance(win, QtWidgets.QMessageBox)
            self.assertIn("superieur", win.informativeText())
            timer = QtCore.QTimer.singleShot(200, verif)
            win.accept()
        self.win.to_add.setText("0.001")
        self.win.reason.setText("coucou")
        timer = QtCore.QTimer.singleShot(200, callback)
        self.win.accept()

