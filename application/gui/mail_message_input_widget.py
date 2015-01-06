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

from PyQt5 import QtCore, QtWidgets, QtGui
import api.mail
import re


class MailMessageInput(QtWidgets.QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.completer = QtWidgets.QCompleter(sorted([k for k in api.mail.COMPLETION_FIELD]), self)
        self.completer.activated.connect(self.insert_completion)
        self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.completer.setModelSorting(QtWidgets.QCompleter.CaseSensitivelySortedModel)

    def insert_completion(self, completion):
        text_cursor = self.textCursor()
        for i in range(len(self.completer.completionPrefix())):
            text_cursor.deletePreviousChar()
        text_cursor.movePosition(QtGui.QTextCursor.EndOfWord)
        text_cursor.insertText("{" + completion + "}")
        self.setTextCursor(text_cursor);

    def focusInEvent(self, event):
        self.completer.setWidget(self)
        super().focusInEvent(event)

    def text_under_cursor(self):
        text_cursor = self.textCursor()
        text_cursor.select(QtGui.QTextCursor.WordUnderCursor)
        return text_cursor.selectedText()

    def keyPressEvent(self, event):
        if self.completer.popup().isVisible():
            blacklisted_keys = [
                QtCore.Qt.Key_Enter,
                QtCore.Qt.Key_Return,
                QtCore.Qt.Key_Escape,
                QtCore.Qt.Key_Tab,
                QtCore.Qt.Key_Backtab,
            ]
            if event.key() in blacklisted_keys:
                event.ignore()
                return

        if event.key() != QtCore.Qt.Key_Tab:
            super().keyPressEvent(event)

        ctrlOrShift = event.modifiers() and (QtCore.Qt.ControlModifier or QtCore.Qt.ShiftModifier)
        if ctrlOrShift and not event.text():
            return;

        eow = "~!@#$%^&*()_+|:\"<>?,./;'[]\\-={}"
        hasModifier = (event.modifiers() != QtCore.Qt.NoModifier) and not ctrlOrShift
        completionPrefix = self.text_under_cursor()

        if event.key() != QtCore.Qt.Key_Tab and (hasModifier or event.text() or event.text()[len(event.text()) - 1:] in eow):
            self.completer.popup().hide()
            return

        if completionPrefix != self.completer.completionPrefix():
            self.completer.setCompletionPrefix(completionPrefix)
            self.completer.popup().setCurrentIndex(self.completer.completionModel().index(0,0))

        cr = self.cursorRect()
        cr.setWidth(self.completer.popup().sizeHintForColumn(0) + self.completer.popup().verticalScrollBar().sizeHint().width());
        self.completer.complete(cr);
