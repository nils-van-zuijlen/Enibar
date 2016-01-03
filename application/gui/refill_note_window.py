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
RefillNote Window
====================


"""


from PyQt5 import QtWidgets, uic

import api.notes
import api.transactions
import api.validator
import gui.utils
from .validation_window import ValidationWindow
import settings


class RefillNoteWindow(QtWidgets.QDialog):
    """ RefillNote window class """
    def __init__(self, selected_note, performer):
        super().__init__()
        uic.loadUi('ui/refill_note_window.ui', self)
        self.selected_note = selected_note
        self.to_add.set_validator(api.validator.NUMBER)
        self.reason.set_validator(api.validator.NOTHING)
        self.to_add.setFocus()
        self.performer = performer

        self.show()
        self.to_add.selectAll()

    def accept(self):
        """ Called when "Ajouter" is clicked
        """
        to_add = float(self.to_add.text().replace(',', '.'))
        # See #96
        if not round(to_add, 2) > 0:
            gui.utils.error("Erreur", "La valeur à ajouter doit etre superieur à\
                0.01€")
            return

        prompt = ValidationWindow("Etes vous sûr de vouloir ajouter {} € sur la note\
            \nde {}".format(self.to_add.text(), self.selected_note),
            settings.ASK_VALIDATION_REFILL)
        if not prompt.is_ok:
            return
        reason = self.reason.text()
        api.notes.transactions([self.selected_note, ], to_add)
        api.transactions.log_transaction(
            self.selected_note,
            "Note",
            "{} {}".format(self.performer, "[{}]".format(reason) if reason else ""),
            "Rechargement",
            "1",
            to_add
        )
        super().accept()

    def on_change(self):
        """ Set state of the validation button.
        """
        if self.to_add.valid:
            self.valid_button.setEnabled(True)
        else:
            self.valid_button.setEnabled(False)


class MultiRefillNoteWindow(QtWidgets.QDialog):
    """ A window that ask for a value to add and set it as a variable instead
        of adding it to the notes. It's used to add money on multiple notes.
    """
    def __init__(self, performer, text="ajouter"):
        super().__init__()
        uic.loadUi('ui/refill_note_window.ui', self)
        self.performer = performer
        self.to_add.set_validator(api.validator.NUMBER)
        self.reason.set_validator(api.validator.NOTHING)
        self.to_add.setFocus()
        self.to_add_value = 0
        self.reason_value = ""
        self.text = text

        self.show()

    def accept(self):
        """ Called when "Ajouter" is clicked
        """
        to_add = float(self.to_add.text().replace(',', '.'))
        if round(to_add, 2) < 0.01:
            gui.utils.error("Erreur", "La valeur à ajouter doit etre superieur à\
                0.01€")
            return
        prompt = ValidationWindow("Etes vous sûr de vouloir {} {} € sur les\
            \nnotes selectionées".format(self.text, self.to_add.text()),
            settings.ASK_VALIDATION_REFILL)
        if not prompt.is_ok:
            return
        self.to_add_value = to_add
        self.reason_value = self.reason.text()
        super().accept()

    def on_change(self):
        """ Set state of the validation button
        """
        if self.to_add.valid and self.reason.valid:
            self.valid_button.setEnabled(True)
        else:
            self.valid_button.setEnabled(False)
