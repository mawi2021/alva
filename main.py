# Run: C:\Users\D026557\AppData\Local\Programs\Python\Python39\python.exe main.py
import sys

from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QAction, QMainWindow
from PyQt5.QtCore import Qt
from classes.GraphList import GraphList
from classes.MainWidget import MainWidget
from classes.MainWindowMenu import MainWindowMenu
from classes.MainWindowToolbars import MainWindowToolbars
from classes.Data import Data
from classes.Config import Config

class Main(QMainWindow):

    def __init__(self, parent=None):
        super(Main, self).__init__(parent)

        # ----- Configuration ------------------------------------------------------------------- #
        self.config = Config(self)

        # ----- Data and Database Access -------------------------------------------------------- #
        self.data = Data(self)

        # ----- Panel und Layout ---------------------------------------------------------------- #
        self.widget = MainWidget(self)
        self.setCentralWidget(self.widget)
        self.graphList = GraphList(self)

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
        # Alfa: (A)hnen(l)isten (f)ür (a)lle
        self.setWindowTitle("Alfa")  
        self.setGeometry(self.widget.left, self.widget.top, self.widget.width, self.widget.height)

        self.data.setProject(self.config.DB)

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
    ex = Main()
    ex.show()
    ex.graphList.addGraph("") # Parameter in Brackets: id of central person; here: no person
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()