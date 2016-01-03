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
import gui.empty_note_window
import api.notes


class EmpttNoteTest(basetest.BaseGuiTest):
    def setUp(self):
        self._reset_db()
        super().setUp()
        self.add_note("test")
        self.win = gui.empty_note_window.EmptyNoteWindow("test")

    def test_empty_note(self):
        """ Testing empty note
        """
        self.win.to_add.setText("20")
        self.win.reason.setText("coucou")
        self.win.accept()
        self.assertEqual(api.notes.get(lambda x: x['nickname'] == "test")[0]['note'], -20)

    def test_empty_note_bad_value(self):
        """ Testing empty note with bad value
        """
        def callback():
            win = self.app.activeWindow()
            self.assertIsInstance(win, QtWidgets.QMessageBox)
            self.assertIn("superieur", win.informativeText())
            self.assertEqual(api.notes.get(lambda x: x['nickname'] == "test")[0]['note'], 0)
            win.accept()
        self.win.to_add.setText("0.001")
        self.win.reason.setText("coucou")
        QtCore.QTimer.singleShot(200, callback)
        self.win.accept()

