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
Gui Utils
=========

Somme shortcut to do repetitive actions more easely
"""

import api.notes
from PyQt5 import QtWidgets, QtCore, QtGui
import time


def error(title, message=""):
    """ Display error with title and message
    """
    err = QtWidgets.QMessageBox()
    err.setText(title)
    err.setInformativeText(message)
    err.setIcon(QtWidgets.QMessageBox.Critical)
    err.exec()


class NotesList(QtWidgets.QListWidget):
    # pylint: disable=too-many-public-methods
    """ Notes list on the left of the MainWindow. """
    def __init__(self, parent):
        super().__init__(parent)
        self.minors_color =  QtGui.QColor(255, 192, 203)
        self.overdraft_color = QtCore.Qt.red

    def init_mw(self):
        """ Function used only on the main_window
        """
        self.refresh_timer = QtCore.QTimer(self)
        self.refresh_timer.setInterval(10 * 1000)  # 10 seconds
        self.refresh_timer.timeout.connect(self.on_timer)
        self.refresh_timer.start()

    def build(self, notes_list):
        """ Fill the list with notes from notes_list, coloring negatives one
            in red """
        current_time = time.time()
        for note in notes_list:
            widget = QtWidgets.QListWidgetItem(note["nickname"], self)
            if note['note'] < 0:
                widget.setBackground(self.overdraft_color)
            elif current_time - note["birthdate"] < 18 * 365 * 24 * 3600:
                widget.setBackground(self.minors_color)
            else:
                widget.setStyleSheet("background-color: none;")

    def on_timer(self):
        """ Rebuild the note list every 10 seconds
        """
        api.notes.rebuild_cache()
        self.refresh(api.notes.get(lambda x: x['hidden'] == 0))

    def clean(self):
        """ Clean the note list
        """
        print("Clean")
        for i in reversed(range(self.count())):
            a = self.takeItem(i)
            del a

    def refresh(self, notes_list):
        """ Refresh the note list
        """
        selected = self.currentRow()
        self.clean()
        self.build(notes_list)
        self.setCurrentRow(selected)

