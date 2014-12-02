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
Douchette Window
====================


"""


from PyQt5 import QtWidgets, uic, QtGui

EQUIVALENCE_TABLE = {"&": 1, "é": 2, "\"": 3, "'": 4, "(": 5,
                     "-": 6, "è": 7, "_": 8, "ç": 9, "à": 0, ")": "-"}


class DouchetteWindow(QtWidgets.QDialog):
    """ Douchette window class """
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        uic.loadUi('ui/douchette_window.ui', self)
        self.show()
        self.equivalence_table = {"&": 1, "é": 2, "\"": 3, "'": 4, "(": 5,
                                  "-": 6, "è": 7, "_": 8, "ç": 9, "à": 0}

    def accept(self):
        """ Called when "Valider" is clicked
        """
        self.callback(self.content_input.text())
        super().accept()

    def event(self, event):
        """ Rewrite the events loop
        """
        if isinstance(event, QtGui.QKeyEvent):
            try:
                if self.content_input.hasFocus():
                    char = str(EQUIVALENCE_TABLE[event.text()])
                    text = self.content_input.text()[:-1]
                    self.content_input.setText(text + char)
                    event.accept()
                    return True
            except KeyError:
                pass
        return super().event(event)

