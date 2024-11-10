# Sources:
#   https://pythonspot.com/pyqt5-table/

from PyQt5.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QAbstractItemView
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

class PersonListWidget(QWidget):

    def __init__(self, main, configData, data):
        super().__init__()
        self.main       = main
        self.configData = configData
        self.data       = data
        
        self.bgColorHighlight = QColor(237, 235, 194) # = hellgelb
        self.bgColorNormal    = QColor(255, 255, 255) 
        self.bgColorNormalCSS = 'background-color:rgb(255, 255, 255)'
        self.bgColorTableHead = QColor(128, 255, 255) # = hell-türkis
        self.highlightedRows = []
        self.sort = {"col": 0, "asc": True}

        self.initUI()        
    def initUI(self):
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(0)
        
        fields = self.main.config.jData["personListFields"]
        self.tableWidget.setColumnCount(len(fields))
        cnt = 0
        for obj in fields:
            headerItem = QTableWidgetItem(fields[obj])
            self.tableWidget.setHorizontalHeaderItem(cnt,headerItem)
            cnt += 1
            
        stylesheet = "::section{background-color:rgb(128,255,255);padding:8px;font-weight:bold;font-size:12px;border-top:1px solid gray;border-bottom:1px solid gray;}"
        self.tableWidget.horizontalHeader().setStyleSheet(stylesheet)
        
        self.tableWidget.setSortingEnabled(True)
        self.tableWidget.horizontalHeader().setSortIndicatorShown( True )
        self.tableWidget.verticalHeader().setVisible(False)

        # Signals #
        self.tableWidget.currentCellChanged.connect(self._onCurrentCellChanged)
        self.tableWidget.cellChanged.connect(self._onChange)
        self.tableWidget.cellClicked.connect(self._onCellClicked)

        # Add box layout, add table to box layout and add box layout to widget
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableWidget) 
        self.setLayout(self.layout) 
    
    def addPerson(self,id):
        data = self.data.getPersonForTable(id)
        self.addTableLine(data)        
    def addTableLine(self,data):
        cnt = self.tableWidget.rowCount()
        self.tableWidget.insertRow(cnt)

        if data:
            if len(data) > 0:
                for i in range(len(data)):
                    self.tableWidget.setItem(cnt, i, QTableWidgetItem(data[i]))
    def clearTable(self):
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)
    def fillTable(self,dataArr):
        self.tableWidget.clearContents()

        cnt = len(dataArr)
        self.tableWidget.setRowCount(cnt)

        for i in range(cnt):
            line = dataArr[i]
            for j in range(len(line)):
                self.tableWidget.setItem(i, j, QTableWidgetItem(line[j]))
    def refreshBackground(self):
        self.setStyleSheet(self.bgColorNormalCSS + ';margin:0px;padding:0px;border:0px;')
    def setPerson(self,id):
        if id == "": return
        
        newRow = 0
        items = self.tableWidget.findItems(id, Qt.MatchExactly)
        for item in items:
            if item.column() == 0:
                newRow = item.row()
                self.tableWidget.scrollToItem(item, QAbstractItemView.PositionAtCenter)
                break

        # Un-Highlight formerly highlighted Rows #
        for row in self.highlightedRows:
            for col in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(row,col)
                if item:
                    item.setBackground(self.bgColorNormal)
        self.highlightedRows = []

        # Highlight selected Row #
        for col in range(self.tableWidget.columnCount()):
            item = self.tableWidget.item(newRow,col)
            if item:
                item.setBackground(self.bgColorHighlight)
        self.highlightedRows.append(newRow)
    def updateTableHighlightedRow(self,data):
        # Called from PersonWidget.py #
        for row in self.highlightedRows:
            for i in range(len(data)):
                # Update each cell content #
                item = self.tableWidget.item(row,i)
                if item:
                    item.setText(data[i])
                    item.setBackground(self.bgColorHighlight)
    def _onCellClicked(self, row, col):
        for selItem in self.tableWidget.selectedItems():
            id = self.tableWidget.item(selItem.row(),0).text()
            self.main.widget.setPerson(id)
            return # take one row only into cosideration for each single-click event #
    def _onCurrentCellChanged(self,row,col):
        # is called when navigating in the table via arrow keys #
        for selItem in self.tableWidget.selectedItems():
            id = self.tableWidget.item(selItem.row(),0).text()
            self.main.widget.setPerson(id)
            return # take one row only into cosideration for each double-click event #
    def _onChange(self):
        # is called 
        # - when ending editing of a call by enter or tab (= leaving a changed cell)
        # - when changing the color of a cell
        # - When adding new table lines
        # be aware of possible endless loops!
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
