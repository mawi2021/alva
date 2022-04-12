# Sources:
#   https://pythonspot.com/pyqt5-table/

from PyQt5.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QAbstractItemView
from PyQt5.QtGui import QColor
from PyQt5 import Qt

class PersonListWidget(QWidget):

    def __init__(self, main, configData, data):
        super().__init__()
        self.main       = main
        self.configData = configData
        self.data       = data
        
        self.initUI()
        self.bgColorHighlight = QColor(255, 128, 128)
        self.bgColorNormal    = QColor(255,255,255) #255, 254, 235) = hellgelb
        self.bgColorNormalCSS = 'background-color:rgb(255, 255, 255)'
        self.highlightedRows = []
        self.sort = {"col": 0, "asc": True}
        
    def initUI(self):
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(0)
        
        fields = self.main.config.jData["personListFields"]
        self.tableWidget.setColumnCount(len(fields))
        fieldNames = []
        for obj in fields:
            fieldNames.append(fields[obj])
        self.tableWidget.setHorizontalHeaderLabels(fieldNames)
        
        self.tableWidget.setSortingEnabled(True)
        self.tableWidget.horizontalHeader().setSortIndicatorShown( True )
        self.tableWidget.verticalHeader().setVisible(False)

        # Signals #
        self.tableWidget.currentCellChanged.connect(self.onCurrentCellChanged)
        self.tableWidget.cellChanged.connect(self.onChange)

        # Add box layout, add table to box layout and add box layout to widget
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableWidget) 
        self.setLayout(self.layout) 

    def onCurrentCellChanged(self,row,col):
        # is called when navigating in the table via arrow keys #
        for selItem in self.tableWidget.selectedItems():
            id = self.tableWidget.item(selItem.row(),0).text()
            self.main.widget.setPerson(id)
            return # take one row only into cosideration for each double-click event #
        
    def onChange(self):
        # is called when ending editing of a call by enter or tab (= leaving a changed cell) #
        # When changing the color of a cell, this routine is called, too - be aware of possible
        # endless loops!
        for selItem in self.tableWidget.selectedItems():
            id = self.tableWidget.item(selItem.row(),0).text()
            col = selItem.column()
            text = self.tableWidget.item(selItem.row(),col).text()

            # Get old value #
            pers = self.data.getPersonForTable(id)

            # Compare old and new values; cancel, if no content changes #
            if pers[col] == text:
                return

            # A change was done in cell content #
            self.data.updatePersValue("INDI", id, list(self.configData["personListFields"].keys())[col], text)
            
            # Update Person Details
            self.main.widget.setPersonNoList(id)
    
    def addPerson(self,id):
        data = self.data.getPersonForTable(id)
        self.addTableLine(data)        
 
    def setPerson(self,id):
        if id == "": return

        # Un-Highlight formerly highlighted Rows #
        for row in self.highlightedRows:
            item1 = self.tableWidget.item(row,0)
            if item1:
                item1.setBackground(self.bgColorNormal)
        self.highlightedRows = []

        # Highlight selected Row #
        items = self.tableWidget.findItems(id,Qt.Qt.MatchExactly)
        for item in items:
            row = item.row()
            self.highlightedRows.append(row)
            item.setBackground(self.bgColorHighlight)

            # highlight first column in table #
            item2 = self.tableWidget.item(row,0) 
            if item2:
                item2.setBackground(self.bgColorHighlight)

        # Scroll to highlighted item #
        if len(items) > 0:
            self.tableWidget.scrollToItem(item, QAbstractItemView.PositionAtCenter)

    def refreshBackground(self):
        self.setStyleSheet(self.bgColorNormalCSS + ';margin:0px;padding:0px;border:0px;')

    def fillTable(self,dataArr):
        self.tableWidget.clearContents()

        cnt = len(dataArr)
        self.tableWidget.setRowCount(cnt)

        for i in range(cnt):
            line = dataArr[i]
            for j in range(len(line)):
                self.tableWidget.setItem(i, j, QTableWidgetItem(line[j]))

    def updateTableHighlightedRow(self,data):
        # Called from PersonWidget.py #
        for row in self.highlightedRows:
            for i in range(len(data)):
                # Update each column content #
                self.tableWidget.setItem(row, i, QTableWidgetItem(data[i]))   

    def addTableLine(self,data):
        cnt = self.tableWidget.rowCount()
        self.tableWidget.insertRow(cnt)

        for i in range(len(data)):
            self.tableWidget.setItem(cnt, i, QTableWidgetItem(data[i]))

    def clearTable(self):
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)