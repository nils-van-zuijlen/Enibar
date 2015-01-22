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
Mail scheduler window
=====================

"""

from .save_mail_model_window import SaveMailModelWindow
from .load_mail_model_window import LoadMailModelWindow
from PyQt5 import QtCore, QtWidgets, uic, QtGui
import api.mail


class MailSchedulerWindow(QtWidgets.QMainWindow):
    """ Mail scheduler window
    """
    def __init__(self, parent):
        super().__init__(parent)
        uic.loadUi("ui/mail_scheduler_window.ui", self)
        self.filter_selector.set_filter_input(self.filter_input)
        self.build_mail_list()
        self.scheduled_mails_list.setCurrentRow(0)

        self.show()

    def build_mail_list(self):
        """ Build mail list. Fetch all scheduled mail and add them to the list
        """
        self.scheduled_mails_list.clear()
        for mail in api.mail.get_scheduled_mails():
            self.scheduled_mails_list.addItem(mail['name'])

    def on_selected_mail_change(self):
        """ Callback used to detect mail selection change from the list and
        update current mail view.
        """
        item = self.scheduled_mails_list.currentItem()
        if not item:
            self.description_groupbox.setEnabled(False)
            self.status_groupbox.setEnabled(False)
            self.schedule_groupbox.setEnabled(False)
            self.message_groupbox.setEnabled(False)
            self.filter_groupbox.setEnabled(False)
            return
        mail = api.mail.get_unique_scheduled_mails(name=item.text())
        if mail:
            self.name_input.setText(mail['name'])
            self.active_checkbox.setChecked(mail['active'])
            self.schedule_interval.setValue(mail['schedule_interval'])
            self.schedule_interval_unit.setCurrentIndex(api.mail.INTERVAL_UNITS.index(mail['schedule_unit']))
            self.schedule_day.setCurrentIndex(mail['schedule_day'])
            self.filter_selector.setCurrentIndex(mail['filter'])
            self.filter_input.setText(mail['filter_value'])
            self.subject_input.setText(mail['subject'])
            self.sender_input.setText(mail['sender'])
            self.message_input.setPlainText(mail['message'])
        self.description_groupbox.setEnabled(True)
        self.status_groupbox.setEnabled(True)
        self.schedule_groupbox.setEnabled(True)
        self.message_groupbox.setEnabled(True)
        self.filter_groupbox.setEnabled(True)

    def rename_current_mail(self):
        """ REname current selected mail
        """
        item = self.scheduled_mails_list.currentItem()

        if item.text() == self.name_input.text():
            return

        api.mail.rename_scheduled_mail(item.text(), self.name_input.text())
        self.statusbar.showMessage("Mail «{}» renomé en «{}»".format(
            item.text(), self.name_input.text()
        ))
        item.setText(self.name_input.text())

    # Menubar
    def save_model_fnc(self):
        """ Save as model action
        """
        popup = SaveMailModelWindow(self)
        if popup.exec_() and popup.input.text():
            api.mail.save_model(
                popup.input.text(),
                self.subject_input.text(),
                self.message_input.toPlainText(),
                self.filter_selector.currentIndex(),
                self.filter_input.text()
            )

    def load_model_fnc(self):
        """ Load mail action
        """
        popup = LoadMailModelWindow(self)
        if popup.exec_():
            model = popup.get_selected()
            model_data = api.mail.get_unique_model(name=model)
            self.subject_input.setText(model_data['subject'])
            self.message_input.setText(model_data['message'])
            self.filter_selector.setCurrentIndex(model_data['filter'])
            self.filter_input.setText(model_data['filter_value'])

    def new_mail_fnc(self):
        """ Create new mail action
        """
        item = QtWidgets.QListWidgetItem("Brouillon")
        self.scheduled_mails_list.addItem(item)
        self.scheduled_mails_list.setCurrentItem(item)

        # reset all fields
        self.name_input.setText("Brouillon")
        self.active_checkbox.setChecked(False)
        self.schedule_interval.setValue(1)
        self.schedule_interval_unit.setCurrentIndex(0)
        self.schedule_day.setCurrentIndex(0)
        self.filter_selector.setCurrentIndex(0)
        self.filter_input.setText("")
        self.filter_input.setEnabled(False)
        self.subject_input.setText("")
        self.sender_input.setText("cafeteria@enib.fr")
        self.message_input.setPlainText("")

    def save_scheduled_mail_fnc(self):
        """ Save scheduled mail action
        """
        save_success = api.mail.save_scheduled_mails(
            self.name_input.text(),
            self.active_checkbox.isChecked(),
            self.schedule_interval.value(),
            api.mail.INTERVAL_UNITS[self.schedule_interval_unit.currentIndex()],
            self.schedule_day.currentIndex(),
            self.filter_selector.currentIndex(),
            self.filter_input.text(),
            self.subject_input.text(),
            self.sender_input.text(),
            self.message_input.toPlainText(),
            None
        )

        if save_success:
            item = self.scheduled_mails_list.currentItem()
            item.setText(self.name_input.text())
            self.statusbar.showMessage("Mail «{}» sauvegardé".format(
                self.name_input.text()
            ))


class ScheduledMailsList(QtWidgets.QListWidget):
    """ Scheduled mail list. Required to rewrite keyPressEvent in a clean way
    """
    def __init__(self, parent):
        super().__init__(parent)

    def keyPressEvent(self, event):
        """ QtListWidget keyPressEvent used to handle scheduled mail deletion

        :param event QKeyboadEvent: Qt keyboard event
        """
        if event.key() == QtCore.Qt.Key_Delete:
            item = self.currentItem()
            if not item:
                return
            api.mail.delete_scheduled_mail(item.text())
            self.takeItem(self.row(item))
            self.parent().parent().statusbar.showMessage(
                "Mail «{}» supprimé.".format(item.text())
            )
        else:
            super().keyPressEvent(event)

