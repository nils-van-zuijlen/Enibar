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

from PyQt5 import QtCore, QtWidgets, uic, QtGui
import api.notes


class MailSelectorWindow(QtWidgets.QDialog):
    def __init__(self, parent, mails):
        super().__init__(parent)
        uic.loadUi("ui/mail_selector_window.ui", self)
        self.load_list(mails)

    def load_list(self, mails):
        for note in api.notes.get():
            widget = QtWidgets.QTreeWidgetItem(self.mail_list,(
                note['nickname'],
                note['mail'],
                note['firstname'],
                note['lastname']
            ))
            if note['mail'] in mails:
                widget.setSelected(True)

    def get_mail_list(self):
        mails = []
        for line in self.mail_list.selectedIndexes():
            mail = self.mail_list.topLevelItem(line.row()).text(1)
            if mail not in mails:
                mails.append(mail)
        return mails
