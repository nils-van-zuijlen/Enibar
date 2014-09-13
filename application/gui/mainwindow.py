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

from .auth_prompt import ask_auth
from .validation_window import ValidPrompt
from .consumptionmanagment import ConsumptionManagmentWindow
from .douchette import Douchette
from .emptynote import EmptyNote
from .manage_notes import ManageNotes
from .notesaction import NotesAction
from .panelmanagment import PanelManagment
from .passwordmanagment import PasswordManagment
from .refillnote import RefillNote
from .transactionhistory import TransactionHistory
from .usermanagment import UserManagmentWindow
import api.categories
import api.notes
import api.transactions
import datetime
import gui.utils
import settings
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
        self.selected_nickname = None
        self.win = None
        self.eco_diff = 0

        # Set product list header width
        self.product_list.setColumnWidth(0, 30)
        self.product_list.setColumnWidth(1, 128)
        self.product_list.setColumnWidth(2, 40)

        self.panels.build()

    def select_note(self, index):
        """
        Called when a note is selected
        """
        self.note_box.setEnabled(True)
        self.refill_note.setEnabled(True)
        self.empty_note.setEnabled(True)
        if index >= 0:
            self.selected = self.notes_list.item(index)
        widget = self.notes_list.currentItem()

        if self.selected_nickname != self.selected.text():
            self.selected_nickname = self.selected.text()
            self.refresh_ecocups()

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
            self.empty_note.setEnabled(False)
            self.note_box.setEnabled(False)
            return

        infos = list(api.notes.get(lambda x: widget.text() == x["nickname"]))[0]
        # pylint: disable=star-args
        self.note_name.setText("{nickname} - {firstname} {lastname}".format(
            **infos))
        self.note_mail.setText(infos['mail'])
        self.note_solde.setText("{:.2f} €".format(infos['note']))
        self.note_promo.setText(infos['promo'])
        self.note_phone.setText(infos['tel'])

        if infos['photo_path']:
            path = settings.IMG_BASE_DIR + '/' + infos['photo_path']
            image = QtGui.QPixmap(path)
        else:
            image = QtGui.QPixmap("")
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

    def refresh_ecocups(self):
        """ Set the state of the repay_ecocup button
        """
        note = api.notes.get(lambda x: x["nickname"] == self.selected_nickname)
        if list(note)[0]["ecocups"] + self.eco_diff > 0:
            self.repay_ecocup_btn.setEnabled(True)
        else:
            self.repay_ecocup_btn.setEnabled(False)

    def refresh(self):
        """ Refresh the notes list
        """
        self.notes_list.refresh(api.notes.get(lambda x: x['hidden'] == 0))

    def event(self, event):
        """ Rewrite the event loop
        """
        if isinstance(event, QtGui.QKeyEvent) and\
                event.type() == QtCore.QEvent.KeyPress:
            if event.text() == "\"":
                self.win = Douchette(self.on_douchette)
                return True
            if event.key() == 0x01000004 or event.key() == 0x01000005:
                self.validate_transaction()
        return super().event(event)

    def on_douchette(self, text):
        """ Called after the douchette is fired !
        """
        product = api.products.get_unique(barcode=text)
        if not product:
            return
        catname = api.categories.get_unique(id=product["category"])
        if not catname:
            return
        prices = list(api.prices.get(product=product["id"]))
        if not prices:
            return
        if not len(product):
            return
        self.product_list.add_product(
            catname["name"],
            product["name"],
            prices[0]["label"],
            prices[0]["value"])
        text = "{:.2f} €".format(self.product_list.get_total())
        self.total.setText(text)

    def validate_transaction(self):
        """ Validate transaction
        """
        total = self.product_list.get_total()
        text = "Es tu sûr de vouloir enlever {} € sur la note\
                \nde {}".format(total, self.selected.text())
        prompt = ValidPrompt(text)
        if not prompt.is_ok:
            return
        if self.selected:
            transactions = []
            for product in self.product_list.products:
                transaction = {
                    'note': self.selected.text(),
                    'category': product['category'],
                    'product': product['product'],
                    'price_name': product['price_name'],
                    'quantity': product['count'],
                    'price': -product['price']
                }
                transactions.append(transaction)
            if api.transactions.log_transactions(transactions):
                api.notes.transaction(self.selected.text(), -total)
                api.notes.change_ecocups(self.selected_nickname, self.eco_diff)
                self.refresh()
                self.eco_diff = 0
                self.refresh_ecocups()
                self.product_list.clear()
                self.notes_list.setFocus()
            else:
                gui.utils.error('Impossible de valider la transaction')


class MenuBar(QtWidgets.QMenuBar):
    """ MainWindow menu bar """
    # pylint: disable=too-many-public-methods
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

    @ask_auth("manage_users")
    def user_managment_fnc(self, _):
        """ Call user managment window """
        self.cur_window = UserManagmentWindow()
        self._connect_window()

    @ask_auth("manage_products")
    def consumption_managment_fnc(self, _):
        """ Call consumption managment window """
        self.cur_window = ConsumptionManagmentWindow()
        self.cur_window.finished.connect(self.parent().panels.rebuild)
        self._connect_window()

    @ask_auth("manage_notes")
    def manage_note_fnc(self, _):
        """ Open an ManageNotes window
        """
        self.cur_window = ManageNotes(self.parent())
        self._connect_window()

    def export_notes_with_profs_fnc(self, _):
        """ Export all notes """
        self.export(api.notes.get())

    def export_notes_without_profs_fnc(self, _):
        """ Export only students notes """
        self.export(api.notes.get(lambda x: x["promo"] != "Prof"))

    def change_password_fnc(self, _):
        """ Open a PasswordManagment window
        """
        self.cur_window = PasswordManagment()
        self._connect_window()

    @ask_auth("manage_products")
    def panel_managment_fnc(self, _):
        """ Open a PanelManagment window
        """
        self.cur_window = PanelManagment()
        self.cur_window.finished.connect(self.parent().panels.rebuild)
        self._connect_window()

    @ask_auth("manage_notes")
    def notes_action_fnc(self, _):
        """ Open a NotesAction window
        """
        self.cur_window = NotesAction()
        self._connect_window()

    @ask_auth("manage_notes")
    def refill_note_fnc(self, _):
        """ Open a RefillNote window
        """
        self.cur_window = RefillNote(
            self.parent().notes_list.currentItem().text())
        self._connect_window()

    def empty_note_fnc(self, _):
        """ Open a EmptyNote window
        """
        self.cur_window = EmptyNote(
            self.parent().notes_list.currentItem().text())
        self._connect_window()

    def take_ecocup_fnc(self):
        """ Used to take an ecocup on a note
        """
        self.parent().product_list.add_product(
            "Bar",
            "Ecocup",
            "Achat",
            settings.ECOCUP_PRICE
        )
        text = "{:.2f} €".format(self.parent().product_list.get_total())
        self.parent().total.setText(text)
        self.parent().eco_diff += 1
        self.parent().refresh_ecocups()

    def repay_ecocup_fnc(self):
        """ Used to repay an ecocup on a note
        """
        self.parent().product_list.add_product(
            "Bar",
            "Ecocup",
            "Remboursement",
            -settings.ECOCUP_PRICE
        )
        text = "{:.2f} €".format(self.parent().product_list.get_total())
        self.parent().total.setText(text)
        self.parent().eco_diff -= 1
        self.parent().refresh_ecocups()

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

    def show_transactions_history(self):
        """ Show transaction logs
        """
        self.cur_window = TransactionHistory(self)
        self._connect_window()

