from PyQt5.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QAbstractItemView
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

class TableWidget(QWidget):
    # Show some data, not editable

    def __init__(self, main):
        super().__init__()
        self.main       = main
        
        self.bgColorHighlight = QColor(237, 235, 194) # = hellgelb
        self.bgColorNormal    = QColor(255, 255, 255) 
        self.bgColorNormalCSS = 'background-color:rgb(255, 255, 255)'
        self.bgColorTableHead = QColor(128, 255, 255) # = hell-türkis
        self.sort = {"col": 0, "asc": True}

        self.table = QTableWidget()

        self.initUI()        
    def initUI(self):
        self.table.setRowCount(0)
        
        fields = self.main.get_conf_table_fields()
        self.table.setColumnCount(len(fields))
        cnt = 0
        for obj in fields:
            headerItem = QTableWidgetItem(fields[obj])
            self.table.setHorizontalHeaderItem(cnt,headerItem)
            cnt += 1
            
        stylesheet = "::section{background-color:rgb(128,255,255);margin:3px;}" #font-weight:bold;font-size:12px;border:1px solid black;}"
        self.table.horizontalHeader().setStyleSheet(stylesheet)
        
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setSortIndicatorShown( True )
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(20)

        # Signals #
        self.table.cellClicked.connect(self._on_cell_clicked) # click on a cell makes it selected (highlighted)

        self.table.setSelectionBehavior(QAbstractItemView.SelectRows) # selection of the whole line 
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # not editable

        # Add box layout, add table to box layout and add box layout to widget
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.table) 
        self.setLayout(self.layout) 

        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
    
    def add_person(self, persID):
        data = self.main.get_person_for_table(persID)
        self._add_line(data)
        row = self._get_row_for_persID(persID) # new row
        self.table.selectRow(row)              # select new row
    def clear_table(self):
        self.table.clearContents()
        self.table.setRowCount(0)
    def delete_person(self, persID):
        row = self._get_row_for_persID(persID)
        self.table.removeRow(row)
    def fill_table(self, dataArr):
        self.table.clearContents()

        cnt = len(dataArr)
        self.table.setRowCount(cnt)
        id_col = self.main.get_table_col_number("id")

        for i in range(cnt):
            line = dataArr[i]
            _, sex = self.main.get_sex(line[id_col])
            for j in range(len(line)):
                if id_col != j:
                    self.table.setItem(i, j, QTableWidgetItem(line[j]))
                    if isinstance(line[j], bool):
                        if line[j]:
                            item = QTableWidgetItem("X")
                            item.setTextAlignment(Qt.AlignCenter)
                            self.table.setItem(i, j, item)
                        else:
                            self.table.setItem(i, j, QTableWidgetItem(""))
                    else:
                        self.table.setItem(i, j, QTableWidgetItem(line[j]))
                else:
                    item = QTableWidgetItem(); 
                    item.setData(Qt.DisplayRole, int(line[j][2:-1])); 
                    item.setTextAlignment(Qt.AlignCenter)  
                    if sex == "m":
                        item.setBackground(QColor(230, 247, 252))
                    elif sex == "w":
                        item.setBackground(QColor(252, 239, 230))
                    self.table.setItem(i, j, item)

        # Sort by ID
        if id_col >= 0:
            self.table.sortItems(id_col, Qt.AscendingOrder)
    def resize_table_columns(self):
        self.table.resizeColumnsToContents()
    def select_persID(self, id):
        if id == "": return

        row = self._get_row_for_persID(id)
        if row == -1: return

        item = self.table.item(row, 0)
        self.table.scrollToItem(item, QAbstractItemView.PositionAtCenter)
        self.table.selectRow(item.row())
    def update_table_row(self, persID):
        line   = self.main.get_person_for_table(persID)
        row    = self._get_row_for_persID(persID)
        id_col = self.main.get_table_col_number("id")
        _, sex = self.main.get_sex(line[id_col])

        for j in range(len(line)):
            if id_col != j:
                if isinstance(line[j], bool):
                    if line[j]:
                        item = QTableWidgetItem("X")
                        item.setTextAlignment(Qt.AlignCenter)
                        self.table.setItem(row, j, item)
                    else:
                        self.table.setItem(row, j, QTableWidgetItem(""))
                else:
                    self.table.setItem(row, j, QTableWidgetItem(line[j]))
            else:
                item = self.table.item(row, j) 
                if sex == "m":
                    item.setBackground(QColor(230, 247, 252))
                elif sex == "w":
                    item.setBackground(QColor(252, 239, 230))
                else:
                    item.setBackground(QColor(255, 255, 255))
                self.table.setItem(row, j, item)
    # ---------------------------- #
    # ----- PRIVATE ROUTINES ----- #
    # ---------------------------- #
    def _on_cell_clicked(self, row, col):
        id_col = self.main.get_table_col_number("id")
        persID = "@I" + self.table.item(row, id_col).text() + "@"
        self.main.set_person(persID, False)
        return # single-click event in table #
    def _add_line(self, line):
        if not line:
            return
        
        row = self.table.rowCount()
        self.table.insertRow(row)   
        id_col = self.main.get_table_col_number("id")
        _, sex = self.main.get_sex(line[id_col])

        for j in range(len(line)):
            if id_col != j:
                self.table.setItem(row, j, QTableWidgetItem(line[j]))
            else:
                item = QTableWidgetItem()
                item.setData(Qt.DisplayRole, int(line[id_col][2:-1]))
                item.setTextAlignment(Qt.AlignCenter)
                if sex == "m":
                    item.setBackground(QColor(230, 247, 252))
                elif sex == "w":
                    item.setBackground(QColor(252, 239, 230))
                self.table.setItem(row, j, item)
    def _get_row_for_persID(self, persID):
        if str(persID[0]) == "@":
            id = persID[2:-1]
        else:
            id = persID

        cnt = self.table.rowCount()
        for row in range(cnt):
            item = self.table.item(row, 0) # unter der Voraussetzung, dass Spalte 0 immer die ID enthält
            if item.text() == str(id):
                return row
        return -1
    def _set_cell(self, persID, value, tech_col_name):
        if persID == "": return
        row = self._get_row_for_persID(persID) # get row
        fields = self.main.get_conf_table_fields() # get column
        col = 0
        for key in fields:
            if key == tech_col_name:
                break
            else:
                col = col + 1
        self.table.setItem(row, col, QTableWidgetItem(value))  # update cell