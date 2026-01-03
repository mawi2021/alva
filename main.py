# Doku: https://alva.ur-ahn.de/
import sys
from datetime import datetime
from PyQt5.QtWidgets            import QApplication, QMainWindow, QStyleFactory, QMessageBox
from classes.Graph              import GraphList
from classes.MainWidget         import MainWidget, MainWindowMenu, MainWindowToolbars
from classes.Data               import Data
from classes.Config             import Config

# ALLGEMEIN
# - Block für weitere Familie erstellen - nötig(?)
# - Löschen einer Ehe (fehlt)
# - Menübar einfärben(?) oder Schrift fett / größer(?)
# - Shortcuts
# - alle Farben und Texte (=> Konstanten) in allen Klassen auslagern in Konfiguration
# - ID kann auch in anderer als erster Spalte stehen => wichtig in Tabelle
# - combine projects (neu)
# - Datum per 3 Feldern eingeben dd-mm-yyyy, wenn unbekannt, dann bleibt die Komponente 0
# - Datum geschätzt als Checkbox
# - Menüpunkt mit Checks
# - Menüpunkt mit Statistik
# - PersonWidget muss einen Scrollbalken bekommen
# - Status anklemmen
# - Personen mit Info, zu welchen Stammbäumen sie ghören, also ob sie mit den anderen Personen 
#   irgendwie verbunden sind, um zu sehen, wer "Karteileichen" sind
# - In Personendetails: Cosima fehlt auf erstem Tab bei mir
# - Personenstring überall einheitlich
# GRAPH (Ancestors)
# - Skalierung nicht lang genug
# GRAPH (Nachfahren)
# - klickbar

