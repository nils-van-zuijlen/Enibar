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
Mail widget
===========

A collection of widget which are used in almost all related mail window
"""

from PyQt5 import QtCore, QtWidgets, QtGui
import weakref

from .save_mail_model_window import SaveMailModelWindow
from .load_mail_model_window import LoadMailModelWindow
from .mail_selector_window import MailSelectorWindow


class MailFilterSelector(QtWidgets.QComboBox):
    """ Mail filter selector used to select which filter should be used to match
    notes to send email to. Filters are defined in api.mail
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.filter_input = None

    def set_filter_input(self, filter_input):
        """ Set filter input. Link input to the selector so it can disable or
        enable input when it's relevant and update placeholder text to match
        filter.

        :param MailFilterInput filter_input: Input you wan to link
        """
        self.filter_input = filter_input
        self.filter_input.filter_selector = weakref.proxy(self)

    def update_filter(self, selected):
        """ Qt callback to QCombobox.currentIndexChanged to update linked input
        according to the new selected item

        :param int selected: Current item index
        """
        if not self.filter_input:
            raise ValueError

        if selected == 0:
            self.filter_input.setEnabled(False)
        else:
            self.filter_input.setEnabled(True)
            self.filter_input.setText("")

            if selected == 1:
                self.filter_input.setPlaceholderText(
                    "Cliquez pour selctionner des notes"
                )
            elif selected >= 2:
                self.filter_input.setPlaceholderText("Montant à comparer")


class MailFilterInput(QtWidgets.QLineEdit):
    """ Mail filter input used define filter value.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.filter_selector = None

    def mousePressEvent(self, event):
        """ Rewrite of QLineEdit mouse press event so it open a mail selection
        window when it's clicked and current filter is set to "following notes".
        """
        if not self.filter_selector or self.filter_selector.currentIndex() != 1:
            return

        popup = MailSelectorWindow(self, self.text().split(','))
        if popup.exec():
            mails = popup.get_mail_list()
            self.setText(','.join(mails))

