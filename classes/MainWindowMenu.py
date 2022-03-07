# Sorces
#   https://realpython.com/python-menus-toolbars/
#   https://iconarchive.com/show/oxygen-icons-by-oxygen-icons.org.1.html


from PyQt5.QtWidgets import QMenuBar, QMenu, QAction
from PyQt5.QtGui import QIcon

class MainWindowMenu(QMenuBar):

    def __init__(self, parent):
        super().__init__()

        # ----- F I L E ------------------------------------------------------------------------- #
        fileMenu = self.addMenu("Daten")

        self.newProjectAction = QAction(QIcon("icons/newproject2.png"), "Neu", self)
        self.newProjectAction.triggered.connect(parent.onNewProject)
        fileMenu.addAction(self.newProjectAction)

        self.openProjectAction = QAction(QIcon("icons/openproject2.png"), "Öffnen", self)
        self.openProjectAction.triggered.connect(parent.onOpenProject)
        fileMenu.addAction(self.openProjectAction)

        self.combineAction = QAction(QIcon("icons/combine2.png"), "Vereinen", self)
        self.combineAction.triggered.connect(parent.onCombining)
        fileMenu.addAction(self.combineAction)

        self.deleteAction = QAction(QIcon("icons/trash2.png"), "Löschen", self)
        self.deleteAction.triggered.connect(parent.onDelete)
        fileMenu.addAction(self.deleteAction)

        fileMenu.addSeparator()

        self.saveAction = QAction(QIcon("icons/disc2.png"), "Speichern", self)
        self.saveAction.triggered.connect(parent.onSave)
        fileMenu.addAction(self.saveAction)

        self.saveasAction = QAction(QIcon("icons/discas2.png"), "Speichern unter", self)
        self.saveasAction.triggered.connect(parent.onSaveAs)
        fileMenu.addAction(self.saveasAction)

        fileMenu.addSeparator()

        self.importAction = QAction(QIcon("icons/import2.png"), "Import", self)
        self.importAction.triggered.connect(parent.onImport)
        fileMenu.addAction(self.importAction)

        self.exportAction = QAction(QIcon("icons/export2.png"), "Export", self)
        self.exportAction.triggered.connect(parent.onExport)
        fileMenu.addAction(self.exportAction)

        fileMenu.addSeparator()

        self.exitAction = QAction(QIcon("icons/exit2.png"), "Programm beenden", self)
        self.exitAction.triggered.connect(parent.onExit)
        fileMenu.addAction(self.exitAction)

        # --------------------------------------------------------------------------------------- #
        processMenu = self.addMenu("Bearbeiten")

        # --------------------------------------------------------------------------------------- #
        viewMenu    = self.addMenu("Ansicht")

        # --------------------------------------------------------------------------------------- #
        outMenu     = self.addMenu("Ausgabe")

        self.printAction = QAction(QIcon("icons/print2.png"), "Drucken", self)
        self.printAction.triggered.connect(parent.onPrint)
        outMenu.addAction(self.printAction)

        # --------------------------------------------------------------------------------------- #
        toolsMenu   = self.addMenu("Werkzeuge")

        # --------------------------------------------------------------------------------------- #
        helperMenu  = self.addMenu("Hilfe")
