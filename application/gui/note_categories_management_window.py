# Copyright (C) 2014-2018 Bastien Orivel <b2orivel@enib.fr>
# Copyright (C) 2014-2018 Arnaud Levaufre <a2levauf@enib.fr>
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
Note categories management Window
====================


"""


from PyQt5 import QtWidgets, uic
import api.note_categories
import gui.utils
import api.notes


class NoteCategoriesManagementWindow(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/note_categories_management_window.ui', self)
        self._populate_lists()
        self.notes_not_in_category_list.set_custom_filter(
            lambda x: self.current_category not in x["categories"])
        self.notes_in_category_list.set_custom_filter(
            lambda x: self.current_category in x["categories"])
        self.show_note_category_button.setEnabled(False)
        self.hide_note_category_button.setEnabled(False)
        self.delete_note_category_button.setEnabled(True)
        self.show()

    def _populate_lists(self):
        """ Clears and fill the note categories lists.
        """
        self.shown_note_categories_list.clear()
        self.hidden_note_categories_list.clear()
        for category in api.note_categories.get():
            if category['hidden']:
                QtWidgets.QListWidgetItem(category['name'], self.hidden_note_categories_list)
            else:
                QtWidgets.QListWidgetItem(category['name'], self.shown_note_categories_list)
        self._populate_dropdown()

    # TAB 1
    def add_note_category_fnc(self):
        """ Called whenever we press enter on the add_note_category_input or
        "ajouter" is pressed
        """
        category_name = self.add_note_category_input.text()
        self.add_note_category_input.clear()
        if api.note_categories.add(category_name):
            self._populate_lists()
        else:
            gui.utils.error("Error", "Impossible d'ajouter cette catégorie")

    def delete_note_category_fnc(self):
        items = [item.text() for item in self.shown_note_categories_list.selectedItems()]
        api.note_categories.delete(items)
        self._populate_lists()

    def hide_note_category_fnc(self):
        items = [item.text() for item in self.shown_note_categories_list.selectedItems()]
        api.note_categories.set_hidden(items, True)
        self._populate_lists()
        self.hide_note_category_button.setEnabled(False)

    def show_note_category_fnc(self):
        items = [item.text() for item in self.hidden_note_categories_list.selectedItems()]
        api.note_categories.set_hidden(items, False)
        self._populate_lists()
        self.show_note_category_button.setEnabled(False)

    def on_shown_note_category_change(self, new):
        category = api.note_categories.get_unique(name=new)

        if not category:  # Happens after deletion.
            self.delete_note_category_button.setEnabled(False)
            self.hide_note_category_button.setEnabled(False)
            return

        if category['protected']:
            self.delete_note_category_button.setEnabled(False)
            self.hide_note_category_button.setEnabled(False)
        else:
            self.delete_note_category_button.setEnabled(True)
            self.hide_note_category_button.setEnabled(True)

    def on_hidden_note_category_change(self, new):
        category = api.note_categories.get_unique(name=new)

        if not category:
            self.show_note_category_button.setEnabled(False)
            return

        if category['protected']:
            self.show_note_category_button.setEnabled(False)
        else:
            self.show_note_category_button.setEnabled(True)

    # TAB 2
    def _populate_dropdown(self):
        self.note_categories_selector.clear()
        self.note_categories_selector.addItems([cat['name'] for cat in api.note_categories.get()])
        self.current_category = self.note_categories_selector.currentText()

    def dropdown_item_changed_fnc(self, item):
        self.current_category = item
        self.notes_not_in_category_list.set_custom_filter(
            lambda x: self.current_category not in x["categories"])
        self.notes_in_category_list.set_custom_filter(
            lambda x: self.current_category in x["categories"])

    def add_notes_in_category_fnc(self):
        notes = [w.text() for w in self.notes_not_in_category_list.selectedItems()]
        api.note_categories.add_notes(notes, self.current_category)
        self.notes_not_in_category_list.set_custom_filter(
            lambda x: self.current_category not in x["categories"])
        self.notes_in_category_list.set_custom_filter(
            lambda x: self.current_category in x["categories"])

    def remove_notes_from_category_fnc(self):
        notes = [w.text() for w in self.notes_in_category_list.selectedItems()]
        api.note_categories.remove_notes(notes, self.current_category)
        self.notes_not_in_category_list.set_custom_filter(
            lambda x: self.current_category not in x["categories"])
        self.notes_in_category_list.set_custom_filter(
            lambda x: self.current_category in x["categories"])
