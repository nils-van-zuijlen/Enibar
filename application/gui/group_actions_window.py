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
NotesAction Window
====================


"""


from PyQt5 import QtWidgets, uic, QtCore

import api.notes
import api.prices
import api.categories
import api.validator
from .utils import valid
from .notes_list_widget import NotesList
from .panels_management_window import ConsumptionList
from .refill_note_window import MultiRefillNoteWindow
from .validation_window import ValidationWindow
import datetime


class GroupActionsWindow(QtWidgets.QDialog):
    """ NotesAction window class """
    def __init__(self, performer):
        super().__init__()
        self.performer = performer
        self.cur_window = None
        self.current_filter = lambda x: x['hidden'] == 0

        uic.loadUi('ui/group_actions_window.ui', self)

        self.filter_input.setEnabled(False)
        self.filter_input.set_validator(api.validator.NUMBER)
        self.on_change = lambda: False  # Don't do anything.
        self.filter_input.keyPressEvent = self.filter_input_changed
        self.note_list.rebuild(api.notes.get(self.current_filter))
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
        self.note_list.rebuild(api.notes.get(self.note_list.current_filter))

    def _multiple_action(self, fnc, *args, **kwargs):
        """ Execute a function on the currently selected notes
        """
        indexes = self.note_list.selectedIndexes()
        notes_nicks = []
        for index in indexes:
            notes_nicks.append(index.data())
        val = fnc(notes_nicks, *args, **kwargs)
        self.note_list.rebuild(api.notes.get(self.note_list.current_filter))
        return val

    def filter_combobox_change(self, id_):
        """ Called when the filter combobox is chnged
        """
        if id_ == 0:
            self.note_list.current_filter = lambda x: x['hidden'] == 0
            self.filter_input.setEnabled(False)
        elif id_ == 1:
            self.note_list.current_filter = lambda x: x['hidden'] == 1
            self.filter_input.setEnabled(False)
        elif id_ == 2:
            self.filter_input.setEnabled(True)
            self.filter_input.setText("0")
            self.note_list.current_filter = lambda x: x['note'] > 0 and\
                x['hidden'] == 0
        elif id_ == 3:
            self.filter_input.setEnabled(True)
            self.filter_input.setText("0")
            self.note_list.current_filter = lambda x: x['note'] < 0 and\
                x['hidden'] == 0
        self.note_list.rebuild(api.notes.get(self.note_list.current_filter))

    def filter_input_changed(self, event):
        """ Called when the filter input is changed
        """
        QtWidgets.QLineEdit.keyPressEvent(self.filter_input, event)
        text = self.filter_input.text()
        try:
            if self.filter_combobox.currentIndex() == 2:
                self.note_list.current_filter = lambda x: x['note'] >\
                    float(text) and x['hidden'] == 0
                self.note_list.rebuild(api.notes.get(
                    self.note_list.current_filter))
            elif self.filter_combobox.currentIndex() == 3:
                self.note_list.current_filter = lambda x: x['note'] <\
                    float(text) and x['hidden'] == 0
                self.note_list.rebuild(api.notes.get(
                    self.note_list.current_filter))
        except ValueError:
            self.note_list.clear()

    def hide_action(self):
        """ Called when "cacher" is clicked
        """
        self._multiple_action(api.notes.hide)

    def show_action(self):
        """ Called when "Montrer" is clicked
        """
        self._multiple_action(api.notes.show)

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
                notes = list(notes)
                to_add = self.cur_window.to_add_value
                reason = self.cur_window.reason_value
                if not to_add:
                    return
                transactions = []
                for note in notes:
                    transactions.append({'note': note,
                                         'category': "Note",
                                         'product': reason,
                                         'price_name': "Solde",
                                         'quantity': 1,
                                         'price': -to_add
                                        }
                    )
                api.notes.transactions(notes, -to_add)
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
                notes = list(notes)
                to_add = self.cur_window.to_add_value
                reason = self.cur_window.reason_value
                if not to_add:
                    return
                transactions = []
                for note in notes:
                    transactions.append({'note': note,
                                         'category': "Note",
                                         'product': '{} {}'.format(self.performer, "[{}]".format(reason) if reason else ""),
                                         'price_name': "Rechargement",
                                         'quantity': 1,
                                         'price': to_add
                                        }
                    )
                api.notes.transactions(notes, to_add)
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

        transactions = []
        notes = []
        for note in self.note_list.selectedItems():
            transaction = {
                'note': note.text(),
                'category': category,
                'product': product['name'],
                'price_name': price_name,
                'quantity': 1,
                'price': -price['value']
            }
            transactions.append(transaction)
            notes.append(note.text())
        if api.transactions.log_transactions(transactions):
            api.notes.transactions(notes, -price['value'])
            valid("OK", "Transaction effectuée")

    def export_csv_action(self):
        """ Called when "Export CSV" is clicked
        """
        path, _ = QtWidgets.QFileDialog(self).getSaveFileName(
            self, "Exporter vers", "{}.csv".format(
                datetime.datetime.now().strftime("%Y-%m-%d")),
            "CSV Files (*.csv)")
        if path:
            with open(path, "w") as save_file:
                save_file.write(self._multiple_action(api.notes.export_by_nick,
                                                      csv=True))

    def export_xml_action(self):
        """ Called when "Export XML" is clicked
        """
        path, _ = QtWidgets.QFileDialog(self).getSaveFileName(
            self, "Exporter vers", "{}.xml".format(
                datetime.datetime.now().strftime("%Y-%m-%d")),
            "XML Files (*.xml)")
        if path:
            with open(path, "w") as save_file:
                save_file.write(self._multiple_action(api.notes.export_by_id,
                                                      xml=True))


class MultiNotesList(NotesList):
    """ List of notes with multi-selection
    """
    def __init__(self, parent):
        super().__init__(parent)

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


class UniqueConsumptionList(ConsumptionList):
    """ A Consumption list where you can select only one item
    """

    def __init__(self, parent):
        super().__init__(parent)

    def add_product(self, name, category):
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

