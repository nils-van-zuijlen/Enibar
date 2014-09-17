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
Validation prompt
====================

"""


from PyQt5 import QtWidgets, uic


class ValidPrompt(QtWidgets.QDialog):
    """ Validation prompt class """
    def __init__(self, text, enabled=True):
        super().__init__()
        if enabled:
            self.is_ok = False
            uic.loadUi('ui/validprompt.ui', self)
            self.content.setText(text)
            self.exec()
        else:
            self.is_ok = True

    def accept(self):
        """ Called when "Valider" is clicked """
        self.is_ok = True
        return super().accept()

