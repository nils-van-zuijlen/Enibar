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
