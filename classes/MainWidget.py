# Sources:
#   Splitter-Example: https://codeloop.org/how-to-create-qsplitter-in-pyqt5/#more-321

from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QFrame, QLineEdit, QHBoxLayout, QSplitter, \
                            QSizePolicy, QVBoxLayout, QAction, QMainWindow
import sys
from PyQt5.QtCore         import Qt
from classes.TableWidget  import TableWidget
from classes.PersonWidget import PersonWidget

class MainWidget(QWidget):
    def __init__(self, main, data):
        super().__init__()
        self.main       = main
        self.data       = data
        self.graphList  = ""

        # ----- Constants ----------------------------------------------------------------------- #
        # TODO: read values from conf file
        self.top = 0
        self.left = 0
        self.width = 2000
        self.height = 1000

        statusBgColorStr = 'background-color:white'

        # ----- Create Main Window Panels ------------------------------------------------------- #
        self.listFrame = TableWidget(self.main)
        self.listFrame.setContentsMargins(0,0,0,0)

        self.persFrame = PersonWidget(self.main, self.data)
        self.persFrame.refreshBackground()

        statusFrame = QFrame()
        statusFrame.setFrameShape(QFrame.StyledPanel)
        statusFrame.setStyleSheet(statusBgColorStr)

        mainSplitter = QSplitter(Qt.Horizontal)
        mainSplitter.addWidget(self.listFrame)
        mainSplitter.addWidget(self.persFrame)
        mainSplitter.setSizes([1000,1000])

        statusSplitter = QSplitter(Qt.Vertical)
        statusSplitter.addWidget(mainSplitter)
        statusSplitter.addWidget(statusFrame)
        statusSplitter.setSizes([700,50])

        hbox = QHBoxLayout()
        hbox.addWidget(statusSplitter)

        self.layout = hbox
        self.setLayout(self.layout)
    def setGraphList(self, graphList):
        self.graphList = graphList
    def setPerson(self, id, with_list = True):
        if with_list:
            self.listFrame.select_persID(id)
        self.persFrame.setPerson(id)
        # self.graphList.setPerson(id)
    def setPersonNoList(self, id):
        self.persFrame.setPerson(id)
        self.graphList.setPerson(id)
    def setPersonNoGraph(self, id):
        self.listFrame.set_person(id)
        self.persFrame.setPerson(id)
    def clearWidgets(self):
        self.listFrame.clear_table()
        self.persFrame.clearPerson()
        self.graphList.clear()
    def closeGraphs(self):
        self.graphList.close()