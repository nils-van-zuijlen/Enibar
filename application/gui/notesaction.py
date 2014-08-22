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


class MultiNotesList(NotesList):
    # pylint: disable=too-many-public-methods
    """ List of notes with multi-selection
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.build(api.notes.get())


