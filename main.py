# Doku: https://alva.ur-ahn.de/
import sys
from datetime import datetime
from PyQt5.QtWidgets            import QApplication, QMainWindow, QStyleFactory, QMessageBox
from classes.Graph              import GraphList
from classes.MainWidget         import MainWidget, MainWindowMenu, MainWindowToolbars
from classes.Data               import Data

# Beim Entwickeln, einmalig pro Projekt:
#   python -m venv .venv
# Beim Entwickeln vor jedem Start bzw. Projektwechsel (dann grün (.venv) in Kommandozeile)
#   .venv\Scripts\Activate.ps1
# Vor Auslieferung:
#   pip freeze > requirements.txt
# Auf Gegenseite beim Installieren:
#   python -m venv .venv
#   .venv\Scripts\Activate.ps1
#   pip install -r requirements.txt

# ALLGEMEIN
# - Datumsangaben in convert_date_to_hr => else-Zweig verbesssern
# - Block für weitere Familie erstellen - nötig(?)
# - Löschen einer Ehe (fehlt)
# - Shortcuts
# - alle Farben und Texte (=> Konstanten) in allen Klassen auslagern in Konfiguration
# - combine projects (neu)
# - Menüpunkt mit Checks => Alter Personen < 110; Mutter < 60 bei Geburt der Kinder
# - Menüpunkt mit Statistik
# - PersonWidget muss einen Scrollbalken bekommen und dafür dürfen die Widgets nicht resizable 
#   sein; evtl. liegt das an den GroupBox-Widgets => kann umgebaut werden zu Labeln mit fixer 
#   und gleicher Breite, dann hat man den gleichen Formular-Eindruck
# - StatusWidget anklemmen und dort Nachrichten ausgeben
# - Checks: Personen mit Info, zu welchen Stammbäumen sie ghören, also ob sie mit den anderen Personen 
#   irgendwie verbunden sind, um zu sehen, wer "Karteileichen" sind
# - In Personendetails: Cosima fehlt auf erstem Tab bei mir (Partner und Kinder scheinbar nur bei Ehe gefüllt)
# - mehrere familien und kinder / partner => prüfen, ggf. gehen änderungen nur auf 1. familie
# - self.main.widget in Data auflösen
# - für weitere Feature-Ideen andere Software anschauen, z.B. https://www.youtube.com/watch?v=gjeM32tkcFA
# - ged-Dateien einlesen und ausgeben
# - Ereignisse im Leben einer Person in neuer Tabelle
# - Bilderreferenzen auf Ereignisse (und nicht nur auf Person)
# - bei Datenänderung der Person ändert sich die blaue Zeile oberhalb der Personendetails nicht
# - Konfigurationen in der Datenbank ablegen, gg. mehrere verschiedene Konfigurationen, so dass man 
#   Einstellungen schnell und einfach wechseln kann
# - Maximales Level der angezeigten Personen im Vorfahren-/Nachfahren-Graph
# Graphen
# - klickbar Person
# - klickbar URL(s)
# - Farben selbst konfigurieren
# - Wenn Datum geschätzt, dann Angabe um <jahr> statt am <datum>
# - Nachfahren wieder mit Ehe-Block unter der Person
# - IDs ein-/ausblenden
# - Vorfahren als html (analog Nachfahren)
# - Dreieck hoch und runter als Navigation mit dieser Person und Anzeige Vorfahren und Nachfahren

