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

from .add_note import AddNote
from .panelmanagment import PanelManagment
from .passwordmanagment import PasswordManagment
from .consumptionmanagment import ConsumptionManagmentWindow
from .usermanagment import UserManagmentWindow
import api.notes
import datetime
import settings
import time


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
        self.note_box.setEnabled(True)
        widget = self.notes_list.currentItem()
        if not widget:
            return
        infos = list(api.notes.get(lambda x: widget.text() in x["nickname"]))[0]
        self.note_name.setText("{nickname} - {firstname} {lastname}".format(
            nickname=infos['nickname'],
            firstname=infos['firstname'],
            lastname=infos['lastname']
        ))
        self.note_mail.setText(infos['mail'])
        self.note_solde.setText("{:.2f} €".format(infos['note']))
        self.note_promo.setText(infos['promo'])
        self.note_phone.setText(infos['tel'])

        image = QtGui.QPixmap('img/coucou.jpg')
        if not image.isNull():
            self.note_photo.setPixmap(image.scaled(QtCore.QSize(120, 160), 1))
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
        self.refresh_timer = QtCore.QTimer(self)
        self.refresh_timer.setInterval(10 * 1000)  # 10 seconds
        self.refresh_timer.timeout.connect(self.on_timer)
        self.refresh_timer.start()
        self.minors_color = settings.MINORS_COLOR
        self.overdraft_color = settings.OVERDRAFT_COLOR

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

    def on_timer(self):
        """ Rebuild the note list every 10 seconds
        """
        api.notes.rebuild_cache()
        self.refresh(api.notes.get(lambda x: x['hidden'] == 0))

    def clean(self):
        """ Clean the note list
        """
        for i in reversed(range(self.count())):
            self.takeItem(i)

    def refresh(self, notes_list):
        """ Refresh the note list
        """
        selected = self.currentRow()
        self.clean()
        self.build(notes_list)
        self.setCurrentRow(selected)


class MenuBar(QtWidgets.QMenuBar):
    """ MainWindow menu bar """
    def __init__(self, parent):
        super().__init__(parent)
        self.cur_window = None

    def user_managment_fnc(self):
        """ Call user managment window """
        self.cur_window = UserManagmentWindow()

    def consumption_managment_fnc(self):
        """ Call consumption managment window """
        # Java style
        self.cur_window = ConsumptionManagmentWindow()

    def add_note_fnc(self):
        """ Open an AddNote window
        """
        self.cur_window = AddNote(self.parent())

    def export_notes_with_profs_fnc(self):
        """ Export all notes """
        self.export(api.notes.get())

    def export_notes_without_profs_fnc(self):
        """ Export only students notes """
        self.export(api.notes.get(lambda x: x["promo"] != "Prof"))

    def change_password_fnc(self):
        """ Open a PasswordManagment window
        """
        self.cur_window = PasswordManagment()

    def panel_managment_fnc(self):
        """ Open a PanelManagment window
        """
        self.cur_window = PanelManagment()

    def export(self, notes):
        """ Generic export notes function """
        path = QtWidgets.QFileDialog(self).getSaveFileName(
            self, "Exporter vers", "{}.xml".format(
                datetime.datetime.now().strftime("%Y-%m-%d")),
            "XML Files (*.xml)")[0]

        if path:
            with open(path, "w") as save_file:
                save_file.write(api.notes.export(notes))

