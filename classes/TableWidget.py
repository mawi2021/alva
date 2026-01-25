from PyQt5.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QAbstractItemView
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

# Variable and method check done
# Constants not checked

class TableWidget(QWidget):
    # Show some data, not editable

    def __init__(self, main):
        super().__init__()
        self.main = main
        self.table = QTableWidget()
        self.init_UI()        
    def add_person(self, persID):
        data = self.main.get_person_for_table(persID)
        if not data:
            return
        
        row = self.table.rowCount()
        self.table.insertRow(row)

        # fill id column in new row
        id_col = self.main.get_table_col_number("id")
        item = QTableWidgetItem()
        item.setData(Qt.DisplayRole, persID)
        item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, id_col, item)
        self.update_table_row(persID)
     
        self.table.selectRow(row)              # select new row
    def clear_table(self):
        self.table.clearContents()
        self.table.setRowCount(0)
    def delete_person(self, persID):
        row = self.get_row_for_persID(persID)
        self.table.removeRow(row)
    def fill_table(self, dataArr):
        self.table.clearContents()

        cnt = len(dataArr)
        self.table.setRowCount(cnt)
        id_col = self.main.get_table_col_number("id")
        center_fields = self.get_centered_fields()

        for i in range(cnt):
            line = dataArr[i]
            sex = self.main.get_sex(line[id_col])
            for j in range(len(line)):
                if id_col != j:
                    if j in center_fields:  # alignment centered
                        if line[j]:
                            item = QTableWidgetItem(line[j])
                            item.setTextAlignment(Qt.AlignCenter)
                            self.table.setItem(i, j, item)
                        else:
                            self.table.setItem(i, j, QTableWidgetItem(""))
                    elif isinstance(line[j], int):
                        item = QTableWidgetItem(); 
                        item.setData(Qt.DisplayRole, line[j]); 
                        item.setTextAlignment(Qt.AlignCenter)  
                        self.table.setItem(i, j, item)
                    else:
                        self.table.setItem(i, j, QTableWidgetItem(line[j]))
                else:
                    item = QTableWidgetItem(); 
                    item.setData(Qt.DisplayRole, line[j]); 
                    item.setTextAlignment(Qt.AlignCenter)  
                    if sex == "m":
                        item.setBackground(QColor(230, 247, 252))
                    elif sex == "w":
                        item.setBackground(QColor(252, 239, 230))
                    else:
                        item.setBackground(QColor(255, 255, 255))
                    self.table.setItem(i, j, item)

        # Sort by ID
        if id_col >= 0:
            self.table.sortItems(id_col, Qt.AscendingOrder)
    def get_centered_fields(self):
        return (self.main.get_table_col_number("finished"), 
                self.main.get_table_col_number("SEX"),
                self.main.get_table_col_number("no_child"), 
                self.main.get_table_col_number("guess_birth"),
                self.main.get_table_col_number("guess_death"))
    def get_row_for_persID(self, persID):
        cnt = self.table.rowCount()
        id_col = self.main.get_table_col_number("id")
        for row in range(cnt):
            item = self.table.item(row, id_col) 
            if item.text() == str(persID):
                return row
        return -1
    def get_selected_pers(self):
        row    = self.table.currentRow()
        if row == -1:
            return -1
        
        id_col = self.main.get_table_col_number("id")
        item   = self.table.item(row, id_col)
        return int(item.text())
    def init_UI(self):
        self.table.setRowCount(0)
        
        fields = self.main.get_table_field_texts()
        self.table.setColumnCount(len(fields))
        cnt = 0
        for obj in fields:
            headerItem = QTableWidgetItem(obj)
            self.table.setHorizontalHeaderItem(cnt,headerItem)
            cnt += 1
            
        stylesheet = "::section{background-color:rgb(128,255,255);margin:3px;}" #font-weight:bold;font-size:12px;border:1px solid black;}"
        self.table.horizontalHeader().setStyleSheet(stylesheet)
        
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setSortIndicatorShown( True )
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(20)

        # Signals #
        self.table.cellClicked.connect(self.on_cell_clicked) # click on a cell makes it selected (highlighted)

        self.table.setSelectionBehavior(QAbstractItemView.SelectRows) # selection of the whole line 
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # not editable

        # Add box layout, add table to box layout and add box layout to widget
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.table) 
        self.setLayout(self.layout) 

        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
    def on_cell_clicked(self, row, col): # single-click event in table #
        id_col = self.main.get_table_col_number("id")
        persID = int(self.table.item(row, id_col).text())
        self.main.set_person(persID, False)
    def refresh_header_texts(self):
        fields = self.main.get_table_field_texts()
        field_list = []
        for field_txt in fields:
            field_list.append(field_txt)
        self.table.setHorizontalHeaderLabels(field_list)
    def resize_table_columns(self):
        self.table.resizeColumnsToContents()
    def select_persID(self, id):
        if id == "": return

        row = self.get_row_for_persID(id)
        if row == -1: return

        item = self.table.item(row, 0)
        self.table.scrollToItem(item, QAbstractItemView.PositionAtCenter)
        self.table.selectRow(item.row())
    def update_table_row(self, persID):
        if persID == -1:
            return
        line   = self.main.get_person_for_table(persID)
        row    = self.get_row_for_persID(persID)
        id_col = self.main.get_table_col_number("id")
        sex    = self.main.get_sex(line[id_col])
        center_fields = self.get_centered_fields()

        for j in range(len(line)):
            if id_col != j:
                if j in center_fields:  # alignment centered
                    if line[j]:
                        item = QTableWidgetItem(line[j])
                        item.setTextAlignment(Qt.AlignCenter)
                        self.table.setItem(row, j, item)
                    else:
                        self.table.setItem(row, j, QTableWidgetItem(""))
                elif isinstance(line[j], int):
                    item = QTableWidgetItem(); 
                    item.setData(Qt.DisplayRole, line[j]); 
                    item.setTextAlignment(Qt.AlignCenter)  
                    self.table.setItem(row, j, item)
                else:
                    self.table.setItem(row, j, QTableWidgetItem(line[j]))
            else:  # "id"-column
                item = self.table.item(row, j) 
                if sex == "m":
                    item.setBackground(QColor(230, 247, 252))
                elif sex == "w":
                    item.setBackground(QColor(252, 239, 230))
                else:
                    item.setBackground(QColor(255, 255, 255))
                self.table.setItem(row, j, item)
