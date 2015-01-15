# Copyright (C) 2014-2015 Bastien Orivel <b2orivel@enib.fr>
# Copyright (C) 2014-2015 Arnaud Levaufre <a2levauf@enib.fr>
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
Main Window
===========

The MainWindow class is the main class of the program.

"""

from PyQt5 import QtCore, QtGui, QtWidgets, uic

from .auth_prompt_window import ask_auth
from .validation_window import ValidationWindow
from .products_management_window import ProductsManagementWindow
from .douchette_window import DouchetteWindow
from .empty_note_window import EmptyNoteWindow
from .notes_management_window import NotesManagementWindow
from .group_actions_window import GroupActionsWindow
from .panels_management_window import PanelsManagementWindow
from .password_management_window import PasswordManagementWindow
from .refill_note_window import RefillNoteWindow
from .history_window import HistoryWindow
from .users_management_window import UsersManagementWindow
from .search_window import SearchWindow
from .stats_window import StatsWindow
from .about_window import AboutWindow
from .csv_import_window import CsvImportWindow
import api.categories
import api.notes
import api.transactions
import datetime
import gui.utils
import settings
import time


class MainWindow(QtWidgets.QMainWindow):
    """Main Window
    """

    def __init__(self):
        super().__init__()
        uic.loadUi('ui/main_window.ui', self)

        # The QListWidget item currently selected.
        self.selected = None

        # The nickname of th currently selected note.
        self.selected_nickname = None

        # Timer used to add a delay when selecting a note.
        self.timer = None

        # The secondary window currently opened. It' here to force having only
        # one window opened at a time.
        self.win = None

        # Hack to count ecocups to add/delete.
        self.eco_diff = 0

        # Build the notes_list
        self.rebuild_notes_list()

        # Set product list header width
        self.product_list.setColumnWidth(0, 30)
        self.product_list.setColumnWidth(1, 128)
        self.product_list.setColumnWidth(2, 40)

        # Build the panels.
        self.panels.build()

        # Set the headers of the history in the note details.
        self.note_history.header().setStretchLastSection(False)
        self.note_history.header().setSectionResizeMode(
            2,
            QtWidgets.QHeaderView.Stretch
        )

    def on_note_selection(self, index):
        """ Called when a note is selected
            Rebuild the timer so it stays unique. Then call self.refresh_note
            100ms later if not called again.
        """
        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)

        def refresh():
            """ We need that to pass index to self._note_refresh
            """
            self._note_refresh(index)
        self.timer.timeout.connect(refresh)
        self.timer.start()

    def reset_note_box(self):
        """ Reset the note box to default
        """
        self.note_name.setText("Surnom - Prénom nom")
        self.note_mail.setText("email@enib.fr")
        self.note_promo.setText("Promo")
        self.note_phone.setText("+336 00 00 00 00")
        self.note_solde.setText("0.00 €")
        self.total_cons.setText("0.00 €")
        self.total_refill.setText("0.00€")
        image = QtGui.QPixmap()
        self.note_photo.setPixmap(image)
        self.note_box.setStyleSheet("background-color: none;")
        self.refill_note.setEnabled(False)
        self.empty_note.setEnabled(False)
        self.note_box.setEnabled(False)
        self.repay_ecocup_btn.setEnabled(False)
        self.take_ecocup_btn.setEnabled(False)

    def _note_refresh(self, index):
        """ Build the note infos.
        """
        # Stop the timer so it doesn't refresh the note every 100ms
        if self.timer:
            self.timer.stop()

        # Enable the right box and clear the history.
        self.note_box.setEnabled(True)
        self.refill_note.setEnabled(True)
        self.empty_note.setEnabled(True)
        # We need that beaucause of #114
        self.take_ecocup_btn.setEnabled(True)

        self.note_history.clear()
        if index >= 0:
            self.selected = QtWidgets.QListWidgetItem(self.notes_list.item(index))
        else:
            self.reset_note_box()
            return

        if self.selected_nickname != self.selected.text():
            self.selected_nickname = self.selected.text()
            self.refresh_ecocup_button()

        # If there are no current selected note, set the default text and diable
        # everything
        if not self.selected:
            self.reset_note_box()
            return

        infos = api.notes.get(
            lambda x: self.selected.text() == x["nickname"]
        )
        if infos:
            infos = infos[0]
        note_hist = api.transactions.get_reversed(note=self.selected.text())

        # Construct the note history
        for i, product in enumerate(note_hist):
            if i > settings.MAX_HISTORY:
                break
            name = "{} ({}) - {}".format(product['product'],
                                         product['price_name'],
                                         product['category'])
            widget = QtWidgets.QTreeWidgetItem(
                [product['date'].toString("yyyy/MM/dd HH:mm:ss"),
                 str(product['quantity']),
                 name,
                 str(-product['price'])
                ]
            )
            self.note_history.addTopLevelItem(widget)
        self.note_history.resizeColumnToContents(0)
        self.note_history.resizeColumnToContents(1)

        self.note_name.setText("{nickname} - {firstname} {lastname}".format(
            **infos))
        self.note_mail.setText(infos['mail'])
        self.note_solde.setText("{:.2f} €".format(infos['note']))
        self.total_cons.setText("{:.2f} €".format(-infos['tot_cons']))
        self.total_refill.setText("{:.2f} €".format(infos['tot_refill']))
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

    def refresh_ecocup_button(self):
        """ Set the state of the repay_ecocup button depending on self.eco_diff
        """
        note = api.notes.get(lambda x: x["nickname"] == self.selected_nickname)
        if list(note)[0]["ecocups"] + self.eco_diff > 0:
            self.repay_ecocup_btn.setEnabled(True)
        else:
            self.repay_ecocup_btn.setEnabled(False)

    def rebuild_notes_list(self):
        """ Rebuild the notes list with only the shown notes.
        """
        self.notes_list.refresh(api.notes.get(lambda x: x['hidden'] == 0))
        self._note_refresh(self.notes_list.currentRow())

    def event(self, event):
        """ Rewrite the event loop. Used to handle the douchette and the \n key
            If the " key is pressed, open a Douchette window. If the \n key is
            pressed, call self.validate_transaction.
        """
        if isinstance(event, QtGui.QKeyEvent) and\
                event.type() == QtCore.QEvent.KeyPress:
            if event.text() == "\"":
                self.win = DouchetteWindow(self.on_douchette)
                return True
            if event.key() == QtCore.Qt.Key_Return or\
                    event.key() == QtCore.Qt.Key_Enter:
                self.validate_transaction()
        return super().event(event)

    def on_douchette(self, text):
        """ Called after the douchette is fired !
        """
        price = api.prices.get_unique(barcode=text)
        if not price:
            return
        catname = api.categories.get_unique(id=price["category"])
        if not catname:
            return
        product = api.products.get_unique(id=price["product"])
        if not product:
            return
        self.product_list.add_product(
            catname["name"],
            product["name"],
            price["label"],
            price["value"])
        text = "{:.2f} €".format(self.product_list.get_total())
        self.total.setText(text)

    def validate_transaction(self):
        """ Validate transaction if a note is currently selected. And give the
            focus back to the notes_list.
        """
        if self.selected and self.product_list.products:

            note = api.notes.get(lambda x: x["nickname"] ==
                self.selected_nickname)[0]
            if note['ecocups'] < -self.eco_diff:
                gui.utils.error("Erreur", "Verifiez le nombre d'écocups.")
                return
            total = self.product_list.get_total()
            text = "Es tu sûr de vouloir enlever {:.2f} € sur la note\
                    <br/>de {}<br/><br/><span style=\"font-size:12pt;\
                    font-weight:600; color:#ff0000;\">NE PAS OUBLIER LES\
                    ECOCUPS !!!!</span>".format(total, self.selected.text())
            prompt = ValidationWindow(text, settings.ASK_VALIDATION_VALIDATE)
            if not prompt.is_ok:
                return
            transactions = []
            for product in self.product_list.products:
                transaction = {
                    'note': self.selected.text(),
                    'category': product['category'],
                    'product': product['product'],
                    'price_name': product['price_name'],
                    'quantity': product['count'],
                    'price': -product['price'],
                    'deletable': product['deletable']
                }
                transactions.append(transaction)
            if api.transactions.log_transactions(transactions):
                api.notes.transactions([self.selected.text(), ], -total,
                    do_not=True)
                api.notes.change_ecocups(self.selected_nickname, self.eco_diff)
                self.rebuild_notes_list()
                self.eco_diff = 0
                self.refresh_ecocup_button()
                self.product_list.clear()
                self.notes_list.setFocus()
            else:
                gui.utils.error('Impossible de valider la transaction')


class MenuBar(QtWidgets.QMenuBar):
    """ MainWindow menu bar """
    def __init__(self, parent):
        super().__init__(parent)
        self.cur_window = None

    def _refresh_parent(self):
        """ Refresh the parent
        """
        self.parent().notes_list.current_filter = lambda x: x['hidden'] == 0
        self.parent().rebuild_notes_list()
        self._close_window()

    def _connect_window(self):
        """ Connect the finished signal of the opened window to
            refresh_parent
        """
        self.cur_window.finished.connect(self._refresh_parent)

    def _close_window(self):
        """ Close the current open window
        """
        if self.cur_window is not None:
            self.cur_window.close()

    @ask_auth("manage_users")
    def user_managment_fnc(self, _):
        """ Call user managment window """
        self._close_window()
        self.cur_window = UsersManagementWindow()
        self._connect_window()

    @ask_auth("manage_products")
    def consumption_managment_fnc(self, _):
        """ Call consumption managment window """
        self._close_window()
        self.cur_window = ProductsManagementWindow()
        self.cur_window.finished.connect(self.parent().panels.rebuild)
        self._connect_window()

    @ask_auth("manage_notes")
    def manage_note_fnc(self, _):
        """ Open an ManageNotes window
        """
        self._close_window()
        self.cur_window = NotesManagementWindow(self.parent())
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
        self._close_window()
        self.cur_window = PasswordManagementWindow()
        self._connect_window()

    @ask_auth("manage_products")
    def panel_managment_fnc(self, _):
        """ Open a PanelManagment window
        """
        self._close_window()
        self.cur_window = PanelsManagementWindow()
        self.cur_window.finished.connect(self.parent().panels.rebuild)
        self._connect_window()

    @ask_auth("manage_notes", pass_performer=True)
    def notes_action_fnc(self, _, _performer=""):
        """ Open a NotesAction window
        """
        self._close_window()
        self.cur_window = GroupActionsWindow(_performer)
        self._connect_window()

    @ask_auth("manage_notes", pass_performer=True)
    def refill_note_fnc(self, _, _performer=""):
        """ Open a RefillNote window
        """
        self._close_window()
        self.cur_window = RefillNoteWindow(
            self.parent().notes_list.currentItem().text(), performer=_performer)
        self._connect_window()

    @ask_auth("manage_notes")
    def csv_import_fnc(self, _):
        """ Open a CsvImportWindow
        """
        self._close_window()
        path, _ = QtWidgets.QFileDialog(self).getOpenFileName(
            self,
            "Imported",
            "",
            "CSV Files (*.csv)"
        )

        if path:
            self.cur_window = CsvImportWindow(path)
            self._connect_window()

    def about(self):
        """ Open an AboutWindow
        """
        self._close_window()
        self.cur_window = AboutWindow()
        self._connect_window()

    def refresh_panels_fnc(self, _):
        """ Refresh the panels of the main window.
        """
        self.parent().panels.rebuild()

    def empty_note_fnc(self, _):
        """ Open a EmptyNote window
        """
        self._close_window()
        self.cur_window = EmptyNoteWindow(
            self.parent().notes_list.currentItem().text())
        self._connect_window()

    def take_ecocup_fnc(self):
        """ Used to take an ecocup on a note
        """
        self.parent().product_list.add_product(
            settings.ECOCUP_CATEGORY,
            settings.ECOCUP_NAME,
            settings.ECOCUP_PRICE_TYPES['take'],
            settings.ECOCUP_PRICE
        )
        text = "{:.2f} €".format(self.parent().product_list.get_total())
        self.parent().total.setText(text)
        self.parent().eco_diff += 1
        self.parent().refresh_ecocup_button()

    def repay_ecocup_fnc(self):
        """ Used to repay an ecocup on a note
        """
        self.parent().product_list.add_product(
            settings.ECOCUP_CATEGORY,
            settings.ECOCUP_NAME,
            settings.ECOCUP_PRICE_TYPES['repay'],
            -settings.ECOCUP_PRICE
        )
        text = "{:.2f} €".format(self.parent().product_list.get_total())
        self.parent().total.setText(text)
        self.parent().eco_diff -= 1
        self.parent().refresh_ecocup_button()

    def export(self, notes):
        """ Generic export notes function """
        path, format_ = QtWidgets.QFileDialog(self).getSaveFileName(
            self,
            "Exporter vers",
            "{}.xml".format(datetime.datetime.now().strftime("%Y-%m-%d")),
            "XML Files (*.xml)\nCSV Files (*.csv)"
        )

        if path:
            with open(path, "w") as save_file:
                if format_ == "XML Files (*.xml)":
                    save_file.write(api.notes.export(notes, xml=True))
                else:
                    save_file.write(api.notes.export(notes, csv=True))

    def show_transactions_history(self):
        """ Show transaction logs
        """
        self._close_window()
        self.cur_window = HistoryWindow(self)
        self._connect_window()

    def trigger_search(self):
        """ Open a search window
        """
        self._close_window()
        self.cur_window = SearchWindow(self)
        self._connect_window()

    def stats_by_note_fnc(self):
        """ Open a StatsWindow by note
        """
        self._close_window()
        self.cur_window = StatsWindow()
        self._connect_window()

    def stats_by_category_fnc(self):
        """ Open a StatsWindow by category
        """
        self._close_window()
        self.cur_window = StatsWindow(by_note=False)
        self._connect_window()

