# Sources:
#   https://pythonspot.com/pyqt5-table/

from PyQt5.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QAbstractItemView
from PyQt5.QtGui import QColor
from PyQt5 import Qt, QtCore

class PersonListWidget(QWidget):

    def __init__(self, main):
        super().__init__()
        self.main = main
        self.initUI()
        self.bgColorHighlight = QColor(255, 128, 128)
        self.bgColorNormal    = QColor(255,255,255) #255, 254, 235) = hellgelb
        self.bgColorNormalCSS = 'background-color:rgb(255, 255, 255)'
        self.highlightedRows = []
        self.sort = {"col": 0, "asc": True}
        
    def initUI(self):
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(0)
        # TODO: Columns from config file (number and content)
        self.tableWidget.setColumnCount(len(self.main.data.fields))
        self.tableWidget.setHorizontalHeaderLabels(self.main.data.fieldNames)
        
        self.tableWidget.setSortingEnabled(True)
        self.tableWidget.horizontalHeader().setSortIndicatorShown( True )

        self.tableWidget.verticalHeader().setVisible(False)

        # table selection change
        self.tableWidget.doubleClicked.connect(self.onDblClick)
        self.tableWidget.cellChanged.connect(self.onChange)

        # Add box layout, add table to box layout and add box layout to widget
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableWidget) 
        self.setLayout(self.layout) 

        # TODO: background-color of table header cells
        # TODO: filtering

    def onDblClick(self):
        #print("PersonListWidget.onDblClick")

        for selItem in self.tableWidget.selectedItems():
            id = self.tableWidget.item(selItem.row(),0).text()
            self.main.widget.persFrame.navigateToPerson(id)

    def onChange(self):
        # print("PersonListWidget.onChange")
        # When changing the color of a cell, this routine is called, too - be aware of possible
        # endless loops!

        for selItem in self.tableWidget.selectedItems():
            id = self.tableWidget.item(selItem.row(),0).text()
            col = selItem.column()
            text = self.tableWidget.item(selItem.row(),col).text()

            # Get old value from DB
            pers = self.main.data.db.selectPerson(id)
            if self.main.data.fields[col] in pers.keys(): 
                dbValue = pers[self.main.data.fields[col]]
            else:
                dbValue = ""

            # Compare old and new values
            if dbValue == text:
                return

            # print("Old: " + dbValue + " <=> New: " + text)
            self.main.data.db.updateTable("pers", id, self.main.data.fields[col], text)

            # Update Person Details
            self.main.widget.persFrame.navigateToPerson(id)
 
    def highlightLine(self,id):
        #print("PersonListWidget.highlightLine(" + str(id) + ")")
        # print(self.highlightedRows)

        if id == "": return

        # Un-Highlight
        for row in self.highlightedRows:
            col = 0
            while col < len(self.main.data.fields):
                item1 = self.tableWidget.item(row,col)
                if item1:
                    item1.setBackground(self.bgColorNormal)
                col = col + 1
        self.highlightedRows = []

        # Highlight
        items = self.tableWidget.findItems(id,Qt.Qt.MatchExactly)
        for item in items:
            row = item.row()
            self.highlightedRows.append(row)
            item.setBackground(self.bgColorHighlight)

            col = 0
            while col < len(self.main.data.fields):
                item2 = self.tableWidget.item(row,col)
                if item2:
                    item2.setBackground(self.bgColorHighlight)
                col = col + 1

        # Scroll to highlighted item
        if len(items) > 0:
            self.tableWidget.scrollToItem(item, QAbstractItemView.PositionAtCenter)

    def refreshBackground(self):
        # print("PersonListWidget.refreshBackground")
        self.setStyleSheet(self.bgColorNormalCSS + ';margin:0px;padding:0px;border:0px;')

    def fillTable(self,dataArr):
        #print("PersonListWidget.fillTable")

        self.tableWidget.clearContents()

        cnt = len(dataArr)
        self.tableWidget.setRowCount(cnt)

        for i in range(cnt):
            line = dataArr[i]
            for j in range(len(line)):
                self.tableWidget.setItem(i, j, QTableWidgetItem(line[j]))

    def addTableLine(self,data):
        cnt = self.tableWidget.rowCount()
        self.tableWidget.insertRow(cnt)

        for i in range(len(data)):
            self.tableWidget.setItem(cnt, i, QTableWidgetItem(data[i]))        

    def clearTable(self):
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)