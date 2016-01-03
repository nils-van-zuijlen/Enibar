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


from PyQt5 import QtCore, QtWidgets, uic
from gui.tree_item_widget import TreeWidget


class SendMailRecapWindow(QtWidgets.QDialog):
    """ Send mail recap window
    """
    def __init__(self, parent, mails):
        super().__init__(parent)
        uic.loadUi('ui/send_mail_recap_window.ui', self)
        for mail in mails:
            widget = TreeWidget(self.mail_list, (
                mail['nickname'],
                mail['mail'],
                mail['status'],
            ))
        self.show()
