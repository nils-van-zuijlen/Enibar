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
Stats window
============

Provide neat stats
"""

from PyQt5 import QtWidgets, uic, QtCore
from collections import defaultdict
import api.stats
from gui.tree_item_widget import TreeWidget


class StatsWindow(QtWidgets.QDialog):
    """Stats window class
    """
    def __init__(self, by_note=True, note_filter=None, cat_filter=None):
        super().__init__()
        uic.loadUi('ui/stats_window.ui', self)

        self.stats_cache = defaultdict(lambda: defaultdict(
            lambda: defaultdict(lambda: 0)))
        self.prices = defaultdict(dict)
        self.total_cache = defaultdict(lambda: defaultdict(lambda: 0))

        self.note_widgets = []
        self.win = None

        self.tot_debit = 0
        self.tot_credit = 0
        if by_note:
            self.note_mode = True
        else:
            self.note_mode = False

        self.note_filter = note_filter
        self.cat_filter = cat_filter

        self.progressbar.reset()
        self.progressbar.setRange(0, 100)
        self.progressbar.setValue(1)

        self.updatetimer = QtCore.QTimer()
        self.updatetimer.singleShot(200, self._update)

        self.show()

    def _resize_columns(self):
        """ Resize all columns to the content
        """
        for i in range(4):
            self.tree.resizeColumnToContents(i)

    def _update(self):
        """ Callback for the timer to update the tree
        """
        if self.note_mode:
            self.build_stats_notes(self.note_filter)
            self.build_widgets_notes()
        else:
            self.build_stats_categories(self.cat_filter)
            self.build_widgets_categories()

    def build_stats_categories(self, category_filter):
        """ Build stats when we want them by category
        """
        self.progressbar.setFormat("Construction du cache")
        self.progressbar.setValue(20)
        for line in api.stats.get_notes_stats():
            if category_filter and line['category'] != category_filter:
                continue
            pid = "%s - (%s) [%s €]" % (line['product'], line['price_name'],
                abs(line['price']))

            self.prices[line['category']][pid] = line['price']
            cat = self.stats_cache[line['category']]
            cat[pid][line['nickname']] += line['quantity']

            if line['price'] > 0:
                self.total_cache[line['category']]['credit'] +=\
                    line['price'] * line['quantity']
                self.tot_credit += line['price'] * line['quantity']
            else:
                self.total_cache[line['category']]['debit'] +=\
                    line['price'] * line['quantity']
                self.tot_debit += line['price'] * line['quantity']
            self.total_cache[line['category']]['qt'] += line['quantity']

    def build_widgets_categories(self):
        """ Build the tree when we have stats by category
        """
        self.progressbar.setFormat("Construction des widgets")
        nb, i = len(self.stats_cache.keys()), 0
        for key, value in self.stats_cache.items():
            self.progressbar.setValue(20 + int(i * 80 / nb))
            i += 1
            w = TreeWidget(self.tree, [
                key,
                str(int(self.total_cache[key]['qt'])),
                str(round(self.total_cache[key]['credit'], 2)),
                str(round((self.total_cache[key]['credit'] * 100) /
                    self.tot_credit, 2) if self.tot_credit else "0"),
                str(round(self.total_cache[key]['debit'], 2)),
                str(round((self.total_cache[key]['debit'] * 100) /
                    self.tot_debit, 2) if self.tot_debit else "0")]
            )
            for name, product in value.items():
                tot_product_debit = 0
                tot_product_credit = 0
                tot_product_qt = 0
                for note, qt in product.items():
                    if self.prices[key][name] > 0:
                        tot_product_credit += qt * self.prices[key][name]
                    else:
                        tot_product_debit += qt * self.prices[key][name]
                    tot_product_qt += qt

                w1 = TreeWidget(w, [
                    name,
                    str(int(tot_product_qt)),
                    str(round(tot_product_credit, 2)),
                    str(round((tot_product_credit * 100) / self.total_cache[key]['credit'], 2) if self.total_cache[key]['credit'] else "0"),
                    str(round(tot_product_debit, 2)),
                    str(round((tot_product_debit * 100) / self.total_cache[key]['debit'], 2) if self.total_cache[key]['debit'] else "0")]
                )
                self.note_widgets.append(w1)
                for note, qt in product.items():
                    product_price = qt * self.prices[key][name]
                    w2 = TreeWidget(w1, [
                        note,
                        str(int(qt)),
                        str(round(product_price, 2)) if product_price > 0 else "0",
                        str(round((product_price * 100) / tot_product_credit, 2) if (tot_product_credit and product_price > 0) else "0"),
                        str(round(product_price, 2)) if product_price < 0 else "0",
                        str(round((product_price * 100) / tot_product_debit, 2) if (tot_product_debit and product_price < 0) else "0")]
                    )
                    self.note_widgets.append(w2)
            self.note_widgets.append(w)
        self.progressbar.setValue(100)
        self.progressbar.setFormat("Terminé")
        self._resize_columns()

    # Notes
    def build_stats_notes(self, note_filter):
        """ Refresh the stats of the window
        """
        self.progressbar.setFormat("Construction du cache")
        self.progressbar.setValue(20)
        for line in api.stats.get_notes_stats():
            if note_filter and line['nickname'] != note_filter:
                continue
            pid = "%s - (%s) [%s €]" % (line['product'], line['price_name'],
                abs(line['price']))

            self.prices[line['category']][pid] = line['price']
            note = self.stats_cache[line['nickname']]
            note[line['category']][pid] += line['quantity']

            if line['price'] > 0:
                self.total_cache[line['nickname']]['credit'] +=\
                    line['price'] * line['quantity']
                self.tot_credit += line['price'] * line['quantity']
            else:
                self.total_cache[line['nickname']]['debit'] +=\
                    line['price'] * line['quantity']
                self.tot_debit += line['price'] * line['quantity']
            self.total_cache[line['nickname']]['qt'] += line['quantity']

    def build_widgets_notes(self):
        """ Build the tree when we have stats by note
        """
        self.progressbar.setFormat("Construction des widgets")
        nb, i = len(self.stats_cache.keys()), 0
        for key, value in self.stats_cache.items():
            self.progressbar.setValue(20 + int(i * 80 / nb))
            i += 1
            w = TreeWidget(self.tree, [
                key,
                str(int(self.total_cache[key]['qt'])),
                str(round(self.total_cache[key]['credit'], 2)),
                str(round((self.total_cache[key]['credit'] * 100) / self.tot_credit,
                    2) if self.tot_credit else "0"),
                str(round(self.total_cache[key]['debit'], 2)),
                str(round((self.total_cache[key]['debit'] * 100) / self.tot_debit,
                    2) if self.tot_debit else "0")]
            )

            # Build totals
            for category, products in value.items():
                tot_cat_debit = 0
                tot_cat_credit = 0
                tot_cat_nb = 0
                for name, qt in products.items():
                    if self.prices[category][name] > 0:
                        tot_cat_credit += qt * self.prices[category][name]
                    else:
                        tot_cat_debit += qt * self.prices[category][name]
                    tot_cat_nb += qt
                w2 = TreeWidget(w, [
                    category,
                    str(tot_cat_nb),
                    str(round(tot_cat_credit, 2)),
                    str(round((tot_cat_credit * 100) / self.total_cache[key]['credit'], 2) if self.total_cache[key]['credit'] else "0"),
                    str(round(tot_cat_debit, 2)),
                    str(round((tot_cat_debit * 100) / self.total_cache[key]['debit'], 2) if self.total_cache[key]['debit'] else "0")]
                )
                for name, qt in products.items():
                    product_price = self.prices[category][name] * qt
                    w3 = TreeWidget(w2, [
                        name,
                        str(int(qt)),
                        str(round(product_price, 2)) if product_price > 0 else "0",
                        str(round((product_price * 100) / tot_cat_credit, 2) if (tot_cat_credit and product_price > 0) else "0"),
                        str(round(product_price, 2)) if product_price < 0 else "0",
                        str(round((product_price * 100) / tot_cat_debit, 2) if (tot_cat_debit and product_price < 0) else "0")]
                    )
                    self.note_widgets.append(w3)
                self.note_widgets.append(w2)
            self.note_widgets.append(w)
        self.progressbar.setValue(100)
        self.progressbar.setFormat("Terminé")
        self._resize_columns()

    def show_details(self):
        """ Called when we click on "details"
        """
        selected = self.tree.selectedItems()
        if selected:
            selected = selected[0]
            if not selected.childCount():
                if not self.note_mode:
                    self.win = StatsWindow(note_filter=selected.text(0))
            elif not selected.child(0).childCount():
                if self.note_mode:  # Category
                    self.win = StatsWindow(by_note=False,
                                           cat_filter=selected.text(0)
                    )
            else:
                if self.note_mode:
                    self.win = StatsWindow(note_filter=selected.text(0))

    def on_selection(self):
        """ Set state of the details button
        """
        selected = self.tree.selectedItems()
        if not selected:
            self.details_button.setEnabled(False)
        selected = selected[0]
        if selected and ((not selected.childCount() and not self.note_mode) or
                (selected.child(0) and
                 (not selected.child(0).childCount() and self.note_mode)) or
                selected.child(0) and selected.child(0).childCount()):
            self.details_button.setEnabled(True)
        else:
            self.details_button.setEnabled(False)

