# Copyright (C) 2014-2018 Bastien Orivel <b2orivel@enib.fr>
# Copyright (C) 2014-2018 Arnaud Levaufre <a2levauf@enib.fr>
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

A custom QListWidget that contains the list of notes and can be filtered
"""

from PyQt5 import QtWidgets, QtCore, uic
import api.notes
import api.validator


class FilteredNotesListWidget(QtWidgets.QWidget):
    itemSelectionChanged = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        uic.loadUi('ui/filtered_notes_list_widget.ui', self)
        self.on_change = lambda: False
        self.filter_input.keyPressEvent = self.filter_input_changed
        self.filter_input.setEnabled(False)
        self.filter_input.set_validator(api.validator.ALL_NUMBER)
        self.search_input.setFocus(True)

    def set_filter(self, filter_):
        self.note_list.current_filter = filter_
        self.note_list.rebuild(api.notes.get(
            lambda x: self.note_list.custom_filter(x) and self.note_list.current_filter(x)))

    def set_custom_filter(self, filter_):
        self.note_list.custom_filter = filter_
        self.note_list.rebuild(api.notes.get(
            lambda x: self.note_list.custom_filter(x) and self.note_list.current_filter(x)))

    def filter_combobox_change(self, id_):
        """ Called when the filter combobox is changed
        """
        if id_ == 0:
            self.note_list.current_filter = lambda x: True
            self.filter_input.setEnabled(False)
        elif id_ == 1:
            self.note_list.current_filter = lambda x: x['hidden'] == 0
            self.filter_input.setEnabled(False)
        elif id_ == 2:
            self.note_list.current_filter = lambda x: x['hidden'] == 1
            self.filter_input.setEnabled(False)
        elif id_ == 3:
            self.filter_input.setEnabled(True)
            self.filter_input.setText("0")
            self.note_list.current_filter = lambda x: x['note'] > 0 and\
                x['hidden'] == 0
        elif id_ == 4:
            self.filter_input.setEnabled(True)
            self.filter_input.setText("0")
            self.note_list.current_filter = lambda x: x['note'] < 0 and\
                x['hidden'] == 0
        self.note_list.rebuild(api.notes.get(
            lambda x: self.note_list.custom_filter(x) and self.note_list.current_filter(x)))

    def filter_input_changed(self, event):
        """ Called when the filter input is changed
        """
        QtWidgets.QLineEdit.keyPressEvent(self.filter_input, event)
        text = self.filter_input.text()
        try:
            if self.filter_combobox.currentIndex() == 3:
                self.note_list.current_filter = lambda x: x['note'] >\
                    float(text) and x['hidden'] == 0
                self.note_list.rebuild(api.notes.get(
                    lambda x: self.note_list.custom_filter(x) and self.note_list.current_filter(x)))
            elif self.filter_combobox.currentIndex() == 4:
                self.note_list.current_filter = lambda x: x['note'] <\
                    float(text) and x['hidden'] == 0
                self.note_list.rebuild(api.notes.get(
                    lambda x: self.note_list.custom_filter(x) and self.note_list.current_filter(x)))
        except ValueError:
            self.note_list.clear()

    def search_input_changed(self, event):
        """ Called when the search input is changed
        """
        self.note_list.hide_unmatched_items(self.search_input.text())

    def __getattr__(self, attr):
        try:
            return self.__dict__[attr]
        except:
            return getattr(self.note_list, attr)

    def on_selection_changed(self):
        self.itemSelectionChanged.emit()

    def search_input_validated(self):
        if self.note_list.nb_shown == 1:
            item = self.note_list.itemAt(1, 1)  # Hideous hack to get the first visible item
            self.note_list.setCurrentItem(item, QtCore.QItemSelectionModel.Toggle)
