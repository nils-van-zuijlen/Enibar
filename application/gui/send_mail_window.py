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
Send mail window
================
"""

from PyQt5 import QtCore, QtWidgets, uic
from .mail_selector_window import MailSelectorWindow
import api.mail
from .save_mail_model_window import SaveMailModelWindow
from .load_mail_model_window import LoadMailModelWindow


class SendMailWindow(QtWidgets.QMainWindow):
    """ Main window used to send simple mail.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('ui/send_mail_window.ui', self)

        # Default value for inputs
        self.destinateur_input.setText("cafeteria@enib.fr")
        self.filter_selector.set_filter_input(self.filter_input)

        # Show window
        self.show()

    def send(self):
        """ Send mail
        """
        recipients = api.mail.get_recipients(
            self.filter_selector.currentIndex(),
            self.filter_input.text()
        )
        for recipient in recipients:
            api.mail.send_mail(
                recipient['mail'],
                self.subject_input.text(),
                api.mail.format_message(self.message_input.toPlainText(), recipient),
                self.destinateur_input.text(),
            )

    def save_model(self):
        """ Save mail model
        """
        popup = SaveMailModelWindow(self)
        if popup.exec() and popup.input.text():
            print(api.mail.save_model(
                popup.input.text(),
                self.subject_input.text(),
                self.message_input.toPlainText(),
                self.filter_selector.currentIndex(),
                self.filter_input.text()
            ))

    def open_model(self):
        """ Open mail model. Fill all fields in the ui.
        """
        popup = LoadMailModelWindow(self)
        if popup.exec():
            model = popup.get_selected()
            model_data = api.mail.get_unique_model(name=model)
            self.subject_input.setText(model_data['subject'])
            self.message_input.setText(model_data['message'])
            self.filter_selector.setCurrentIndex(model_data['filter'])
            self.filter_input.setText(model_data['filter_value'])