class Main(QMainWindow):
    # Constraints:
    # - data stored in SQlite database (file-based)
    # - Person IDs are integer (not e.g. @I29@)
    # - No camel case, but separated words
    # - Keep it simple
    # - Genealogische Zeichen aus: https://de.wikipedia.org/wiki/Genealogisches_Zeichen
    # - Icons from: https://commons.wikimedia.org/wiki/Crystal_Clear
    # - in table first column always ID

    def __init__(self, parent=None):
        super(Main, self).__init__(parent)

        # ----- Initiate widgets and other classes ---------------------------------------------- #
        self.data         = Data(self)
        self.widget       = MainWidget(self)
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

        QApplication.setCursorFlashTime(0)  # 0 = no cursor blinking in all widgets
        self.data.init_project()
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
    def create_family(self):
        return self.data.create_family()
    def create_person(self):
        persID = self.data.create_person()
        self.tableWidget.add_person(persID)  # Add Person in PersonList 
        self.widget.set_person(persID)       # Set the new (empty) person having Focus 
    def create_project(self):
        print( "create_project" )
        self.data.create_project()
        self.set_person(-1)
    def delete_father(self, persID):
        self.data.set_indi_attribute(persID, "father", -1)
    def delete_husband(self, famID):
        self.data.set_fam_attribute(famID, "HUSB", -1)
    def delete_mother(self, persID):
        self.data.set_indi_attribute(persID, "mother", -1)
    def delete_wife(self, famID):
        self.data.set_fam_attribute(famID, "WIFE", -1)
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
    def get_ancestors(self):
        return self.data.get_ancestors(self.detailWidget.get_ID())
    def get_birth_full(self, persID):
        if persID in (0, -1): 
            return ""
        person = self.data.get_person(persID) # as dictionary from INDI
        dat = person["BIRT_DATE"]
        plc = person["BIRT_PLAC"]
        return self.get_date_line(dat, plc, "*")
    def get_children(self, persID):
        return self.data.get_children(persID)
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
    def get_descendants(self):
        return self.data.get_descendants(self.detailWidget.get_ID())
    def get_family_as_adult(self, persID):
        return self.data.get_family_as_adult(persID)
    def get_family_ids_as_adult(self, persID):
        return self.data.get_family_ids_as_adult(persID)
    def get_family_attribute(self, famID, attribute):
        return self.data.get_fam_attribute(famID, attribute)
    def get_father(self, persID):
        return self.data.get_indi_attribute(persID, "father")
    def get_firstname(self, persID):
        return self.data.get_indi_attribute(persID, "GIVN")
    def get_id(self):
        return self.detailWidget.get_ID() 
    def get_name_full(self, persID):
        if persID in (0, -1): return ""
        person = self.data.get_person(persID) # as dictionary from INDI
        return person["GIVN"] + " " + person["SURN"]
    def get_marriage_date(self, persID, idx):
        marr = self.data.get_marriage(persID, idx)
        if marr == {}:
            return ""
        
        # return "⚭ am " + marr[0]["MARR_DATE"] + " in " + marr[0]["MARR_PLAC"]
        return marr["MARR_DATE"]
    def get_marriage_place(self, persID, idx):
        marr = self.data.get_marriage(persID, idx)
        if marr == {}:
            return ""
        
        # return "⚭ am " + marr[0]["MARR_DATE"] + " in " + marr[0]["MARR_PLAC"]
        return marr["MARR_PLAC"]    
    def get_mother(self, persID):
        return self.data.get_indi_attribute(persID, "mother")
    def get_partners_blood(self, persID):
        return self.data.get_partners_blood(persID)
    def get_person(self, persID):
        return self.data.get_person(persID)
    def get_person_attribute(self, persID, attribute):
        return self.data.get_indi_attribute(persID, attribute)
    def get_person_for_table(self, persID):
        return self.data.get_person_for_table(persID)
    def get_person_string(self, persID):
        if persID == -1: 
            return ""
        obj = self.data.get_person(persID)
        line = obj["GIVN"] + " " + obj["SURN"] + ", " \
             + self.get_date_line(obj["BIRT_DATE"], obj["BIRT_PLAC"], "*") + ", " \
             + self.get_date_line(obj["DEAT_DATE"], obj["DEAT_PLAC"], "†")
        line = line.strip().replace(",,", ",").strip()
        if line[-1:] == ",":
            line = line[:-1].strip()
        return line
    def get_person_strings_for_value_help(self, exclID, sexNot):
        return self.data.get_person_strings_for_value_help(exclID, sexNot)
    def get_sex(self, persID):
        return self.data.get_indi_attribute(persID, "SEX")
    def get_surname(self, persID):
        return self.data.get_indi_attribute(persID, "SURN")
    def get_table_col_number(self, fieldname):
        return self.data.get_table_col_number(fieldname)
    def get_table_field_texts(self):
        return self.data.get_table_col_texts()
    def get_url(self, persID):
        return self.data.get_indi_attribute(persID, "url")
    def import_action(self):
        print( "import_action" )  # called from MainWindowMenu
        self.data.import_data()
    def is_field_in_table(self, fieldname):
        return self.data.get_table_col_number(fieldname) != -1
    def on_exit(self):
        print( "onExit" )  # called from MainWindowMenu
        self.data.on_exit()
        self.conf.on_exit()
    def open_graph_ancestors(self):
        anc_list, line_list, min_year, max_year = self.get_ancestors()
        graph = self.graphList.add_graph_ancestor_html(anc_list, line_list, min_year, max_year)
        graph.show()
    def open_graph_descendants(self):
        anc_list, line_list, min_year, max_year = self.get_descendants()
        graph = self.graphList.add_graph_descendant_html(anc_list, line_list, min_year, max_year)
        graph.show() 
    def resize_table_columns(self):
        self.tableWidget.resize_table_columns()
    def select_project(self):
        self.data.select_project()    
    def set_comment(self, persID, value):
        self.data.set_indi_attribute(persID, "comment", value)
    def set_father(self, persID, fatherID):
        self.data.set_indi_attribute(persID, "father", fatherID)
    def set_family_attribute(self, famID, attribute, value):
        self.data.set_fam_attribute(famID, attribute, value)
    def set_finished(self, persID, value):
        self.data.set_indi_attribute(persID, "finished", value)
    def set_husband(self, famID, husband):
        self.data.set_fam_attribute(famID, "HUSB", husband)
    def set_marriage_date(self, persID, idx, value):
        marr = self.data.get_marriage(persID, idx)
        if "id" in marr:
            self.data.set_fam_attribute(marr["id"], "MARR_DATE", value)    
    def set_marriage_place(self, persID, idx, value):
        marr = self.data.get_marriage(persID, idx)
        if "id" in marr:
            self.data.set_fam_attribute(marr["id"], "MARR_PLAC", value)
    def set_mother(self, persID, motherID):
        self.data.set_indi_attribute(persID, "mother", motherID)
    def set_person(self, persID, with_list = True):
        self.widget.set_person(persID, with_list)
        self.update_table_row(persID)
    def set_person_attribute(self, persID, attribute, value):
        self.data.set_indi_attribute(persID, attribute, value)
    def set_sex(self, persID, value):
        self.data.set_indi_attribute(persID, "sex", value)
    def set_wife(self, famID, wife):
        self.data.set_fam_attribute(famID, "WIFE", wife)
    def statistik_person(self):
        pass
    def update_table_row(self, persID):
        self.tableWidget.update_table_row(persID)

