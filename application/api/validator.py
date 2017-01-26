# Copyright (C) 2014-2017 Bastien Orivel <b2orivel@enib.fr>
# Copyright (C) 2014-2017 Arnaud Levaufre <a2levauf@enib.fr>
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
Validators
==========

Some validators to use with our fancy Input.
"""

from PyQt5 import QtGui
from PyQt5 import QtCore
from gui.input_widget import Input


PHONE_NUMBER = QtGui.QRegExpValidator(QtCore.QRegExp(r"(?:\+[0-9])?[0-9]{10}"))
NAME = QtGui.QRegExpValidator(QtCore.QRegExp(".+"))
NOTHING = QtGui.QRegExpValidator(QtCore.QRegExp(".*"))
NUMBER = QtGui.QRegExpValidator(QtCore.QRegExp("[0-9]+([,.][0-9]+)?"))
ALL_NUMBER = QtGui.QRegExpValidator(QtCore.QRegExp("-?[0-9]+([,.][0-9]+)?"))
MAIL = QtGui.QRegExpValidator(QtCore.QRegExp(
    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]{2,4}$"))
BIRTHDATE = QtGui.QRegExpValidator(QtCore.QRegExp((
    r"(^(((0[1-9]|[12][0-8]|19)[\/]"
    r"(0[1-9]|1[012]))|((29|30|31)[\/](0[13578]|1[02]))|"
    r"((29|30)[\/](0[4,6,9]|11)))[\/](19|[2-9][0-9])\d\d$)|"
    r"(^29[\/]02[\/](19|[2-9][0-9])(00|04|08|12|16|20|24|"
    r"28|32|36|40|44|48|52|56|60|64|68|72|76|80|84|88|92|96)$)")))


def on_change(cls, button):
    """ Called when an Input goes from red to green
    """
    def wrapper():
        """ Function to be returned
        """
        for _, obj in cls.__dict__.items():
            if isinstance(obj, Input):
                if not obj.valid and obj.isEnabled():
                    button.setEnabled(False)
                    return
        button.setEnabled(True)
    return wrapper

