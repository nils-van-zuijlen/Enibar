# Copyright (C) 2014 Bastien Orivel <b2orivel@enib.fr>
# Copyright (C) 2014 Arnaud Levaufre <a2levauf@enib.fr>
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
PanelManagment Window
====================


"""


from PyQt5 import QtWidgets, QtCore, QtGui, uic

import api.panels
import api.validator
import gui.utils
from .consumptionmanagment import ConsumptionList


class PanelManagment(QtWidgets.QDialog):
    # pylint: disable=too-many-instance-attributes
    """ AddNote window class """
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/paneladmin.ui', self)
        self.panel_list = []

        self.create_panel_list()
        self.show()

    def create_panel_list(self):
        self.panel_list = []
        for panel in api.panels.get():
            self.panel_list.append(QtWidgets.QListWidgetItem(
                panel["name"], self.panels))

    def accept(self):
        if self.name_input.text():
            if not api.panels.add(self.name_input.text()):
                gui.utils.error("Erreur", "Impossible d'ajouter la catégorie")
            else:
                self.panel_list.append(QtWidgets.QListWidgetItem(
                    self.name_input.text(), self.panels))
            self.name_input.setText("")

    def delete(self):
        """ Callback to remove panel
        """
        for index in reversed(self.panels.selectedIndexes()):
            if api.panels.remove(index.data()):
                item = self.panels.takeItem(index.row())
                del item
            else:
                gui.utils.error(
                    "Impossible de suppimer le panel {}".format(
                        index.data()
                    )
                )

    def on_selection(self):
        selected = self.panels.selectedIndexes()
        if len(selected) > 1:
            self.product_list.setEnabled(False)
            self.panel_content.setEnabled(False)
        else:
            self.product_list.setEnabled(True)
            self.panel_content.setEnabled(True)


class GlobalConsumptionList(ConsumptionList):
    def __init__(self, parent):
        super().__init__(parent)

class PanelConsumptionList(ConsumptionList):
    def __init__(self, parent):
        super().__init__(parent)

