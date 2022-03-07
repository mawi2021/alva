# Sources:
#   https://www.geeksforgeeks.org/pyqt5-qtabwidget/
#   https://www.tutorialspoint.com/pyqt/pyqt_qlineedit_widget.htm

import sys
from PyQt5.QtWidgets import QTabWidget, QVBoxLayout, QWidget, QLabel, QLineEdit, QFormLayout, \
                            QHBoxLayout, QVBoxLayout, QPushButton, QPlainTextEdit
 #, QMainWindow, QApplication, QAction, QTableWidget,QTableWidgetItem
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
from classes.GraphList import GraphList

class PersonWidget(QWidget):

    def __init__(self, main):
        super().__init__()
        self.main = main
        self.navigationListBack = []
        self.initUI()
        # TODO: Auslagern in Config.py
        self.bgColorNormal = 'background-color:rgb(255, 254, 235)'
        
        self.ID = ""
        
    def initUI(self):
        self.qTabWidget = QTabWidget()

        # Initialize tab screen
        self.tabGeneral = QWidget()
        self.tabRaw     = QWidget()
        self.tabFamily  = QWidget()
        #self.qTabWidget.resize(300, 200)

        # Add tabs
        self.qTabWidget.addTab(self.tabGeneral, "Allgemein")
        self.addGeneralFields()
        self.qTabWidget.addTab(self.tabRaw, "Raw")
        self.addRawFields()
        self.qTabWidget.addTab(self.tabFamily, "???")

        # Button Line above Tab Widget
        hboxB = QHBoxLayout()

        self.backButton = QPushButton("🡸", self)
        self.backButton.clicked.connect(self.navigateBack)
        hboxB.addWidget(self.backButton)

        self.addButton = QPushButton("Neue Person", self)
        self.addButton.clicked.connect(self.onAddPerson)
        hboxB.addWidget(self.addButton)

        self.addButton = QPushButton("Grafik öffnen", self)
        self.addButton.clicked.connect(self.onOpenGraph)
        hboxB.addWidget(self.addButton)

        # Add box layout, add table to box layout and add box layout to widget
        self.layout = QVBoxLayout()
        self.layout.addLayout(hboxB)
        self.layout.addWidget(self.qTabWidget) 
        self.setLayout(self.layout) 

    def addGeneralFields(self):

        formLayout = QFormLayout()

        # formLayout.addRow("", hboxB)

        # ID
        self.eId = QLabel()
        formLayout.addRow("ID", self.eId)

        # Firstname
        self.eFirstname = QLineEdit()
        formLayout.addRow("Vorname", self.eFirstname)

        # Surname
        self.eSurname = QLineEdit()
        formLayout.addRow("Nachname", self.eSurname)

        # Father
        self.eFather = QLabel()
        self.fatherButton = QPushButton("", self)
        hboxV = QHBoxLayout()
        hboxV.addWidget(self.eFather)
        self.fatherButton.clicked.connect(self.navigateToFather)
        hboxV.addWidget(self.fatherButton)
        formLayout.addRow("Vater", hboxV)

        # Mother
        self.eMother = QLabel()
        self.motherButton = QPushButton("", self)
        hboxM = QHBoxLayout()
        hboxM.addWidget(self.eMother)
        self.motherButton.clicked.connect(self.navigateToMother)
        hboxM.addWidget(self.motherButton)
        formLayout.addRow("Mutter", hboxM)

        self.tabGeneral.setLayout(formLayout)

    def addRawFields(self):
        formLayout = QVBoxLayout()

        self.rawText = QPlainTextEdit()
        self.rawText.setReadOnly(True)
        formLayout.addWidget(self.rawText)

        self.tabRaw.setLayout(formLayout)
    
    def navigateBack(self):
        # print("PersonWidget.navigateBack")

        # ToDo: navigation back does not navigate back in graphical pane
        # beziehungsweise macht das, wenn ich irgendwohin außerhalb des frames klicke

        idx = len(self.navigationListBack) - 2
        if idx >= 0:
            id = self.navigationListBack[idx]
            self.navigationListBack.pop(idx) # remove element from back-array
            self.navigateToPerson(id)
            self.navigationListBack.pop(idx) # remove element from back-array
            self.ID = id

    def navigateToMother(self):
        # print("PersonWidget.navigateToMother")
        id = self.motherButton.text()
        self.navigateToPerson(id)
        self.ID = id        

    def navigateToFather(self):
        # print("PersonWidget.navigateToFather")
        id = self.fatherButton.text()
        self.navigateToPerson(id)
        self.ID = id        

    def navigateToPerson(self,id):
        # print("PersonWidget.navigateToPerson")
        if not id:
            return
        
        self.ID = id
        data = self.main.data.db.selectPerson(id)

        self.eId.setText(data["id"])
        self.eFirstname.setText(data["firstname"])
        self.eSurname.setText(data["surname"])
        self.eFather.setText(data["father"])
        self.fatherButton.setText(data["fatherId"])
        self.eMother.setText(data["mother"])
        self.motherButton.setText(data["motherId"])

        self.rawText.clear()
        self.rawText.insertPlainText(data["raw"])

        # Set correct Navigation
        if id != "":
            self.navigationListBack.append(id)
        else:
            self.navigationListBack = []

        # Set Highlight Color in Table
        self.main.widget.listFrame.highlightLine(id)

        # Update Drawing
        self.main.graphList.setPerson(id)
        self.main.graphList.update()
        
    def refreshBackground(self):
        #print("PersonWidget.refreshBackground")
        self.setStyleSheet(self.bgColorNormal)

    def clearPerson(self):
        # print("PersonWidget.clearPerson")
        self.navigateToPerson("")
        self.ID = ""    

    def onAddPerson(self):
        # New entry in Database
        id = self.main.data.db.getNextPersonId()
        self.ID = id        
        self.main.data.db.insertPerson(id,"","","","","")

        # TODO new row in PersonList
        data = self.main.data.db.selectPersonWithFields(id, self.main.data.fields)
        self.main.widget.listFrame.addTableLine(data)

        # Update in Graph and Person
        self.navigateToPerson(id)
        
    def onOpenGraph(self):
        self.main.graphList.addGraph(self.ID)