# Doku: https://alva.ur-ahn.de/
import sys

from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QStyleFactory
from PyQt5.QtCore import Qt
from classes.GraphList import GraphList
from classes.MainWidget import MainWidget
from classes.MainWindowMenu import MainWindowMenu
from classes.MainWindowToolbars import MainWindowToolbars
from classes.Data import Data
from classes.Config import Config

# WEITER MIT PersonWidget >> _onPartnerClick()
# TODO (Graph.py):
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
# TODO (Personenliste)
# - Copy&Paste in Personentabelle nicht möglich
# TODO (PersonWidget)
# - Neuer Ehepartner => es ist derzeit nicht klar, zu welcher Familie er gehört (_onPartnerClick)
# - Block für weitere Familie erstellen - nötig(?)
# - Kommentar zur Person: wenn man schreibt, sind Schrift, Schriftart, Größe und Hintergrund nicht 
#   einheitlich mit dem Rest
# - Löschen einer Ehe (fehlt)
# TODO (allgemein)
# - Ctrl + S >> Speichern
# - Neues Flag, dass zu der Person noch nicht alle INfos erfasst sind (Eltern <=> Ehen <=> Kinder)

class Main(QMainWindow):

    def __init__(self, parent=None):
        super(Main, self).__init__(parent)

        # ----- Configuration ------------------------------------------------------------------- #
        self.config = Config(self)

        # ----- Data and Database Access -------------------------------------------------------- #
        self.data = Data(self, self.config.jData)

        # ----- Panel und Layout ---------------------------------------------------------------- #
        self.widget = MainWidget(self, self.config.jData, self.data)
        self.setCentralWidget(self.widget)
        self.graphList = GraphList(self, self.data)
        self.widget.setGraphList(self.graphList)

        # ----- Menu and all Actions ------------------------------------------------------------ #
        # TODO: Menübar einfärben (?nötig?)
        # TODO: Icons im Menü vor dem Text
        # TODO: Shortcuts
        # TODO: alle Submenüs
        # TODO: alle Aktionen
        self.menu = MainWindowMenu(self)
        self.setMenuBar(self.menu)
        self.toolbars = MainWindowToolbars(self)

        # TODO: self.setWindowIcon(QtGui.QIcon("icon.png"))
        # Alva: (A)hnen(l)isten (v)on (a)llen
        self.setWindowTitle("Alva")  
        self.setGeometry(self.widget.left, self.widget.top, self.widget.width, self.widget.height)

        if self.config.jData["currProject"] != "":
            self.data.setProject(self.config.jData["currProject"])

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
    def onDelete(self):
        print( "onDelete" )
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
            self.config.onExit()
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