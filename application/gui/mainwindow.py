"""
Main Window description
"""

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui

import api.notes
import api.validator
import time


class MainWindow(QtWidgets.QMainWindow):
    """
    Main Window
    """
    def __init__(self):
        super().__init__()
        self.central_widget = CentralWidget(self)
        self.menu_bar = MenuBar(self)

        self.setCentralWidget(self.central_widget)
        self.setMenuBar(self.menu_bar)


class CentralWidget(QtWidgets.QWidget):
    """ Central widget of the MainWindow
        This is where everithing will be. """
    def __init__(self, parent):
        super().__init__(parent)

        self.layout = QtWidgets.QGridLayout(self)

        self.notes_list = NotesList(self)
        self.notes_list.refresh(api.notes.get_all_shown())
        self.layout.addWidget(self.notes_list, 0, 0)

        self.student_descr = RightContainer(self)
        self.layout.addWidget(self.student_descr, 0, 1)

        self.setLayout(self.layout)


class RightContainer(QtWidgets.QTabWidget):
    """ Container on the right of the MainWindow """
    def __init__(self, parent):
        super().__init__(parent)


class NotesList(QtWidgets.QListWidget):
    # pylint: disable=too-many-public-methods
    """ Notes list on the left of the MainWindow. """
    def __init__(self, parent):
        super().__init__(parent)
        self.notes = []

    def refresh(self, notes_list):
        """ Fill the list with notes from notes_list, coloring negatives one
            in red """
        self.notes = []
        for note in notes_list:
            self.notes.append(QtWidgets.QListWidgetItem(
                note["nickname"], self))
            if note['note'] < 0:
                self.notes[-1].setBackground(QtCore.Qt.red)
            if time.time() - note["birthdate"] < 18 * 365 * 24 * 3600:
                self.notes[-1].setBackground(QtGui.QColor(255, 192, 203))

        if len(self.notes):
            self.notes[0].setSelected(True)


class MenuBar(QtWidgets.QMenuBar):
    """ MainWindow menu bar """
    def __init__(self, parent):
        super().__init__(parent)
        self.files = QtWidgets.QMenu("Files")

        self.about = QtWidgets.QMenu("About")

        #s elf.files.addAction("Add a note", self.add_note_fn)
        self.addMenu(self.files)
        self.addMenu(self.about)

