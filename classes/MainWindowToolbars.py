# Sorces
#   https://realpython.com/python-menus-toolbars/
#   https://iconarchive.com/show/oxygen-icons-by-oxygen-icons.org.1.html

from PyQt5.QtWidgets import QToolBar, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize

class MainWindowToolbars():

    def __init__(self, parent):
        super().__init__()

        self.parent = parent

        #bgColor       = 'rgb(175, 254, 255)' # Türkis
        bgColor       = 'rgb(7, 244, 247)' # Türkis
        bgBrightColor = 'rgb(224, 255, 255)' # Türkis

        # ----- Left Toolbar -------------------------------------------------------------------- #
        self.navToolBar = QToolBar(parent)
        self.navToolBar.setIconSize(QSize(50, 50));
        parent.addToolBar(Qt.LeftToolBarArea, self.navToolBar)
        self.navToolBar.setStyleSheet('background-color:' + bgColor + ';width:50px;')
        self.navToolBar.setFixedHeight(400)

        fileToolbarAction = QAction(QIcon("icons/file.png"), "Daten", parent)
        fileToolbarAction.triggered.connect(parent.onFileNav)
        self.navToolBar.addAction(fileToolbarAction)

        processToolbarAction = QAction(QIcon("icons/process.png"), "Bearbeiten", parent)
        processToolbarAction.triggered.connect(parent.onProcessNav)
        self.navToolBar.addAction(processToolbarAction)

        viewToolbarAction = QAction(QIcon("icons/lens2.png"), "Ansicht", parent)
        viewToolbarAction.triggered.connect(parent.onViewNav)
        self.navToolBar.addAction(viewToolbarAction)

        outToolbarAction = QAction(QIcon("icons/print2.png"), "Ausgabe", parent)
        outToolbarAction.triggered.connect(parent.onOutNav)
        self.navToolBar.addAction(outToolbarAction)

        toolsToolbarAction = QAction(QIcon("icons/tools2.png"), "Werkzeuge", parent)
        toolsToolbarAction.triggered.connect(parent.onToolsNav)
        self.navToolBar.addAction(toolsToolbarAction)

        helperToolbarAction = QAction(QIcon("icons/help.png"), "Hilfe", parent)
        helperToolbarAction.triggered.connect(parent.onHelperNav)
        self.navToolBar.addAction(helperToolbarAction)

        # ----- 2nd Left Toolbar ---------------------------------------------------------------- #
        self.detailToolBar = QToolBar(parent)
        self.detailToolBar.setIconSize(QSize(40, 40));
        parent.addToolBar(Qt.LeftToolBarArea, self.detailToolBar)
        self.detailToolBar.setStyleSheet('background-color:' + bgBrightColor + ';width:50px;')
        self.switchDetailToolbar("Nav")

    def switchDetailToolbar(self, name):
        self.detailToolBar.clear()

        if name == "Nav":
            self.detailToolBar.addAction(self.parent.menu.newProjectAction)
            self.detailToolBar.addAction(self.parent.menu.openProjectAction)
            self.detailToolBar.addAction(self.parent.menu.combineAction)
            self.detailToolBar.addAction(self.parent.menu.deleteAction)
            self.detailToolBar.addAction(self.parent.menu.saveAction)
            self.detailToolBar.addAction(self.parent.menu.saveasAction)
            self.detailToolBar.addAction(self.parent.menu.importAction)
            self.detailToolBar.addAction(self.parent.menu.exportAction)
            self.detailToolBar.addAction(self.parent.menu.exitAction)
        #elif name == "Process":
        #elif name == "View":
        elif name == "Out":
            self.detailToolBar.addAction(self.parent.menu.printAction)
        #elif name == "Tools":
        #elif name == "Helper":