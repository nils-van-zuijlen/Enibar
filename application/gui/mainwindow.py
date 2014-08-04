"""
Main Window description
"""

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import uic

import api.notes
import time
from .add_note import AddNote
import gui.usermanagment
import gui.consumptionmanagment


class MainWindow(QtWidgets.QMainWindow):
    """
    Main Window
    """
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/mainwindow.ui', self)
        #self.central_widget = CentralWidget(self)
        #self.menu_bar = MenuBar(self)

        #self.setCentralWidget(self.central_widget)
        #self.setMenuBar(self.menu_bar)
        self.notes_list.refresh(api.notes.get_all_shown())
        self.notes_list.itemSelectionChanged.connect(self.select_note)

    def select_note(self):
        widget = self.notes_list.currentItem()
        infos = list(api.notes.get_by_nickname(widget.text()))[0]
        self.note_name.setText(widget.text())
        self.note_mail.setText(infos['mail'])
        self.note_solde.setText("{:.2f} €".format(infos['note']))
        self.note_promo.setText(infos['promo'])
        self.note_phone.setText(infos['tel'])

        image = QtGui.QPixmap('img/coucou.jpg')
        if not image.isNull():
            self.note_photo.setPixmap(image.scaled(QtCore.QSize(120, 160)))
        else:
            self.note_photo.setPixmap(image)
        pass

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
        self.cm_window = None
        self.um_window = None

        self.about = QtWidgets.QMenu("About")
        self.administration = QtWidgets.QMenu("Administration")
        self.administration.addAction(
            "Gestion des utilisateurs",
            self.user_managment
        )
        self.administration.addAction(
            "Gestion des consomations",
            self.consumption_managment
        )

        self.files.addAction("Add a note", add_note_fn)
        self.addMenu(self.files)
        self.addMenu(self.about)
        self.addMenu(self.administration)

    def user_managment(self):
        """ Call user managment window """
        self.um_window = gui.usermanagment.UserManagmentWindow()

    def consumption_managment(self):
        """ Call consumption managment window """
        # Java style
        self.cm_window = gui.consumptionmanagment.ConsumptionManagmentWindow()


def add_note_fn():
    """ Open an AddNote window
    """
    win = AddNote()
    win.exec()

