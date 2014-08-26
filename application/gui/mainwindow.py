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

from PyQt5 import QtCore, QtGui, QtWidgets, uic

from .manage_notes import ManageNotes
from .consumptionmanagment import ConsumptionManagmentWindow
from .notesaction import NotesAction
from .panelmanagment import PanelManagment
from .passwordmanagment import PasswordManagment
from .usermanagment import UserManagmentWindow
from .refillnote import RefillNote
import api.notes
import datetime
import time


class MainWindow(QtWidgets.QMainWindow):
    """
    Main Window
    """
    notes_list = None

    def __init__(self):
        super().__init__()
        uic.loadUi('ui/mainwindow.ui', self)

        self.refresh()
        self.notes_list.currentRowChanged.connect(self.select_note)
        self.selected = None

        # Set product list header width
        self.product_list.setColumnWidth(0, 60)
        self.product_list.setColumnWidth(1, 130)
        self.product_list.setColumnWidth(2, 50)

    def select_note(self, index):
        """
        Called when a note is selected
        """
        self.note_box.setEnabled(True)
        self.refill_note.setEnabled(True)
        if index >= 0:
            self.selected = self.notes_list.item(index)
        widget = self.notes_list.currentItem()

        # If there are no current selected note.
        if not widget:
            self.note_name.setText("Surnom - Prénom nom")
            self.note_mail.setText("email@enib.fr")
            self.note_promo.setText("Promo")
            self.note_phone.setText("+336 00 00 00 00")
            self.note_solde.setText("0.00 €")
            image = QtGui.QPixmap()
            self.note_photo.setPixmap(image)
            self.note_box.setStyleSheet("background-color: none;")
            self.refill_note.setEnabled(False)
            self.note_box.setEnabled(False)
            return

        infos = list(api.notes.get(lambda x: widget.text() in x["nickname"]))[0]
        # pylint: disable=star-args
        self.note_name.setText("{nickname} - {firstname} {lastname}".format(
            **infos))
        self.note_mail.setText(infos['mail'])
        self.note_solde.setText("{:.2f} €".format(infos['note']))
        self.note_promo.setText(infos['promo'])
        self.note_phone.setText(infos['tel'])

        if infos['photo_path']:
            image = QtGui.QPixmap(infos['photo_path'])
        else:
            image = QtGui.QPixmap("img/coucou.jpg")
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

    def refresh(self):
        """ Refresh the notes list
        """
        self.notes_list.refresh(api.notes.get(lambda x: x['hidden'] == 0))

    def validate_transaction(self):
        """ Validate transaction
        """
        if self.selected:
            total = self.product_list.get_total()
            api.notes.transaction(self.selected.text(), -total)
            self.refresh()
            self.product_list.clear()


class MenuBar(QtWidgets.QMenuBar):
    """ MainWindow menu bar """
    def __init__(self, parent):
        super().__init__(parent)
        self.cur_window = None

    def _refresh_parent(self):
        """ Refresh the parent
        """
        self.parent().refresh()

    def _connect_window(self):
        """ Connect the finished signal of the opened window to
            refresh_parent
        """
        self.cur_window.finished.connect(self._refresh_parent)

    def user_managment_fnc(self):
        """ Call user managment window """
        self.cur_window = UserManagmentWindow()
        self._connect_window()

    def consumption_managment_fnc(self):
        """ Call consumption managment window """
        self.cur_window = ConsumptionManagmentWindow()
        self.cur_window.finished.connect(self.parent().panels.rebuild)
        self._connect_window()

    def manage_note_fnc(self):
        """ Open an ManageNotes window
        """
        self.cur_window = ManageNotes(self.parent())
        self._connect_window()

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
        self._connect_window()

    def panel_managment_fnc(self):
        """ Open a PanelManagment window
        """
        self.cur_window = PanelManagment()
        self.cur_window.finished.connect(self.parent().panels.rebuild)
        self._connect_window()

    def notes_action_fnc(self):
        """ Open a NotesAction window
        """
        self.cur_window = NotesAction()
        self._connect_window()

    def refill_note_fnc(self):
        """ Open a RefillNote window
        """
        self.cur_window = RefillNote(
            self.parent().notes_list.currentItem().text())
        self._connect_window()

    def take_ecocup_fnc(self):
        """ Used to take an ecocup on a note
        """
        self.parent().product_list.add_product(
            "Bar",
            "Ecocup",
            "Achat",
            2
        )
        text = "{:.2f} €".format(self.parent().product_list.get_total())
        self.parent().total.setText(text)

    def repay_ecocup_fnc(self):
        """ Used to repay an ecocup on a note
        """
        self.parent().product_list.add_product(
            "Bar",
            "Ecocup",
            "Remboursement",
            -2
        )
        text = "{:.2f} €".format(self.parent().product_list.get_total())
        self.parent().total.setText(text)

    def export(self, notes):
        """ Generic export notes function """
        path, format_ = QtWidgets.QFileDialog(self).getSaveFileName(
            self, "Exporter vers", "{}.xml".format(
                datetime.datetime.now().strftime("%Y-%m-%d")),
            "XML Files (*.xml)\nCSV Files (*.csv)")

        if path:
            with open(path, "w") as save_file:
                if format_ == "XML Files (*.xml)":
                    save_file.write(api.notes.export(notes, xml=True))
                else:
                    save_file.write(api.notes.export(notes, csv=True))

