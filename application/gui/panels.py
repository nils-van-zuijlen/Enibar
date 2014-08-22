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
Panels Widget for Main window
=============================

"""

from PyQt5 import QtWidgets
import api.panels


class Panels(QtWidgets.QTabWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.build()

    def build(self):
        for panel in api.panels.get():
            self.addTab(PanelTab(), panel['name'])

    def clear(self):
        pass

    def rebuild(self):
        pass

    def add_tab(self, name):
        pass


class PanelTab(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

