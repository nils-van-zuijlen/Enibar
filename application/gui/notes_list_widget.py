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

"""
NotesList
=========

A custom QListWidget that  ontains the list of notes.
It refreshes itself every 10 seconds.
"""

from PyQt5 import QtWidgets, QtCore, QtGui
import time


class NotesList(QtWidgets.QListWidget):
    """ Notes list on the left of the MainWindow. """
    def __init__(self, parent):
        super().__init__(parent)
        self.current_filter = lambda x: x['hidden'] == 0
        self.minors_color = QtGui.QColor(255, 192, 203)
        self.overdraft_color = QtCore.Qt.red
        self.search_text = ""

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

            if not note['nickname'].lower().startswith(self.search_text):
                widget.setHidden(True)

    def hide_unmatched_items(self, search_text):
        self.search_text = search_text.lower()
        for i in range(self.count()):
            widget = self.item(i)
            if widget.text().lower().startswith(self.search_text):
                widget.setHidden(False)
            else:
                widget.setHidden(True)

    def refresh(self, notes_list):
        """ Refresh the note list
        """
        selected = self.currentItem()
        if selected:
            selected = selected.text()
        self.clear()
        self.build(notes_list)
        try:
            new_selection = self.findItems(selected, QtCore.Qt.MatchExactly)[0]
            self.setCurrentItem(new_selection)
        except IndexError:
            self.setCurrentRow(0)