def main():
    app = QApplication(sys.argv)
    
    # This is because of coloring header line of table in PersonListWidget #
    # https://stackoverflow.com/questions/36196988/color-individual-horizontal-headers-of-qtablewidget-in-pyqt
    app.setStyle(QStyleFactory.create('Fusion'))
    app.setStyleSheet("""
            QMenuBar {
                font-family: "Segoe UI";
                font-size: 11pt;
                font-weight: bold;
            }
            QMenuBar::item {
                padding: 4px 10px;
            }
            QMenuBar::item:selected {
                background: #e0e0e0;
                color: #000;
            }
            QMenu {
                font-family: "Segoe UI";
                font-size: 10pt;
                font-weight: normal;
            }
            QMenu::item:selected {
                background: #e6f2ff;
                color: #000;
            }
            QLabel, QLineEdit {
                min-height:20px;
            }
            QTextEdit {
                min-height:100px;
            }
        """)
    
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
# - Hochzeit eingeben dumpt
# - Menübar einfärben(?) oder Schrift fett / größer(?) => in main(): app.setStyleSheet()
# - Datum geschätzt als Checkbox
# - Datum per 3 Feldern eingeben dd-mm-yyyy, wenn unbekannt, dann bleibt die Komponente 0
# - Personenstring überall einheitlich
# - GraphDescendantHtml => CSS als Datei auslagern
# - Scrollbar fehlt
# - Skalierung nicht lang genug
# - Striche Auswahl direkte oder waagerechte und senkrechte Verbindung
# - Nach Zuordnung Elternteil erfolgt kein Refresh der Zelle in der Tabelle
# - Config als Datenbank statt json Datei
