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
# pylint: disable=no-value-for-parameter

"""
Panels Widget for Main window
=============================

"""

from PyQt5 import QtWidgets
import api.panels


class Panels(QtWidgets.QTabWidget):
    """ Base class for panels
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.build()

    def build(self):
        """ Build the panel
        """
        for panel in api.panels.get():
            self.addTab(PanelTab(), panel['name'])

    def clear(self):
        """ Dummy
        """
        pass

    def rebuild(self):
        """ Dummy
        """
        pass

    def add_tab(self, name):
        """ Dummy
        """
        pass


class PanelTab(QtWidgets.QWidget):
    """ A tab on the main window
    """
    def __init__(self):
        super().__init__()

