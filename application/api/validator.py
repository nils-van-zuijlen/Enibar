"""
Some validators to use with our fancy Input.
"""

from PyQt5 import QtGui
from PyQt5 import QtCore


PHONE_NUMBER = QtGui.QRegExpValidator(QtCore.QRegExp("[0-9]{10}"))
NAME = QtGui.QRegExpValidator(QtCore.QRegExp(".+"))
MAIL = QtGui.QRegExpValidator(QtCore.QRegExp(
    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]{2,4}$"))
BIRTHDATE = QtGui.QRegExpValidator(QtCore.QRegExp((
    r"(^(((0[1-9]|[12][0-8])[\/]"
    r"(0[1-9]|1[012]))|((29|30|31)[\/](0[13578]|1[02]))|"
    r"((29|30)[\/](0[4,6,9]|11)))[\/](19|[2-9][0-9])\d\d$)|"
    r"(^29[\/]02[\/](19|[2-9][0-9])(00|04|08|12|16|20|24|"
    r"28|32|36|40|44|48|52|56|60|64|68|72|76|80|84|88|92|96)$)")))
