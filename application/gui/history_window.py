# Copyright (C) 2014-2016 Bastien Orivel <b2orivel@enib.fr>
# Copyright (C) 2014-2016 Arnaud Levaufre <a2levauf@enib.fr>
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
Transaction hisotry window.
"""

from PyQt5 import QtWidgets, uic, QtCore
from .auth_prompt_window import ask_auth
import api.transactions
from gui.tree_item_widget import TreeWidget
import copy
import datetime
import time
import gui.utils
import collections


class HistoryWindow(QtWidgets.QDialog):
    """ Base class for transaction history
    This class act like a singleton to avoid rebuilding history each time you
    open the window.
    """
    _instance = None
    # _instance_count is required to init QtStuffs only once.
    _instance_count = 0

    def __new__(cls, *args, **kwargs):
        """ Create singleton for better history responsivness.
        """
        cls._instance_count += 1
        if not cls._instance:
            cls._instance = super(HistoryWindow, cls).__new__(
                cls, *args, **kwargs
            )
        return cls._instance

    def __init__(self, parent):
        if self._instance_count == 1:
            super().__init__(parent)
            uic.loadUi('ui/history_window.ui', self)

            self.allow_refresh = False
            self.updatetimer = QtCore.QTimer()
            self.updatetimer.timeout.connect(self.update_list)
            self.updatetimer.setInterval(175)

            column_widths = [120, 120, 120, 120, 120, 75, 50, 50, 50]
            for i, width in enumerate(column_widths):
                self.transaction_list.setColumnWidth(i, width)

            # Hide column with id's. This column is needed to avoid huge
            # operation when we have to find transaction in the transaction
            # list from a selected row. Without this column (and so the id) we
            # have to loop through all transactions and compare their widget to
            # the selected one while here we can simply access transactions
            # this way: transactions[widget.text(8)] if we have the widget.
            self.transaction_list.hideColumn(8)

            self.filter.hide()
            self.transactions = {}
            self.cbs = collections.OrderedDict(
                [('note', self.cb_nickname),
                ('lastname', self.cb_lastname),
                ('firstname', self.cb_firstname),
                ('category', self.cb_category),
                ('product', self.cb_product), ]
            )
            self.last_id = 0

        self.show()

    def showEvent(self, event):
        """ Show Event
        Overwrite default QtDialog showEvent handler. Reset ui parameter when
        window is shown.
        """
        self.allow_refresh = False
        for _, combobox in self.cbs.items():
            combobox.setCurrentIndex(0)
        self.allow_refresh = True

        date = QtCore.QDateTime()
        date.setMSecsSinceEpoch((time.time() - 24 * 3600 * 7) * 1000)

        # We disable the signals here to avoid calling call_update when the
        # window opens as it's useless.
        self.datetime_from.blockSignals(True)
        self.datetime_from.setDateTime(date)
        self.datetime_from.blockSignals(False)
        date.setMSecsSinceEpoch(time.time() * 1000)
        self.datetime_to.blockSignals(True)
        self.datetime_to.setDateTime(date)
        self.datetime_to.blockSignals(False)

        self.progressbar.reset()
        self.progressbar.setRange(0, 0)
        self.progressbar.setFormat("En attente de la base de donnée.")

        QtCore.QTimer.singleShot(200, self.prepare)
        event.accept()

    def update_filters(self):
        """ Update filters
        """
        # Get filters current values.
        transactions_left = copy.copy(self.transactions)
        filters = {}

        for row, combobox in self.cbs.items():
            if combobox.currentText():
                filters[row] = combobox.currentText()
                transactions_left = {key: value for key, value in transactions_left.items() if value[row] == filters[row]}

        current_cat = self.cb_category.currentText()
        for row, combobox in self.cbs.items():
            combobox.clear()
            combobox.addItem("")
            values = set()
            for data in transactions_left.values():
                if data[row] and not (row == 'product' and data['category'] == 'Note' and current_cat != 'Note'):
                    for row_, filt in filters.items():
                        if row != row_ and data[row_] != filt:
                            break
                    else:
                        values.add(data[row])

            combobox.addItems(list(values))
            if row in filters:
                index = combobox.findText(filters[row])
                if index:
                    combobox.setCurrentIndex(index)

    def prepare(self):
        """ Prepare window by fetching all transactions, required filter fields
        and displaying history.
        """
        self.fetch_transactions()
        self.call_update()

    def call_update(self):
        """ Wrapper to call update on transaction list.
        It enhance performances when user rapidly change filter or date by
        calling for a list update only when filter have not changed after
        150ms.
        """
        if self.updatetimer.isActive():
            self.updatetimer.stop()
        self.updatetimer.start()

    def cleared_combobox(self, _):
        """ Clear combo box.
        Check if combobox text is empty and select the first item of the
        combobox. This must be called when editing a combobox to detect when
        filter should be reseted.
        """
        if not self.sender().currentText():
            self.sender().setCurrentIndex(0)
            self.call_update()

    def fetch_transactions(self):
        """ Fetch all transactions and build all QtWidgets needed to display
        them. A huge dictionary containing all transactions information is
        created to allow fast advanced filtering.
        """
        transactions = list(api.transactions.get(id__gt=self.last_id))
        length, count = len(transactions), 0
        self.progressbar.setFormat("Chargement de l'historique %p%")
        self.progressbar.reset()
        self.progressbar.setRange(0, 20)
        for trans in transactions:
            count += 1
            if count % 1000:
                self.progressbar.setValue(int(count / length * 20))
            if trans['id'] not in self.transactions:
                if trans['price'] >= 0:
                    credit = round(trans['price'], 2)
                    debit = "-"
                else:
                    credit = "-"
                    debit = round(-trans['price'], 2)
                self.transactions[trans['id']] = {
                    'note': trans['note'],
                    'lastname': trans['lastname'],
                    'firstname': trans['firstname'],
                    'price': trans['price'],
                    'price_name': trans['price_name'],
                    'date': trans['date'],
                    'product': trans['product'],
                    'category': trans['category'],
                    'quantity': trans['quantity'],
                    'credit': credit,
                    'debit': debit,
                    'widget': None,
                    'id': trans['id'],
                    'show': False,
                }
            self.last_id = trans['id']
        self.progressbar.setFormat("Terminé")

    def update_summary(self):
        """ Update debit, credit and Total on the window
        """
        quantity = 0
        credited = 0
        debited = 0

        for _, transaction in self.transactions.items():
            if transaction['show']:
                price = float(transaction['price'])
                if price >= 0:
                    credited += price
                if price < 0:
                    debited += price
                quantity += transaction['quantity']

        self.quantity.setText(str(quantity))
        self.credited.setText("{} €".format(round(credited, 2)))
        self.debited.setText("{} €".format(round(debited, 2)))
        self.total.setText("{} €".format(round(credited + debited, 2)))

    def update_summary_selected(self):
        """ update debit credit and Total on selected items.
        """
        quantity = 0
        credited = 0
        debited = 0

        for i, index in enumerate(self.transaction_list.selectedIndexes()):
            # i % (columnCount - 1) because the column with the id is hidden
            if i % (self.transaction_list.columnCount() - 1) == 0:
                widget = self.transaction_list.topLevelItem(index.row())
                price = self.transactions[int(widget.text(8))]['price']
                if price >= 0:
                    credited += price
                if price < 0:
                    debited += price
                quantity += self.transactions[int(widget.text(8))]['quantity']

        self.selected_quantity.setText(str(quantity))
        self.selected_credited.setText("{} €".format(round(credited, 2)))
        self.selected_debited.setText("{} €".format(round(debited, 2)))
        self.selected_solde.setText("{} €".format(round(credited + debited, 2)))

    def update_list(self):
        """ Update the list with all filters
        """
        if not self.allow_refresh:
            return
        self.update_filters()

        if self.updatetimer.isActive():
            self.updatetimer.stop()
        filter_ = {
            'note': self.cb_nickname.currentText(),
            'lastname': self.cb_lastname.currentText(),
            'firstname': self.cb_firstname.currentText(),
            'category': self.cb_category.currentText(),
            'product': self.cb_product.currentText(),
        }
        self.progressbar.setFormat("Application des filtres %p%")
        length = len(self.transactions)
        self.progressbar.setRange(0, 20)
        count = 0
        self.transaction_list.clear()
        for id_, transaction in self.transactions.items():
            show = True
            count += 1
            self.progressbar.setValue(int(count / length * 20))
            if not self.datetime_from.dateTime() <= \
                    self.transactions[id_]['date'] <= \
                    self.datetime_to.dateTime():
                show = False
            for index, regex in filter_.items():
                if regex and regex != transaction[index]:
                    show = False
                    break
            transaction['show'] = show
            if show:
                widget = TreeWidget(self.transaction_list, (
                    transaction['date'].toString("yyyy/MM/dd HH:mm:ss"),
                    transaction['note'],
                    transaction['category'],
                    transaction['product'],
                    transaction['price_name'],
                    str(transaction['quantity']),
                    str(transaction['credit']),
                    str(transaction['debit']),
                    str(transaction['id'])
                ))
                transaction['widget'] = widget

        self.progressbar.setFormat("Terminé")
        self.progressbar.setValue(100)
        self.update_summary()

    @ask_auth("manage_notes")
    def delete(self, _):
        """ Delete a product from a line in the history
        """
        indexes = self.transaction_list.selectedIndexes()
        for i, index in reversed(list(enumerate(indexes))):
            # i % (columnCount - 1) because the column with the id is hidden
            if i % (self.transaction_list.columnCount() - 1) != 0:
                continue

            widget = self.transaction_list.topLevelItem(index.row())

            if not api.transactions.rollback_transaction(widget.text(8)):
                gui.utils.error(
                    "Impossible de supprimer la transation n°{}".format(
                        widget.text(8)
                    ),
                    "La transaction du {date} sur la note {note} "
                    "n'a pas été supprimée.".format(
                        date=widget.text(0),
                        note=widget.text(1)
                    )
                )
                continue

            try:
                quantity = int(widget.text(5))
            except ValueError:
                quantity = 1

            if quantity > 1:
                if widget.text(6) != "-":
                    credit = float(widget.text(6))
                    credit -= credit / quantity
                    credit = round(credit, 2)
                    self.transactions[int(widget.text(8))]['price'] = credit
                    self.transactions[int(widget.text(8))]['credit'] = credit
                elif widget.text(7) != "-":
                    debit = float(widget.text(7))
                    debit -= debit / quantity
                    debit = round(debit, 2)
                    self.transactions[int(widget.text(8))]['price'] = -debit
                    self.transactions[int(widget.text(8))]['debit'] = debit
                self.transactions[int(widget.text(8))]['quantity'] = quantity - 1
            else:
                self.transaction_list.takeTopLevelItem(index.row())
                del self.transactions[int(widget.text(8))]
        self.call_update()

    @ask_auth("manage_notes")
    def delete_line(self, _):
        """ Delete a complete line
        """
        indexes = self.transaction_list.selectedIndexes()
        for i, index in reversed(list(enumerate(indexes))):
            # i % (columnCount - 1) because the column with the id is hidden
            if i % (self.transaction_list.columnCount() - 1) != 0:
                continue

            widget = self.transaction_list.topLevelItem(index.row())
            if not api.transactions.rollback_transaction(widget.text(8), True):
                gui.utils.error(
                    "Impossible de supprimer la transation n°{}".format(
                        widget.text(8)
                    ),
                    "La transaction du {date} sur la note {note} "
                    "n'a pas été supprimée.".format(
                        date=widget.text(0),
                        note=widget.text(1)
                    )
                )
                continue
            index = self.transaction_list.indexOfTopLevelItem(widget)
            self.transaction_list.takeTopLevelItem(index)
            del self.transactions[int(widget.text(8))]
        self.call_update()

    def export_csv(self):
        """ Export the selected lines in a csv file
        """
        export_trans = []
        for num, index in enumerate(self.transaction_list.selectedIndexes()):
            # i % (columnCount - 1) because the column with the id is hidden
            if num % (self.transaction_list.columnCount() - 1) != 0:
                continue
            widget = self.transaction_list.topLevelItem(index.row())
            export_trans.append(self.transactions[int(widget.text(8))])

        dialog = ExportWindow(export_trans)
        dialog.exec_()


class ExportWindow(QtWidgets.QDialog):
    """ Export Window
    Used to select wich history column user want to export.
    """
    def __init__(self, trans):
        super().__init__()
        uic.loadUi('ui/history_export_window.ui', self)
        self.trans = trans

    def accept(self, *_):
        """ Accept
        Rewrite of QDialog::accept so it can handle export when user is done
        selecting what he want to export
        """
        dest = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Destination",
            "{date}-historique.csv".format(date=datetime.date.today())
        )

        fields = collections.OrderedDict([
            ('date', self.date.isChecked()),
            ('note', self.nickname.isChecked()),
            ('firstname', self.firstname.isChecked()),
            ('lastname', self.lastname.isChecked()),
            ('category', self.category.isChecked()),
            ('product', self.product.isChecked()),
            ('quantity', self.quantity.isChecked()),
            ('price', self.price.isChecked()),
        ])

        if not dest[0]:
            self.close()
            return
        try:
            with open(dest[0], "w") as dest_file:
                headers = [key for key, checked in fields.items() if checked]
                dest_file.write(';'.join(headers) + "\n")
                # Write all transactions to file
                for trans in self.trans:
                    items = []
                    for key, checked in fields.items():
                        if not checked:
                            continue
                        if type(trans[key]) is QtCore.QDateTime:
                            items.append(trans[key].toString("yyyy-MM-dd hh:mm:ss"))
                        else:
                            items.append(str(trans[key]))
                    line = ";".join(items)
                    dest_file.write(line + "\n")
        except PermissionError:
            gui.utils.error("Erreur", "Impossible d'écrire ici")
        self.close()

