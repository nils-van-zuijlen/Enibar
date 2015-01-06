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
Gui Utils
=========

Somme shortcut to do repetitive actions more easely
"""

from PyQt5 import QtWidgets


def error(title, message=""):
    """ Display error with title and message
    """
    err = QtWidgets.QMessageBox()
    err.setText(title)
    err.setInformativeText(message)
    err.setIcon(QtWidgets.QMessageBox.Critical)
    err.exec()


def valid(title, message=""):
    """ Display validation with title and message
    """
    err = QtWidgets.QMessageBox()
    err.setText(title)
    err.setInformativeText(message)
    err.setIcon(QtWidgets.QMessageBox.Information)
    err.exec()

