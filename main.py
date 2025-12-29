# Doku: https://alva.ur-ahn.de/
import sys
from PyQt5.QtWidgets            import QApplication, QMainWindow, QStyleFactory, QMessageBox
from classes.GraphList          import GraphList
from classes.MainWidget         import MainWidget
from classes.MainWindowMenu     import MainWindowMenu
from classes.MainWindowToolbars import MainWindowToolbars
from classes.Data               import Data
from classes.Config             import Config

# - Umbau @Ixxx@ + @Fxxx@ => numerische ID xxx
# - Umbau Verwaltung per DB statt json Dumps
# - PersonWidget muss einen Scrollbalken bekommen
# - Speichern: das Feld, auf dem gerade der Cursor steht, muss mit berücksichtigt werden
# WEITER MIT PersonWidget >> _onPartnerClick()
# - Eltern-Kind-Strich von Kind zu Partner und nicht zu ohnehin feststehendem Elternteil
# - vielleicht bekommt man die Auswichtung etwas besser hin?
# - Icon zum Neuanlegen einer Person
# - Partner haben keine Bezeichnung ihrer Beziehung zur zentralen Person
# - Großeletern doppelt wegen Partnern
# - hover mit mehr Details?
# - Person- und Partnerdetails aus der Datenbank bereits beim setPerson()
# - Buttons für "Abdocken", "Andocken", "Refresh"(?), Drucken
# - Großeletern-Strich in die Mitte
# - Eltern-Strich in die Mitte (betrifft nicht Onkel und Tanten!)
# - Eltern als ein Elternteil plus Partner ist nicht so doll
# - Beschriftung Verwandtschaftsname nicht fett
# - Vater als letztes und Mutter als erstes Geschwisterkind sortieren, dann beide ohne Lücke 
#   zusammenfügen (was passiert mit anderen Partnern?)
# - Großelternpaare lückenlos zusammenfügen (was passiert mit anderen Partnern?)
# - Stief- und Halbgeschwister?
# - Update-Button
# - Copy&Paste in Personentabelle nicht möglich
# - Neuer Ehepartner => es ist derzeit nicht klar, zu welcher Familie er gehört (_onPartnerClick)
# - Block für weitere Familie erstellen - nötig(?)
# - Kommentar zur Person: wenn man schreibt, sind Schrift, Schriftart, Größe und Hintergrund nicht 
#   einheitlich mit dem Rest
# - Löschen einer Ehe (fehlt)
# - Neues Flag, dass zu der Person noch nicht alle INfos erfasst sind (Eltern <=> Ehen <=> Kinder)
# TODO: Menübar einfärben (?nötig?)
# TODO: Icons im Menü vor dem Text
# TODO: Shortcuts
# TODO: alle Submenüs
# TODO: alle Aktionen
# TODO: self.setWindowIcon(QtGui.QIcon("icon.png"))
# TODO: alle Fraben in allen Klassen auslagern in Konfiguration
# - ID kann auch in anderer als erster Spalte stehen => wichtig in Tabelle

