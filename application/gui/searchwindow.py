# Copyright (C) 2014 Bastien Orivel <b2orivel@enib.fr>
# Copyright (C) 2014 Arnaud Levaufre <a2levauf@enib.fr>
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

"""
SearchWindow
============

The SearchWindow is a tool window that will refresh the MainWindow.notes_list
according to the things in its inputs.

"""


from PyQt5 import QtWidgets, uic, QtCore
import api.validator
from database import Cursor
import gui.utils


class SearchWindow(QtWidgets.QDialog):
    """ SearchWindow class """
    def __init__(self, parent):
        super().__init__(parent)
        uic.loadUi('ui/searchwindow.ui', self)
        self.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint)
        self.name_input.set_validator(api.validator.NAME)
        self.firstname_input.set_validator(api.validator.NAME)
        self.show()

    def on_change(self):
        def notes_filter(note):
            if note["hidden"]:
                return False
            if self.name_input.valid:
                if self.name_input.text().lower() not in note["lastname"].lower():
                    return False
            if self.firstname_input.valid:
                if self.firstname_input.text().lower() not in note["firstname"].lower():
                    return False

            return True
        notes_list = self.parent().parent().notes_list
        notes_list.current_filter = notes_filter
        notes_list.refresh(api.notes.get(notes_list.current_filter))
