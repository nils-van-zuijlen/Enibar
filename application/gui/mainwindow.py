"""
Main Window description
"""

from PyQt5 import QtWidgets
import api.notes


class MainWindow(QtWidgets.QMainWindow):
    """
    Main Window
    """
    def __init__(self):
        super().__init__()
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtWidgets.QGridLayout(self.central_widget)

        self.student_list_widget = QtWidgets.QListWidget(self)
        self.layout.addWidget(self.student_list_widget, 0, 0)

        self.student_list = []
        for student in api.notes.get_all_shown():
            self.student_list.append(QtWidgets.QListWidgetItem(
                student["nickname"], self.student_list_widget))

        self.central_widget.setLayout(self.layout)