class Main(QMainWindow):

    def __init__(self, parent=None):
        super(Main, self).__init__(parent)

        # ----- Initiate widgets and other classes ---------------------------------------------- #
        self.conf         = Config(self)
        self.data         = Data(self, self.conf.jData)
        self.widget       = MainWidget(self, self.data)
        self.setCentralWidget(self.widget)
        self.graphList    = GraphList(self, self.data)
        self.widget.setGraphList(self.graphList)
        self.tableWidget  = self.widget.listFrame
        self.detailWidget = self.widget.persFrame

        # ----- Menu and all Actions ------------------------------------------------------------ #
        self.menu = MainWindowMenu(self)
        self.setMenuBar(self.menu)
        self.toolbars = MainWindowToolbars(self)

        # Alva: (A)hnen(l)isten (v)on (a)llen
        self.setWindowTitle("Alva")  
        self.setGeometry(self.widget.left, self.widget.top, self.widget.width, self.widget.height)

        if self.conf.get_current_project() != "":
            self.data.setProject(self.conf.jData["currProject"])

        QApplication.setCursorFlashTime(0)  # 0 = no cursor blinking in all widgets

    # ------------------------------------------------------------------------------------------- #
    # ----- A C T I O N S ----------------------------------------------------------------------- #
    # ------------------------------------------------------------------------------------------- #
    def onNewProject(self):
        print( "onNewProject" )
        self.data.newProject()
    def onOpenProject(self):
        print( "onOpenProject" )
        self.data.openProject()
    def onCombining(self):
        print( "onCombining" )
    def on_copy_person(self):
        currID = self.detailWidget.get_ID()              # Current line in table is selected line => get ID
        newID  = self.data.copy_person(currID)           # Get new ID 
        self.detailWidget.setPerson(newID)               # Show new line in Details
        self.tableWidget.add_person(newID)               # Show and select new line in Table
    def on_delete_person(self):
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
            self.data.delete_person(currID)              # delete data in json
            newID = self.data.get_first_persID()         # show first person
            self.detailWidget.setPerson(newID)           # show first person in Details
            self.tableWidget.select_persID(newID)        # select first person in Table
    def on_new_person(self):
        persID = self.data.add_person()
        self.tableWidget.add_person(persID)  # Add Person in PersonList 
        self.widget.setPerson(persID)        # Set the new (empty) person having Focus 
    def onDelete(self):
        pass
    def onSave(self):
        print( "onSave" )
        self.data.save()
    def onSaveAs(self):
        print( "onSaveAs" )
    def onImport(self):
        print( "onImport" )
        self.data.importData()
    def onExport(self):
        print( "onExport" )
        self.data.exportData()
    def onExit(self):
        print( "onExit" )
        ret = self.data.onExit()
        if ret:
            self.conf.onExit()
    def onPrint(self):
        print( "onPrint" )
    def onFileNav(self):
        print( "onFileNav" )
        self.toolbars.switchDetailToolbar("Nav")
    def onProcessNav(self):
        print( "onProcessNav" )
        self.toolbars.switchDetailToolbar("Process")
    def onViewNav(self):
        print( "onViewNav" )
        self.toolbars.switchDetailToolbar("View")
    def onOutNav(self):
        print( "onOutNav" )
        self.toolbars.switchDetailToolbar("Out")        
    def onToolsNav(self):
        print( "onToolsNav" )
        self.toolbars.switchDetailToolbar("Tools")        
    def onHelperNav(self):
        print( "onHelperNav" )
        self.toolbars.switchDetailToolbar("Helper")

    # ---------------------- #
    # ---- G E T T E R ----- #
    # ---------------------- #
    def get_conf_table_fields(self):
        return self.conf.get_conf_table_fields()
    def get_finished(self, persID):
        return self.data.get_finished(persID)
    def get_table_col_number(self, fieldname):
        return self.conf.get_table_col_number(fieldname)
    def get_person_for_table(self, persID):
        return self.data.get_person_for_table(persID)
    def get_sex(self, persID):
        return self.data.getSex(persID)

    # ---------------------- #
    # ---- S E T T E R ----- #
    # ---------------------- #
    def set_finished(self, persID, value):
        self.data.set_finished(persID, value)
    def set_person(self, persID, with_list = True):
        self.widget.setPerson(persID, with_list)

    # ---------------------- #
    # ---- O T H E R S ----- #
    # ---------------------- #
    def copy_person(self, persID):
        self.data.copy_person(persID)
    def fill_table(self, data):
        self.tableWidget.fill_table(data)
    def is_field_in_table(self, fieldname):
        return self.conf.is_field_in_table(fieldname)
    def resize_table_columns(self):
        self.tableWidget.resize_table_columns()
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
