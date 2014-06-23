"""
Main Window description
"""

from PyQt5 import QtWidgets


class MainWindow(QtWidgets.QMainWindow):
    """
    Main Window
    """
    def __init__(self):
        # pylint: disable=non-parent-init-called,super-init-not-called
        QtWidgets.QWidget.__init__(self, None)

