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
NotesAction Window
====================


"""


from PyQt5 import QtWidgets, uic

import api.notes
from .utils import NotesList


class NotesAction(QtWidgets.QDialog):
    # pylint: disable=too-many-instance-attributes, too-many-public-methods
    """ NotesAction window class """
    def __init__(self):
        super().__init__()
        self.current_filter = lambda x: x['hidden'] == "0"
        uic.loadUi('ui/notesaction.ui', self)
        self.show()

    def del_action(self, _):
        """ Called when "Supprimer" is clicked
        """
        indexes = self.note_list.selectedIndexes()
        to_del = []
        for index in reversed(indexes):
            to_del.append(index.data())
            self.note_list.takeItem(index.row())
        api.notes.remove_multiple(api.notes.get_notes_id(to_del))
        self.note_list.rebuild(api.notes.get(self.current_filter))

    def _multiple_action(self, fnc):
        """ Execute a function on the currently selected notes
        """
        indexes = self.note_list.selectedIndexes()
        notes_id = []
        for index in indexes:
            notes_id.append(index.data())
        fnc(api.notes.get_notes_id(notes_id))
        self.note_list.rebuild(api.notes.get(self.current_filter))

    def filter_combobox_change(self, id_):
        print(api.notes.get()[0]['note'] > 0)
        if id_ == 0:
            self.current_filter = lambda x: x['hidden'] == 0
        elif id_ == 1:
            self.current_filter = lambda x: x['hidden'] == 1
        elif id_ == 2:
            self.current_filter = lambda x: x['note'] > 0
        elif id_ == 3:
            self.current_filter = lambda x: x['note'] < 0
        self.note_list.rebuild(api.notes.get(self.current_filter))

    def hide_action(self):
        """ Called when "cacher" is clicked
        """
        self._multiple_action(api.notes.hide_multiple)

    def show_action(self):
        """ Called when "Montrer" is clicked
        """
        self._multiple_action(api.notes.show_multiple)


class MultiNotesList(NotesList):
    # pylint: disable=too-many-public-methods
    """ List of notes with multi-selection
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.build(api.notes.get())

    def rebuild(self, notes_list):
        """ Just rebuild the notes list
        """
        print(notes_list)
        self.clean()
        self.build(notes_list)


