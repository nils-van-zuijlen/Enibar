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
import gui.douchette_window
from PyQt5 import QtCore, QtGui, QtTest


class TestDouchette(basetest.BaseGuiTest):
    def setUp(self):
        super().setUp()
        self.code = None
        self.win = gui.douchette_window.DouchetteWindow(self.callaback_dou)

    def callaback_dou(self, arg):
        self.code = arg

    def test_replacement(self):
        """ Testing douchette input replacement
        """
        self.win.content_input.hasFocus = lambda: True  # With VD, hasFocus seems to be bugged...
        self.app.sendEvent(self.win.content_input, QtGui.QKeyEvent(QtGui.QKeyEvent.KeyPress, QtCore.Qt.Key_Ampersand, QtCore.Qt.NoModifier, "&"))
        self.app.sendEvent(self.win.content_input, QtGui.QKeyEvent(QtGui.QKeyEvent.KeyRelease, QtCore.Qt.Key_Ampersand, QtCore.Qt.NoModifier, "&"))
        self.app.sendEvent(self.win.content_input, QtGui.QKeyEvent(QtGui.QKeyEvent.KeyPress, QtCore.Qt.Key_Ampersand, QtCore.Qt.NoModifier, "é"))
        self.app.sendEvent(self.win.content_input, QtGui.QKeyEvent(QtGui.QKeyEvent.KeyRelease, QtCore.Qt.Key_Ampersand, QtCore.Qt.NoModifier, "é"))
        self.app.sendEvent(self.win.content_input, QtGui.QKeyEvent(QtGui.QKeyEvent.KeyPress, QtCore.Qt.Key_Ampersand, QtCore.Qt.NoModifier, "\""))
        self.app.sendEvent(self.win.content_input, QtGui.QKeyEvent(QtGui.QKeyEvent.KeyRelease, QtCore.Qt.Key_Ampersand, QtCore.Qt.NoModifier, "\""))
        self.app.sendEvent(self.win.content_input, QtGui.QKeyEvent(QtGui.QKeyEvent.KeyPress, QtCore.Qt.Key_Ampersand, QtCore.Qt.NoModifier, "'"))
        self.app.sendEvent(self.win.content_input, QtGui.QKeyEvent(QtGui.QKeyEvent.KeyRelease, QtCore.Qt.Key_Ampersand, QtCore.Qt.NoModifier, "'"))
        self.app.sendEvent(self.win.content_input, QtGui.QKeyEvent(QtGui.QKeyEvent.KeyPress, QtCore.Qt.Key_Ampersand, QtCore.Qt.NoModifier, "("))
        self.app.sendEvent(self.win.content_input, QtGui.QKeyEvent(QtGui.QKeyEvent.KeyRelease, QtCore.Qt.Key_Ampersand, QtCore.Qt.NoModifier, "("))
        self.app.sendEvent(self.win.content_input, QtGui.QKeyEvent(QtGui.QKeyEvent.KeyPress, QtCore.Qt.Key_Ampersand, QtCore.Qt.NoModifier, "-"))
        self.app.sendEvent(self.win.content_input, QtGui.QKeyEvent(QtGui.QKeyEvent.KeyRelease, QtCore.Qt.Key_Ampersand, QtCore.Qt.NoModifier, "-"))
        self.app.sendEvent(self.win.content_input, QtGui.QKeyEvent(QtGui.QKeyEvent.KeyPress, QtCore.Qt.Key_Ampersand, QtCore.Qt.NoModifier, "è"))
        self.app.sendEvent(self.win.content_input, QtGui.QKeyEvent(QtGui.QKeyEvent.KeyRelease, QtCore.Qt.Key_Ampersand, QtCore.Qt.NoModifier, "è"))
        self.app.sendEvent(self.win.content_input, QtGui.QKeyEvent(QtGui.QKeyEvent.KeyPress, QtCore.Qt.Key_Ampersand, QtCore.Qt.NoModifier, "_"))
        self.app.sendEvent(self.win.content_input, QtGui.QKeyEvent(QtGui.QKeyEvent.KeyRelease, QtCore.Qt.Key_Ampersand, QtCore.Qt.NoModifier, "_"))
        self.app.sendEvent(self.win.content_input, QtGui.QKeyEvent(QtGui.QKeyEvent.KeyPress, QtCore.Qt.Key_Ampersand, QtCore.Qt.NoModifier, "ç"))
        self.app.sendEvent(self.win.content_input, QtGui.QKeyEvent(QtGui.QKeyEvent.KeyRelease, QtCore.Qt.Key_Ampersand, QtCore.Qt.NoModifier, "ç"))
        self.app.sendEvent(self.win.content_input, QtGui.QKeyEvent(QtGui.QKeyEvent.KeyPress, QtCore.Qt.Key_Ampersand, QtCore.Qt.NoModifier, "à"))
        self.app.sendEvent(self.win.content_input, QtGui.QKeyEvent(QtGui.QKeyEvent.KeyRelease, QtCore.Qt.Key_Ampersand, QtCore.Qt.NoModifier, "à"))
        self.app.sendEvent(self.win.content_input, QtGui.QKeyEvent(QtGui.QKeyEvent.KeyPress, QtCore.Qt.Key_Return, QtCore.Qt.NoModifier))
        self.assertEqual(self.code, "1234567890")

    def test_replacement_maj(self):
        """ Testing douchette input replacement in caps lock
        """
        self.win.content_input.hasFocus = lambda: True  # With VD, hasFocus seems to be bugged...
        self.app.sendEvent(self.win.content_input, QtGui.QKeyEvent(QtGui.QKeyEvent.KeyPress, QtCore.Qt.Key_Ampersand, QtCore.Qt.ShiftModifier, "&"))
        self.app.sendEvent(self.win.content_input, QtGui.QKeyEvent(QtGui.QKeyEvent.KeyRelease, QtCore.Qt.Key_Ampersand, QtCore.Qt.ShiftModifier, "&"))
        self.app.sendEvent(self.win.content_input, QtGui.QKeyEvent(QtGui.QKeyEvent.KeyPress, QtCore.Qt.Key_Ampersand, QtCore.Qt.ShiftModifier, "É"))
        self.app.sendEvent(self.win.content_input, QtGui.QKeyEvent(QtGui.QKeyEvent.KeyRelease, QtCore.Qt.Key_Ampersand, QtCore.Qt.ShiftModifier, "É"))
        self.app.sendEvent(self.win.content_input, QtGui.QKeyEvent(QtGui.QKeyEvent.KeyPress, QtCore.Qt.Key_Ampersand, QtCore.Qt.ShiftModifier, "\""))
        self.app.sendEvent(self.win.content_input, QtGui.QKeyEvent(QtGui.QKeyEvent.KeyRelease, QtCore.Qt.Key_Ampersand, QtCore.Qt.ShiftModifier, "\""))
        self.app.sendEvent(self.win.content_input, QtGui.QKeyEvent(QtGui.QKeyEvent.KeyPress, QtCore.Qt.Key_Ampersand, QtCore.Qt.ShiftModifier, "'"))
        self.app.sendEvent(self.win.content_input, QtGui.QKeyEvent(QtGui.QKeyEvent.KeyRelease, QtCore.Qt.Key_Ampersand, QtCore.Qt.ShiftModifier, "'"))
        self.app.sendEvent(self.win.content_input, QtGui.QKeyEvent(QtGui.QKeyEvent.KeyPress, QtCore.Qt.Key_Ampersand, QtCore.Qt.ShiftModifier, "("))
        self.app.sendEvent(self.win.content_input, QtGui.QKeyEvent(QtGui.QKeyEvent.KeyRelease, QtCore.Qt.Key_Ampersand, QtCore.Qt.ShiftModifier, "("))
        self.app.sendEvent(self.win.content_input, QtGui.QKeyEvent(QtGui.QKeyEvent.KeyPress, QtCore.Qt.Key_Ampersand, QtCore.Qt.ShiftModifier, "-"))
        self.app.sendEvent(self.win.content_input, QtGui.QKeyEvent(QtGui.QKeyEvent.KeyRelease, QtCore.Qt.Key_Ampersand, QtCore.Qt.ShiftModifier, "-"))
        self.app.sendEvent(self.win.content_input, QtGui.QKeyEvent(QtGui.QKeyEvent.KeyPress, QtCore.Qt.Key_Ampersand, QtCore.Qt.ShiftModifier, "È"))
        self.app.sendEvent(self.win.content_input, QtGui.QKeyEvent(QtGui.QKeyEvent.KeyRelease, QtCore.Qt.Key_Ampersand, QtCore.Qt.ShiftModifier, "È"))
        self.app.sendEvent(self.win.content_input, QtGui.QKeyEvent(QtGui.QKeyEvent.KeyPress, QtCore.Qt.Key_Ampersand, QtCore.Qt.ShiftModifier, "_"))
        self.app.sendEvent(self.win.content_input, QtGui.QKeyEvent(QtGui.QKeyEvent.KeyRelease, QtCore.Qt.Key_Ampersand, QtCore.Qt.ShiftModifier, "_"))
        self.app.sendEvent(self.win.content_input, QtGui.QKeyEvent(QtGui.QKeyEvent.KeyPress, QtCore.Qt.Key_Ampersand, QtCore.Qt.ShiftModifier, "Ç"))
        self.app.sendEvent(self.win.content_input, QtGui.QKeyEvent(QtGui.QKeyEvent.KeyRelease, QtCore.Qt.Key_Ampersand, QtCore.Qt.ShiftModifier, "Ç"))
        self.app.sendEvent(self.win.content_input, QtGui.QKeyEvent(QtGui.QKeyEvent.KeyPress, QtCore.Qt.Key_Ampersand, QtCore.Qt.ShiftModifier, "À"))
        self.app.sendEvent(self.win.content_input, QtGui.QKeyEvent(QtGui.QKeyEvent.KeyRelease, QtCore.Qt.Key_Ampersand, QtCore.Qt.ShiftModifier, "À"))
        self.app.sendEvent(self.win.content_input, QtGui.QKeyEvent(QtGui.QKeyEvent.KeyPress, QtCore.Qt.Key_Return, QtCore.Qt.NoModifier))
        self.assertEqual(self.code, "1234567890")

