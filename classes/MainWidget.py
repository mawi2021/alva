from PyQt5.QtWidgets import QWidget, QFrame, QHBoxLayout, QSplitter, QAction, QVBoxLayout, QTextEdit
from PyQt5.QtCore         import Qt, QSize
from PyQt5.QtGui          import QIcon
from PyQt5.QtWidgets      import QToolBar, QAction, QMenuBar

from classes.TableWidget  import TableWidget
from classes.PersonWidget import PersonWidget

# class MainWidget & MainWindowMenu & class MainWindowToolbars

class MainWidget(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main       = main
        self.graphList  = ""

        # ----- Constants ----------------------------------------------------------------------- #
        # TODO: read values from conf file
        self.top = 0
        self.left = 0
        self.width = 1600
        self.height = 1000

        statusBgColorStr = 'background-color:white'

        # ----- Create Main Window Panels ------------------------------------------------------- #
        self.tableW = TableWidget(self.main)
        self.tableW.setContentsMargins(0,0,0,0)

        self.persFrame = PersonWidget(self.main)
        self.persFrame.refreshBackground()

        statusFrame = QFrame()
        statusFrame.setFrameShape(QFrame.StyledPanel)
        statusFrame.setStyleSheet(statusBgColorStr)

        mainSplitter = QSplitter(Qt.Horizontal)
        mainSplitter.addWidget(self.tableW)
        mainSplitter.addWidget(self.persFrame)
        mainSplitter.setSizes([800,800])

        self.status_ta = QTextEdit()     
        self.status_ta.setText("")
        statusLayout = QVBoxLayout(statusFrame)
        statusLayout.addWidget(self.status_ta)

        statusSplitter = QSplitter(Qt.Vertical)
        statusSplitter.addWidget(mainSplitter)
        statusSplitter.addWidget(statusFrame)
        statusSplitter.setSizes([700,50])

        hbox = QHBoxLayout()
        hbox.addWidget(statusSplitter)

        self.layout = hbox
        self.setLayout(self.layout)
    def setGraphList(self, graphList):
        self.graphList = graphList
    def set_person(self, id, with_list = True):
        if with_list:
            self.tableW.select_persID(id)
        self.persFrame.set_person(id)
        # self.graphList.setPerson(id)
    def setPersonNoList(self, id):
        self.persFrame.set_person(id)
        self.graphList.setPerson(id)
    def setPersonNoGraph(self, id):
        self.tableW.set_person(id)
        self.persFrame.set_person(id)
    def add_status_message(self, message):
        self.status_ta.append(message)
    def clear_widgets(self):
        self.tableW.clear_table()
        self.persFrame.set_person(-1)
        self.graphList.clear()
    def closeGraphs(self):
        self.graphList.close()


class MainWindowMenu(QMenuBar):
    def __init__(self, parent):
        super().__init__()

        # ----- F I L E ------------------------------------------------------------------------- #
        fileMenu = self.addMenu("Daten")

        self.newProjectAction = QAction(QIcon("icons/newproject2.png"), "Neu", self)
        self.newProjectAction.triggered.connect(parent.create_project)
        fileMenu.addAction(self.newProjectAction)

        self.openProjectAction = QAction(QIcon("icons/openproject2.png"), "Öffnen", self)
        self.openProjectAction.triggered.connect(parent.select_project)
        fileMenu.addAction(self.openProjectAction)

        fileMenu.addSeparator()

        self.importAction = QAction(QIcon("icons/import2.png"), "Import", self)
        self.importAction.triggered.connect(parent.import_action)
        fileMenu.addAction(self.importAction)

        self.exportAction = QAction(QIcon("icons/export2.png"), "Export", self)
        self.exportAction.triggered.connect(parent.export_action)
        fileMenu.addAction(self.exportAction)

        fileMenu.addSeparator()

        self.exitAction = QAction(QIcon("icons/exit2.png"), "Programm beenden", self)
        self.exitAction.triggered.connect(parent.on_exit)
        fileMenu.addAction(self.exitAction)

        # --------------------------------------------------------------------------------------- #
        personMenu = self.addMenu("Person")

        self.newPersAction = QAction(QIcon("icons/person_new.png"), "Person anlegen", self)
        self.newPersAction.triggered.connect(parent.create_person)
        personMenu.addAction(self.newPersAction)

        self.copyLineAction = QAction(QIcon("icons/person_copy.png"), "Person kopieren", self)
        self.copyLineAction.triggered.connect(parent.copy_person)
        personMenu.addAction(self.copyLineAction)

        self.deleteLineAction = QAction(QIcon("icons/person_delete.png"), "Person löschen", self)
        self.deleteLineAction.triggered.connect(parent.delete_person)
        personMenu.addAction(self.deleteLineAction)

        # --------------------------------------------------------------------------------------- #
        statistikMenu = self.addMenu("Statistik")

        self.anz_pers_Action = QAction(QIcon("icons/personen.png"), "Anzahl Personen", self)
        self.anz_pers_Action.triggered.connect(parent.statistik_person)
        statistikMenu.addAction(self.anz_pers_Action)


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
        self.navToolBar.setFixedHeight(200)

        fileToolbarAction = QAction(QIcon("icons/file.png"), "Daten", parent)
        fileToolbarAction.triggered.connect(self.switch_to_file_menu)
        self.navToolBar.addAction(fileToolbarAction)

        outToolbarAction = QAction(QIcon("icons/person.png"), "Person", parent)
        outToolbarAction.triggered.connect(self.switch_to_person_menu)
        self.navToolBar.addAction(outToolbarAction)

        statToolbarAction = QAction(QIcon("icons/diagram.png"), "Statistik", parent)
        statToolbarAction.triggered.connect(self.switch_to_statistik_menu)
        self.navToolBar.addAction(statToolbarAction)

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
            self.detailToolBar.addAction(self.parent.menu.importAction)
            self.detailToolBar.addAction(self.parent.menu.exportAction)
            self.detailToolBar.addAction(self.parent.menu.exitAction)

        elif name == "Person":
            self.detailToolBar.addAction(self.parent.menu.newPersAction)
            self.detailToolBar.addAction(self.parent.menu.copyLineAction)
            self.detailToolBar.addAction(self.parent.menu.deleteLineAction)      

        elif name == "Statistik":  
            self.detailToolBar.addAction(self.parent.menu.anz_pers_Action)
    def switch_to_file_menu(self):
        self.parent.add_status_message( "switch_to_file_menu" )  # called from MainWindowToolbars
        self.switchDetailToolbar("Nav")
    def switch_to_person_menu(self):
        self.parent.add_status_message( "switch_to_person_menu" )  # called from MainWindowToolbars
        self.switchDetailToolbar("Person")        
    def switch_to_statistik_menu(self):
        self.parent.add_status_message( "switch_to_person_menu" )  # called from MainWindowToolbars
        self.switchDetailToolbar("Statistik")    