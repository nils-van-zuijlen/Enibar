"""
Main Window description
"""

from PyQt5 import QtWidgets
from PyQt5 import QtCore

import api.notes


class MainWindow(QtWidgets.QMainWindow):
    """
    Main Window
    """
    def __init__(self):
        super().__init__()
        self.central_widget = CentralWidget()
        self.menu_bar = MenuBar()

        self.setCentralWidget(self.central_widget)
        self.setMenuBar(self.menu_bar)


class CentralWidget(QtWidgets.QWidget):
    """ Central widget of the MainWindow
        This is where everithing will be """
    def __init__(self):
        super().__init__()

        self.layout = QtWidgets.QGridLayout(self)

        self.student_list_widget = QtWidgets.QListWidget(self)
        self.layout.addWidget(self.student_list_widget, 0, 0)

        self.student_list = []
        for student in api.notes.get_all_shown():
            print(student['note'])
            self.student_list.append(QtWidgets.QListWidgetItem(
                student["nickname"], self.student_list_widget))
            if student['note'] < 0:
                self.student_list[-1].setBackground(QtCore.Qt.red)

        self.setLayout(self.layout)


class MenuBar(QtWidgets.QMenuBar):
    """ MainWindow menu bar """
    def __init__(self):
        super().__init__()
        self.files = QtWidgets.QMenu("Files")
        self.add_note = QtWidgets.QAction("Add a note", self.files)

        self.about = QtWidgets.QMenu("About")

        self.files.addAction(self.add_note)
        self.addMenu(self.files)
        self.addMenu(self.about)

