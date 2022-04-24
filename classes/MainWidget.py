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
    def __init__(self, main, configData, data):
        super().__init__()
        self.main       = main
        self.configData = configData
        self.data       = data
        self.graphList  = ""

        # ----- Constants ----------------------------------------------------------------------- #
        # TODO: read values from config file
        self.top = 0
        self.left = 0
        self.width = 2000
        self.height = 1000

        statusBgColorStr = 'background-color:white'

        # ----- Create Main Window Panels ------------------------------------------------------- #
        self.listFrame = PersonListWidget(self.main, self.configData, self.data)
        self.listFrame.setContentsMargins(0,0,0,0)
        self.listFrame.refreshBackground()

        self.persFrame = PersonWidget(self.main, self.configData, self.data)
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
    
    def setPerson(self, id):
        self.listFrame.setPerson(id)
        self.persFrame.setPerson(id)
        self.graphList.setPerson(id)
        
    def setPersonNoList(self, id):
        self.persFrame.setPerson(id)
        self.graphList.setPerson(id)
        
    def setPersonNoGraph(self, id):
        self.listFrame.setPerson(id)
        self.persFrame.setPerson(id)
                
    def addPerson(self):      
        # Called by PersonWidget after pushing button #
          
        # Get new ID #
        id = self.data.getNextPersonId()  
        self.data.addPerson(id)
        
        # Add Perosn in PersonList #
        self.listFrame.addPerson(id)
        
        # Set the new (empty) person having Focus #
        self.setPerson(id)
    
    def clearWidgets(self):
        self.listFrame.clearTable()
        self.persFrame.clearPerson()
        self.graphList.clear()