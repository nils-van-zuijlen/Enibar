# Copyright (C) 2014-2017 Bastien Orivel <b2orivel@enib.fr>
# Copyright (C) 2014-2017 Arnaud Levaufre <a2levauf@enib.fr>
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


from PyQt5 import QtWidgets, uic, QtCore

import api.notes
import api.prices
import api.categories
import api.validator
from .utils import valid, error
from .notes_list_widget import NotesList
from .panels_management_window import ConsumptionList
from .refill_note_window import MultiRefillNoteWindow
from .validation_window import ValidationWindow
import datetime
import fractions
import sip
import math


def get_coeffed_price(price, coeff):
    """ Returns the coeffed price, nb should be a float and coeff a string
    """
    return float(fractions.Fraction(coeff)) * math.ceil(price * 100) / 100


def get_coeffed_reason(reason, coeff):
    if coeff in ['1/4', '1/2']:
        return coeff + " " + reason
    return reason


def get_coeffed_quantity(quantity, coeff):
    if coeff in ['1/4', '1/2']:
        return 1
    return int(coeff)


class GroupActionsWindow(QtWidgets.QDialog):
    """ NotesAction window class """
    def __init__(self, performer, main_window):
        super().__init__()
        self.main_window = main_window
        self.performer = performer
        self.cur_window = None
        self.current_filter = lambda x: x['hidden'] == 0

        uic.loadUi('ui/group_actions_window.ui', self)

        self.on_change = lambda: False  # Don't do anything.
        self.note_list.rebuild(api.notes.get(self.current_filter))
        self.selected_notes = {}
        self.product_list.build()
        self.show()

    def redis_handle(self, channel, message):
        self.note_list.refresh()

    def del_action(self, _):
        """ Called when "Supprimer" is clicked
        """
        prompt = ValidationWindow("Etes vous sûr de vouloir supprimer ces notes ?")
        if not prompt.is_ok:
            return
        indexes = self.note_list.selectedIndexes()
        to_del = []
        for index in reversed(indexes):
            to_del.append(index.data())
            self.note_list.takeItem(index.row())
        api.notes.remove(to_del)

    def _multiple_action(self, fnc, *args, **kwargs):
        """ Execute a function on the currently selected notes.
            Pass a dict of note: coeff if with_coeffs is True (default),
            otherwise just passes a list of notes.
        """
        with_coeffs = kwargs.pop("with_coeffs", True)
        notes = {}

        for i in range(self.selected_notes_report.topLevelItemCount()):
            item = self.selected_notes_report.topLevelItem(i)
            coeff = self.selected_notes_report.itemWidget(item, 1).currentText()
            note = item.text(0)
            notes[note] = coeff

        for widget in self.note_list.selectedItems():
            widget.setSelected(False)

        if with_coeffs:
            return fnc(notes, *args, **kwargs)

        return fnc(list(notes.keys()), *args, **kwargs)

    def take_action(self):
        """ Called when we want to take on notes
        """
        self.cur_window = MultiRefillNoteWindow(self.performer, text="enlever")
        self.cur_window.reason.setPlaceholderText("Raison")
        self.cur_window.reason.setValidator(api.validator.NAME)
        self.cur_window.reason.on_change()
        self.cur_window.on_change()

        def continuation():
            """ Called when the MultiRefillNoteWindow is closed.
            """
            def take(notes):
                """ take on notes
                """
                if not notes:
                    return

                to_add = self.cur_window.to_add_value
                if not to_add:
                    return

                reason = self.cur_window.reason_value

                transactions = []
                for note, coeff in notes.items():
                    price = get_coeffed_price(to_add, coeff)
                    transactions.append({'note': note,
                                         'category': "Note",
                                         'product': get_coeffed_reason(reason, coeff),
                                         'price_name': "Solde",
                                         'quantity': get_coeffed_quantity(1, coeff),
                                         'price': -price
                                        }
                    )
                api.notes.transactions(notes, -price)
                api.transactions.log_transactions(transactions)
            self._multiple_action(take)

        self.cur_window.finished.connect(continuation)

    def refill_action(self):
        """ Called when we want to refill notes.
        """
        self.cur_window = MultiRefillNoteWindow(self.performer)

        def continuation():
            """ Called when the MultiRefillNoteWindow is closed.
            """
            def refill(notes):
                """ Refill notes
                """
                to_add = self.cur_window.to_add_value
                reason = self.cur_window.reason_value
                if not to_add:
                    return
                transactions = []
                for note, coeff in notes.items():
                    price = get_coeffed_price(to_add, coeff)
                    transactions.append({'note': note,
                                         'category': "Note",
                                         'product': get_coeffed_reason('{} {}'.format(self.performer, "[{}]".format(reason) if reason else ""), coeff),
                                         'price_name': "Rechargement",
                                         'quantity': get_coeffed_quantity(1, coeff),
                                         'price': price
                                        }
                    )
                api.notes.transactions(notes, price)
                api.transactions.log_transactions(transactions)
            self._multiple_action(refill)

        self.cur_window.finished.connect(continuation)

    def take_products_action(self):
        """ Called when "Valider" is clicked
        """
        product = self.product_list.get_selected_product()
        if product is None:
            return

        price_name = self.price_list.currentText()
        category = api.categories.get_unique(id=product['category'])['name']
        descriptor = list(api.prices.get_descriptor(
            category=product['category'],
            label=price_name))[0]
        price = api.prices.get_unique(price_description=descriptor['id'],
                                      product=product['id'])

        def inner(notes):
            if not notes:
                return
            transactions = []
            for note, coeff in notes.items():
                real_price = get_coeffed_price(price['value'], coeff)
                transaction = {
                    'note': note,
                    'category': category,
                    'product': get_coeffed_reason(product['name'], coeff),
                    'price_name': price_name,
                    'quantity': get_coeffed_quantity(1, coeff),
                    'liquid_quantity': descriptor['quantity'],
                    'percentage': product['percentage'],
                    'price': -real_price
                }
                transactions.append(transaction)

            if api.transactions.log_transactions(transactions):
                api.notes.transactions(notes, -real_price)
                valid("OK", "Transaction effectuée")

        self._multiple_action(inner)

    def export_csv_action(self):
        """ Called when "Export CSV" is clicked
        """
        path, _ = QtWidgets.QFileDialog(self).getSaveFileName(
            self, "Exporter vers", "{}.csv".format(
                datetime.datetime.now().strftime("%Y-%m-%d")),
            "CSV Files (*.csv)")
        if path:
            try:
                with open(path, "w") as save_file:
                    save_file.write(self._multiple_action(api.notes.export_by_nick, with_coeffs=False))
            except PermissionError:
                error("Erreur", "Impossible d'écrire ici")

    def selection_changed(self):
        selected = [obj.text() for obj in self.note_list.selectedItems()]
        to_del = []

        if len(selected) > len(self.selected_notes):  # Something was added
            for note in selected:
                if note not in self.selected_notes:
                    cb = QtWidgets.QComboBox()
                    cb.addItems(["1/4", "1/2"] + list(map(str, range(1, 11))))
                    cb.setCurrentIndex(2)

                    item = QtWidgets.QTreeWidgetItem(self.selected_notes_report, [note, "1"])
                    self.selected_notes_report.setItemWidget(item, 1, cb)
                    item.setFlags(QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
                    self.selected_notes[note] = item
        else:
            for note in self.selected_notes:
                if note not in selected:
                    to_del.append(note)

        for note in to_del:
            item = self.selected_notes[note]
            del self.selected_notes[note]
            sip.delete(item)

        self.note_list.search_input.clear()
        self.note_list.search_input.setFocus(True)

    def check_edit(self, item, column):
        """ Allow the edition of the quantity column in the notes report table
        """
        if column == 1:
            self.selected_notes_report.editItem(item, column)

    def notes_management_fnc(self):
        self.main_window.menu_bar.manage_note_fnc_no_auth(False, self.performer)


class MultiNotesList(NotesList):
    """ List of notes with multi-selection
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.mouse_pressed = False

    def rebuild(self, notes_list):
        """ Just rebuild the notes list
        """
        self.clear()
        self.build(notes_list)

    def refresh(self):
        """ Rebuild the note list every 10 seconds
        """
        selected = [item.text() for item in self.selectedItems()]
        self.rebuild(api.notes.get(self.current_filter))
        for item in selected:
            try:
                self.findItems(item, QtCore.Qt.MatchExactly)[0].\
                    setSelected(True)
            except IndexError:
                pass

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.mouse_pressed = True
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not self.mouse_pressed:  # Disable click + drag
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.mouse_pressed = False
        super().mouseReleaseEvent(event)


class UniqueConsumptionList(ConsumptionList):
    """ A Consumption list where you can select only one item
    """
    def add_product(self, name, category, percentage):
        """ Add product to consumption list. If the products has no null price
            only.

        :param str name: Product name
        :param str category: Category Name
        """
        # Find category widget
        cat_widget = None
        for cat in self.categories:
            if category == cat.text(0):
                cat_widget = cat
        if not cat_widget:
            return

        category = api.categories.get_unique(name=category)
        product = api.products.get_unique(
            category=category['id'],
            name=name
        )
        if not product:
            return

        for price in api.prices.get(product=product['id']):
            if float(price['value']) != 0:
                break
        else:
            return

        prod_widget = QtWidgets.QTreeWidgetItem([name])
        cat_widget.addChild(prod_widget)
        self.products.append(prod_widget)

    def get_selected_product(self):
        """ Return the current selected product
        """
        for index in self.selectedIndexes():
            if index.parent().isValid():
                cat_name = index.parent().data()
                category = api.categories.get_unique(name=cat_name)
                if not category:
                    continue
                product = api.products.get_unique(
                    category=category['id'],
                    name=index.data()
                )
                if not product:
                    # Error
                    continue
                return product

    def on_selection(self):
        """ Called when a product is selected
        """
        selected = self.get_selected_product()
        cb_box = self.parent().parent().price_list
        valid_button = self.parent().parent().take_products_btn
        cb_box.clear()
        cb_box.setEnabled(False)
        valid_button.setEnabled(False)
        if selected is not None:
            for price in api.prices.get(product=selected["id"]):
                if float(price['value']) > 0:
                    cb_box.setEnabled(True)
                    valid_button.setEnabled(True)
                    cb_box.addItem(price['label'])