class Main(QMainWindow):
    # Constraints:
    # - data stored in SQlite database (file-based)
    # - Person IDs are integer (not e.g. @I29@)
    # - No camel case, but separated words
    # - Keep it simple
    # - Genealogische Zeichen aus: https://de.wikipedia.org/wiki/Genealogisches_Zeichen
    # - Icons from: https://commons.wikimedia.org/wiki/Crystal_Clear

    def __init__(self, parent=None):
        super(Main, self).__init__(parent)

        # ----- Initiate widgets and other classes ---------------------------------------------- #
        self.conf         = Config(self)
        self.data         = Data(self, self.conf.jData)
        self.widget       = MainWidget(self, self.data)
        self.graphList    = GraphList(self)
        self.tableWidget  = self.widget.tableW
        self.detailWidget = self.widget.persFrame
        self.menu         = MainWindowMenu(self) # used in MainWindowToolbars
        self.toolbars     = MainWindowToolbars(self)

        self.setCentralWidget(self.widget)
        self.widget.setGraphList(self.graphList)
        self.setMenuBar(self.menu)
        self.setWindowTitle("Alva")  # Alva: (A)hnen(l)isten (v)on (a)llen
        self.setGeometry(self.widget.left, self.widget.top, self.widget.width, self.widget.height)

        if self.conf.get_current_project() != "":
            self.data.set_project(self.conf.jData["currProject"])

        QApplication.setCursorFlashTime(0)  # 0 = no cursor blinking in all widgets

    # ------------------------------------------------------------------------------------------- #
    # ----- A C T I O N S ----------------------------------------------------------------------- #
    # ------------------------------------------------------------------------------------------- #

    def clear_widgets(self):
        self.widget.clear_widgets()
    def copy_person(self):
        currID = self.detailWidget.get_ID()              # Current line in table is selected line => get ID
        newID  = self.data.copy_person(currID)           # Get new ID 
        self.detailWidget.set_person(newID)              # Show new line in Details
        self.tableWidget.add_person(newID)               # Show and select new line in Table
    def convert_date_to_hr(self, date_str):
        try:
            obj = datetime.strptime(date_str, "%Y-%m-%d")
            if obj:
                return obj.strftime("%d.%m.%Y")
        except:
            pass
        return date_str
    def create_person(self):
        persID = self.data.create_person()
        self.tableWidget.add_person(persID)  # Add Person in PersonList 
        self.widget.set_person(persID)       # Set the new (empty) person having Focus 
    def create_project(self):
        print( "create_project" )
        self.data.create_project()
        self.set_person(-1)
    def delete_person(self):
        currID = self.detailWidget.get_ID()              # Current line in table is selected line => get ID
        qm = QMessageBox()                               # Dialog to ask, if really delete
        qm.setWindowTitle("Löschen")
        qm.setText("Sind Sie sicher, dass die Person mit ID " + str(currID) + " gelöscht werden soll?")
        qm.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
        btnYes    = qm.button(QMessageBox.Yes)
        btnNo     = qm.button(QMessageBox.No)
        btnYes.setText("Ja")
        btnNo.setText("Nein")
        qm.exec_()
        if qm.clickedButton() == btnYes:
            self.tableWidget.delete_person(currID)       # delete line in Table
            self.data.delete_person(currID)              # delete data in database
            newID = self.tableWidget.get_selected_pers()
            self.detailWidget.set_person(newID)          # show first person in Details
            self.tableWidget.select_persID(newID)        # select first person in Table
    def export(self):
        print( "export" )  # called from MainWindowMenu
        self.data.exportData()
    def fill_table(self, data):
        self.tableWidget.fill_table(data)
    def get_birth_full(self, persID):
        if persID in (0, -1): 
            return ""
        person = self.data.get_person(persID) # as dictionary from INDI
        dat = person["BIRT_DATE"]
        plc = person["BIRT_PLAC"]
        return self.get_date_line(dat, plc, "*")
    def get_conf_table_fields(self):
        return self.conf.get_conf_table_fields()
    def get_date_line(self, date, place, sign):
        dat = self.convert_date_to_hr(date)
        if dat == "" and place == "":
            return ""
        if dat != "":
            dat = sign + " am " + dat
        if place != "":
            place = "in " + place        
        return (dat + " " + place).strip()
    def get_death_full(self, persID):
        if persID in (0, -1): 
            return ""
        person = self.data.get_person(persID) # as dictionary from INDI
        dat = person["DEAT_DATE"]
        plc = person["DEAT_PLAC"]
        return self.get_date_line(dat, plc, "†")
    def get_children(self, persID):
        return self.data.get_children(persID)
    def get_father_id(self, persID):
        return self.data.get_indi_attribute(persID, "father")
    def get_firstname(self, persID):
        return self.data.get_indi_attribute(persID, "GIVN")
    def get_name_full(self, persID):
        if persID in (0, -1): return ""
        person = self.data.get_person(persID) # as dictionary from INDI
        return person["GIVN"] + " " + person["SURN"]
    def get_marriage_for_pair(self, pers1, pers2):
        marr = self.data.get_marriage(pers1, pers2)
        if len(marr) > 0:
            return "⚭ am " + marr[0]["MARR_DATE"] + " in " + marr[0]["MARR_PLAC"]
        return ""
    def get_mother_id(self, persID):
        return self.data.get_indi_attribute(persID, "mother")
    def get_partners_blood(self, persID):
        return self.data.get_partners_blood(persID)
    def get_table_col_number(self, fieldname):
        return self.conf.get_table_col_number(fieldname)
    def get_person_for_table(self, persID):
        return self.data.get_person_for_table(persID)
    def get_sex(self, persID):
        return self.data.get_indi_attribute(persID, "SEX")
    def get_surname(self, persID):
        return self.data.get_indi_attribute(persID, "SURN")
    def import_action(self):
        print( "import_action" )  # called from MainWindowMenu
        self.data.import_data()
    def is_field_in_table(self, fieldname):
        return self.conf.is_field_in_table(fieldname)
    def on_exit(self):
        print( "onExit" )  # called from MainWindowMenu
        self.data.on_exit()
        self.conf.on_exit()
    def open_graph_ancestors(self):
        anc_list, line_list, min_year, max_year = self.data.get_ancestors(self.detailWidget.ID)
        graph = self.graphList.add_graph_ancestor(anc_list, line_list, min_year, max_year)
        graph.show()
    def open_graph_descendants(self):
        anc_list, line_list, min_year, max_year = self.data.get_descendants(self.detailWidget.ID)
        graph = self.graphList.add_graph_descendant(anc_list, line_list, min_year, max_year)
        graph.show()    
    def open_project(self):
        print( "onOpenProject" )# called from MainWindowMenu
        self.data.open_project()    
    def resize_table_columns(self):
        self.tableWidget.resize_table_columns()
    def set_finished(self, persID, value):
        self.data.set_finished(persID, value)
    def set_person(self, persID, with_list = True):
        self.widget.set_person(persID, with_list)
    def statistik_person(self):
        pass
    def update_table_row(self, persID):
        self.tableWidget.update_table_row(persID)

def main():
    app = QApplication(sys.argv)
    
    # This is because of coloring header line of table in PersonListWidget #
    # https://stackoverflow.com/questions/36196988/color-individual-horizontal-headers-of-qtablewidget-in-pyqt
    app.setStyle(QStyleFactory.create('Fusion'))
    
    ex = Main()
    ex.show()
    # ex.graphList.addGraph("") # Parameter in Brackets: id of central person; here: no person
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()


# ----- FEATURES ----- #
# - Ctrl + S >> Speichern
# - ID numerisch und zentriert
# - In Tabelle Farben für Männlich / weiblich in ID-Zelle
# - Umbau @Ixxx@ + @Fxxx@ => numerische ID xxx
# - Aggregierte Klassen in einer Datei (Graph.py, MainWidget.py)
# - Umbau Verwaltung per DB statt json Dumps
# - Neues Flag, dass zu der Person alle Infos erfasst sind (Eltern <=> Ehen <=> Kinder) (fertig)
