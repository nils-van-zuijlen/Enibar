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
EmptyNote Window
====================


"""


from PyQt5 import QtWidgets, QtCore, uic

import api.notes
import api.transactions
import api.validator
import gui.utils
import gui.input


class EmptyNote(QtWidgets.QDialog):
    """ EmptyNote window class """
    def __init__(self, selected_note):
        super().__init__()
        uic.loadUi('ui/refill_note.ui', self)
        self.to_add.set_validator(api.validator.NUMBER)
        self.to_add.setFocus()
        self.reason_input = gui.input.Input(self)
        self.reason_input.set_validator(api.validator.NAME)
        self.reason_input.setPlaceholderText("Raison")
        self.main_layout.addWidget(self.reason_input, 1, 0)
        self.setWindowTitle("Prendre d'une note")
        self.selected_note = selected_note
        self.to_add.setLocale(QtCore.QLocale('English'))

        self.show()
        self.to_add.selectAll()

    def accept(self):
        """ Called when "Enlever" is clicked
        """
        to_add = float(self.to_add.text().replace(',', '.'))
        if to_add > 0:
            api.notes.transaction(self.selected_note, -to_add)
            api.transactions.log_transaction(
                self.selected_note,
                "Note",
                self.reason_input.text(),
                "Solde",
                "1",
                -to_add
            )
            super().accept()
        else:
            gui.utils.error("Erreur", "La valeur à enlever doit etre positive")

    def on_change(self):
        if self.to_add.valid:
            self.valid_button.setEnabled(True)
        else:
            self.valid_button.setEnabled(False)
