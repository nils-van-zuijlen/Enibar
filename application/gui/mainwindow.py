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
Main Window description
"""

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import uic

import api.notes
import time
from .add_note import AddNote
import gui.usermanagment
import gui.consumptionmanagment


class MainWindow(QtWidgets.QMainWindow):
    """
    Main Window
    """
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/mainwindow.ui', self)

        self.notes_list.refresh(api.notes.get(lambda x: x['hidden'] == 0))
        self.notes_list.currentRowChanged.connect(self.select_note)

    def select_note(self):
        """
        Called when a note is selected
        """
        widget = self.notes_list.currentItem()
        infos = list(api.notes.get(lambda x: widget.text() in x["nickname"]))[0]
        self.note_name.setText(widget.text())
        self.note_mail.setText(infos['mail'])
        self.note_solde.setText("{:.2f} €".format(infos['note']))
        self.note_promo.setText(infos['promo'])
        self.note_phone.setText(infos['tel'])

        image = QtGui.QPixmap('img/coucou.jpg')
        if not image.isNull():
            self.note_photo.setPixmap(image.scaled(QtCore.QSize(120, 160)))
        else:
            self.note_photo.setPixmap(image)

        if infos['note'] < 0:
            self.note_box.setStyleSheet("background-color: red;")
        elif time.time() - infos['birthdate'] < 18 * 365 * 24 * 3600:
            self.note_box.setStyleSheet("background-color: pink;")
        else:
            self.note_box.setStyleSheet("background-color: none;")


class NotesList(QtWidgets.QListWidget):
    # pylint: disable=too-many-public-methods
    """ Notes list on the left of the MainWindow. """
    def __init__(self, parent):
        super().__init__(parent)
        self.notes = []

    def refresh(self, notes_list):
        """ Fill the list with notes from notes_list, coloring negatives one
            in red """
        self.notes = []
        for note in notes_list:
            self.notes.append(QtWidgets.QListWidgetItem(
                note["nickname"], self))
            if note['note'] < 0:
                self.notes[-1].setBackground(QtCore.Qt.red)
            elif time.time() - note["birthdate"] < 18 * 365 * 24 * 3600:
                self.notes[-1].setBackground(QtGui.QColor(255, 192, 203))

        if len(self.notes):
            self.notes[0].setSelected(True)


class MenuBar(QtWidgets.QMenuBar):
    """ MainWindow menu bar """
    def __init__(self, parent):
        super().__init__(parent)
        self.cm_window = None
        self.um_window = None
        self.an_window = None

    def user_managment(self):
        """ Call user managment window """
        self.um_window = gui.usermanagment.UserManagmentWindow()

    def consumption_managment(self):
        """ Call consumption managment window """
        # Java style
        self.cm_window = gui.consumptionmanagment.ConsumptionManagmentWindow()

    def add_note(self):
        """ Open an AddNote window
        """
        self.an_window = AddNote()

