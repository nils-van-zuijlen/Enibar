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
ManageNotes Window
====================


"""


from PyQt5 import QtWidgets, QtCore, QtGui, uic

from gui.input_widget import Input
import api.notes
import api.validator
import api.note_categories
import datetime
import gui.notes_list_widget
import settings
import gui.auth_prompt_window


class NotesManagementWindow(QtWidgets.QDialog):
    """ ManageNotes window class """
    def __init__(self, performer, main_window):
        super().__init__()
        uic.loadUi('ui/notes_management_window.ui', self)

        self.main_window = main_window
        self.performer = performer

        # Add validators on inputs.
        self.nickname_input.set_validator(api.validator.NAME)
        self.name_input.set_validator(api.validator.NAME)
        self.first_name_input.set_validator(api.validator.NAME)
        self.mail_input.set_validator(api.validator.MAIL)
        self.phone_input.set_validator(api.validator.PHONE_NUMBER)
        self.birthdate_input.set_validator(api.validator.BIRTHDATE)

        self.photo_selected = None
        self.current_nickname = None

        self.adding = False
        self.categories_added = []

        self.current_shown = -1
        self.on_change = api.validator.on_change(self, self.save_button)
        self.note_list.current_filter = lambda x: True
        self.note_list.refresh(api.notes.get())
        self.show()

    def redis_handle(self, channel, message):
        if channel == 'enibar-notes-mgnt':
            self.note_list.clear()
            self.note_list.refresh(api.notes.get())
            try:
                self.note_list.setCurrentItem(
                    self.note_list.findItems(message[0], QtCore.Qt.MatchExactly)[0],
                    QtCore.QItemSelectionModel.SelectCurrent)
            except IndexError:
                pass

    def add_photo(self):
        """ Function called to add a photo. Open a QFileDialog and fill
            self.photo with the selected image
        """
        self.photo_selected = QtWidgets.QFileDialog(self).getOpenFileUrl(
            self, "Selectionnez une image", settings.IMG_BASE_DIR,
            "Image Files (*.png *.jpg *.bmp)")[0].path()

        if self.photo_selected:
            image = QtGui.QPixmap(self.photo_selected)

            if not image.isNull():
                self.photo.setPixmap(image.scaled(QtCore.QSize(120, 160)))
                self.on_change()

    def add_fnc(self):
        """ Called when "Ajouter" is pressed. This disable this button and set
            everything up to add a note.
        """
        if not self.adding:
            self.adding = True
            self.note_list.clearSelection()
            self.add_button.setEnabled(False)
            self.del_button.setEnabled(False)
            self.cotiz_button.setEnabled(False)
            self.current_shown = -1
            self.enable_inputs()
            self.empty_inputs()
            self.current_nickname = None
            for category in api.note_categories.get():
                self.category_selector.addItem(category["name"])

    def save_fnc(self):
        """ Called when "Sauvegarder" is clicked.
        """
        nick = self.nickname_input.text()
        if self.adding:
            if api.notes.add(nick,
                             self.first_name_input.text(),
                             self.name_input.text(),
                             self.mail_input.text(),
                             self.phone_input.text(),
                             self.birthdate_input.text(),
                             self.promo_input.currentText(),
                             self.photo_selected,
                             self.stats_checkbox.isChecked(),
                             self.mails_checkbox.isChecked()):
                self.adding = False
                self.empty_inputs()
                self.add_button.setEnabled(True)
                for category in self.categories_added + [settings.NONCOTIZ_CATEGORY]:
                    api.note_categories.add_notes([nick], category)
                self.categories_added = []
            else:
                gui.utils.error("Erreur", "Impossible d'ajouter la note.")
        else:
            birthdate = datetime.datetime.strptime(self.birthdate_input.text(),
                                                   "%d/%m/%Y").timestamp()
            api.notes.change_values(self.current_nickname,
                                    tel=self.phone_input.text(),
                                    mail=self.mail_input.text(),
                                    birthdate=birthdate,
                                    promo=self.promo_input.currentText(),
                                    nickname=self.nickname_input.text(),
                                    stats_inscription=self.stats_checkbox.isChecked(),
                                    mails_inscription=self.mails_checkbox.isChecked(),
                                    agios_inscription=self.agios_checkbox.isChecked())
            if self.photo_selected:
                api.notes.change_photo(self.nickname_input.text(),
                                       self.photo_selected)
        api.redis.send_message("enibar-notes-mgnt", [nick])
        self.photo_selected = None

    def fill_inputs(self, note):
        """ This fills the inputs on the right with the note infos.
        """
        self.nickname_input.setText(note["nickname"])
        self.first_name_input.setText(note["firstname"])
        self.name_input.setText(note["lastname"])
        self.mail_input.setText(note["mail"])
        self.phone_input.setText(note["tel"])
        self.birthdate_input.setText(datetime.datetime.fromtimestamp(
            note["birthdate"]).strftime("%d/%m/%Y"))
        self.promo_input.setCurrentText(note["promo"])
        path = settings.IMG_BASE_DIR + '/' + note['photo_path']
        image = QtGui.QPixmap(path)

        if not image.isNull():
            image = image.scaled(QtCore.QSize(120, 160), 1)
        self.photo.setPixmap(image)
        self.notes_infos.setText('Note: ' + str(note['note']) + ' €')
        if note['note'] < 0:
            self.notes_infos.setStyleSheet("color: red;")
        else:
            self.notes_infos.setStyleSheet("color: black;")

        self.mails_checkbox.setChecked(note['mails_inscription'])
        self.stats_checkbox.setChecked(note['stats_inscription'])
        self.agios_checkbox.setChecked(note['agios_inscription'])

        self.category_list.clear()
        self.category_selector.clear()
        for category in api.note_categories.get():
            if category["name"] in note["categories"]:
                self.category_list.addItem(category["name"])
            else:
                self.category_selector.addItem(category["name"])

    def on_note_selected(self, note_selected):
        """ This is called when a note is selected
        """
        if self.adding and note_selected != -1:
            self.adding = False
        elif self.adding and note_selected == -1:
            return

        if note_selected == -1:
            return

        self.del_button.setEnabled(True)
        self.current_nickname = self.note_list.item(note_selected).text()
        if note_selected != self.current_shown:
            self.current_shown = note_selected

        note = api.notes.get(lambda x: x["nickname"] ==
                             self.note_list.item(note_selected).text())[0]
        self.disable_inputs_for_editing()
        self.add_button.setEnabled(True)
        self.fill_inputs(note)
        if settings.NONCOTIZ_CATEGORY in note['categories']:
            self.cotiz_button.setEnabled(True)
        else:
            self.cotiz_button.setEnabled(False)

    @gui.auth_prompt_window.ask_auth("manage_notes")
    def del_fnc(self, _):
        """ Called when "Supprimer" is clicked
        """
        api.notes.remove(note['nickname'] for note in list(
            api.notes.get(lambda x: x["nickname"] == self.current_nickname)))
        self.disable_inputs()
        self.empty_inputs()
        self.note_list.refresh(api.notes.get())

    def empty_inputs(self):
        """ This empty all the inputs
        """
        self._inputs_action(lambda x: x.setText(""))
        img = QtGui.QPixmap()
        self.photo.setPixmap(img)
        self.on_change()
        self.save_button.setEnabled(False)
        self.category_list.clear()
        self.category_selector.clear()

    def disable_inputs(self):
        """ This disable all the inputs
        """
        self._inputs_action(lambda x: x.setEnabled(False))
        self.promo_input.setEnabled(False)
        self.photo_button.setEnabled(False)
        self.save_button.setEnabled(False)
        self.cancel_button.setEnabled(False)
        self.add_category_button.setEnabled(False)
        self.remove_category_button.setEnabled(False)
        self.category_selector.setEnabled(False)
        self.cotiz_button.setEnabled(False)

    def enable_inputs(self):
        """ This enable all the inputs
        """
        self._inputs_action(lambda x: x.setEnabled(True))
        self.promo_input.setEnabled(True)
        self.photo_button.setEnabled(True)
        self.save_button.setEnabled(True)
        self.cancel_button.setEnabled(True)
        self.add_category_button.setEnabled(True)
        self.remove_category_button.setEnabled(True)
        self.category_selector.setEnabled(True)

    def disable_inputs_for_editing(self):
        """ This disable all the inputs excepted those allowed to be edited on
            a note
        """
        self.disable_inputs()
        self.mail_input.setEnabled(True)
        self.phone_input.setEnabled(True)
        self.photo_button.setEnabled(True)
        self.nickname_input.setEnabled(True)
        self.promo_input.setEnabled(True)
        self.birthdate_input.setEnabled(True)
        self.add_category_button.setEnabled(True)
        self.remove_category_button.setEnabled(True)
        self.category_selector.setEnabled(True)

    def add_category_fnc(self):
        category = self.category_selector.currentText()
        if not category:
            return

        if self.adding:
            self.categories_added.append(category)
        elif not api.note_categories.add_notes([self.current_nickname], category):
            return

        self.category_list.addItem(category)
        self.category_selector.removeItem(self.category_selector.currentIndex())
        self.on_note_selected(self.current_shown)

    def remove_category_fnc(self):
        try:
            category = self.category_list.currentItem().text()
        except AttributeError:
            return

        if self.adding:
            self.categories_added.remove(category)
        elif not api.note_categories.remove_notes([self.current_nickname], category):
            return

        self.category_selector.addItem(category)
        self.category_list.takeItem(self.category_list.currentRow())
        self.category_selector.model().sort(0)
        self.on_note_selected(self.current_shown)

    def _inputs_action(self, action):
        """ This performs the action on all object of the type Input in the
            object
        """
        for _, obj in self.__dict__.items():
            if isinstance(obj, Input):
                action(obj)

    def cotiz_fnc(self):
        transactions = []
        if api.note_categories.remove_notes([self.current_nickname], "Non cotiz"):
            transactions.append({'note': self.current_nickname,
                             'category': "Note",
                             'product': "cotiz",
                             'price_name': "Solde",
                             'quantity': 1,
                             'price': -settings.COTIZ_PRICE,
                            }
            )
            api.notes.transactions([self.current_nickname], -1.0)
            api.transactions.log_transactions(transactions)
        self.on_note_selected(self.current_shown)

    def group_action_fnc(self):
        self.main_window.menu_bar.notes_action_fnc_no_auth(False, self.performer)


class ManageNotesList(gui.notes_list_widget.NotesList):
    """ This is a NotesList but the refresh function is overwritten.
        It does not try so select something if we're adding a note.
    """

    def refresh(self, notes_list):
        """ Refresh the note list
        """
        selected = self.currentItem()
        if selected:
            selected = selected.text()
        self.clear()
        self.build(notes_list)
        if self.parent().adding:
            return
        try:
            new_selection = self.findItems(selected, QtCore.Qt.MatchExactly)[0]
            self.setCurrentItem(new_selection)
        except IndexError:
            self.setCurrentRow(0)

