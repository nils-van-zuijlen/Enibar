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
Load mail model window
======================
"""


from PyQt5 import QtCore, QtWidgets, uic
import api.mail


class LoadMailModelWindow(QtWidgets.QDialog):
    """ Load mail model window. Provide a window with a list of mail model to
    load.
    """
    def __init__(self, parent):
        super().__init__(parent)
        uic.loadUi("ui/load_mail_model_window.ui", self)

        # Load model names from database.
        for model in api.mail.get_models():
            self.model_list.addItem(model['name'])

    def get_selected(self):
        """ Get current selected name
        """
        if self.model_list.currentItem():
            return self.model_list.currentItem().text()
        else:
            return None

    def keyPressEvent(self, event):
        """ Rewrite QDialog KeyPressEvent to enable on the fly model deletion
        """
        if event.key() == QtCore.Qt.Key_Delete:
            item = self.model_list.currentItem()
            if not item:
                return
            if api.mail.delete_model(item.text()):
                self.model_list.takeItem(self.model_list.row(item))

