# Sources:
#   Splitter-Example: https://codeloop.org/how-to-create-qsplitter-in-pyqt5/#more-321

from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QFrame, QLineEdit, QHBoxLayout, QSplitter, \
                            QSizePolicy, QVBoxLayout, QAction, QMainWindow
import sys
from PyQt5.QtCore import Qt
from classes.PersonListWidget import PersonListWidget
from classes.PersonWidget import PersonWidget

class MainWidget(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main

        # ----- Constants ----------------------------------------------------------------------- #
        # TODO: read values from config file
        self.top = 0
        self.left = 0
        self.width = 1400
        self.height = 1000

        statusBgColorStr = 'background-color:white'

        # ----- Create Main Window Panels ------------------------------------------------------- #
        self.listFrame = PersonListWidget(self.main)
        self.listFrame.setContentsMargins(0,0,0,0)
        self.listFrame.refreshBackground()

        self.persFrame = PersonWidget(self.main)
        self.persFrame.refreshBackground()

        statusFrame = QFrame()
        statusFrame.setFrameShape(QFrame.StyledPanel)
        statusFrame.setStyleSheet(statusBgColorStr)

        mainSplitter = QSplitter(Qt.Horizontal)
        mainSplitter.addWidget(self.listFrame)
        mainSplitter.addWidget(self.persFrame)
        mainSplitter.setSizes([600,300])

        statusSplitter = QSplitter(Qt.Vertical)
        statusSplitter.addWidget(mainSplitter)
        statusSplitter.addWidget(statusFrame)
        statusSplitter.setSizes([700,50])

        hbox = QHBoxLayout()
        hbox.addWidget(statusSplitter)

        self.layout = hbox
        self.setLayout(self.layout)
    