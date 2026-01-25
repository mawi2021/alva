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
        self.persFrame.refresh_background()

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
        self.main = parent

        # ----- F I L E ------------------------------------------------------------------------- #
        self.fileMenu = self.addMenu(parent.get_text("DATA"))

        self.newProjectAction = QAction(QIcon("icons/newproject2.png"), parent.get_text("NEW"), self)
        self.newProjectAction.triggered.connect(parent.create_project)
        self.fileMenu.addAction(self.newProjectAction)

        self.openProjectAction = QAction(QIcon("icons/openproject2.png"), parent.get_text("OPEN"), self)
        self.openProjectAction.triggered.connect(parent.select_project)
        self.fileMenu.addAction(self.openProjectAction)

        self.fileMenu.addSeparator()

        self.importAction = QAction(QIcon("icons/import2.png"), parent.get_text("IMPORT"), self)
        self.importAction.triggered.connect(parent.import_action)
        self.fileMenu.addAction(self.importAction)

        self.exportAction = QAction(QIcon("icons/export2.png"), parent.get_text("EXPORT"), self)
        self.exportAction.triggered.connect(parent.export_action)
        self.fileMenu.addAction(self.exportAction)

        self.fileMenu.addSeparator()

        self.exitAction = QAction(QIcon("icons/exit2.png"), parent.get_text("PROGRAM_END"), self)
        self.exitAction.triggered.connect(parent.on_exit)
        self.fileMenu.addAction(self.exitAction)

        # --------------------------------------------------------------------------------------- #
        self.personMenu = self.addMenu(parent.get_text("PERSON"))

        self.newPersAction = QAction(QIcon("icons/person_new.png"), parent.get_text("CREATE_PERSON"), self)
        self.newPersAction.triggered.connect(parent.create_person)
        self.personMenu.addAction(self.newPersAction)

        self.copyLineAction = QAction(QIcon("icons/person_copy.png"), parent.get_text("COPY_PERSON"), self)
        self.copyLineAction.triggered.connect(parent.copy_person)
        self.personMenu.addAction(self.copyLineAction)

        self.deleteLineAction = QAction(QIcon("icons/person_delete.png"), parent.get_text("DELETE_PERSON"), self)
        self.deleteLineAction.triggered.connect(parent.delete_person)
        self.personMenu.addAction(self.deleteLineAction)

        # --------------------------------------------------------------------------------------- #
        self.statistikMenu = self.addMenu(parent.get_text("STATISTICS"))

        self.anz_pers_Action = QAction(QIcon("icons/personen.png"), parent.get_text("NUMBER_PERSON"), self)
        self.anz_pers_Action.triggered.connect(parent.statistik_person)
        self.statistikMenu.addAction(self.anz_pers_Action)

        # --------------------------------------------------------------------------------------- #
        self.othersMenu = self.addMenu(parent.get_text("OTHERS"))

        self.langu_Action = QAction(QIcon("icons/personen.png"), parent.get_text("LANGUAGE"), self)
        self.langu_Action.triggered.connect(parent.set_language)
        self.othersMenu.addAction(self.langu_Action)
    def refresh_texts(self):
        self.fileMenu.setTitle(self.main.get_text("DATA"))
        self.newProjectAction.setText(self.main.get_text("NEW"))
        self.openProjectAction.setText(self.main.get_text("OPEN"))
        self.importAction.setText(self.main.get_text("IMPORT"))
        self.exportAction.setText(self.main.get_text("EXPORT"))
        self.exitAction.setText(self.main.get_text("PROGRAM_END"))
        self.personMenu.setTitle(self.main.get_text("PERSON"))
        self.newPersAction.setText(self.main.get_text("CREATE_PERSON"))
        self.copyLineAction.setText(self.main.get_text("COPY_PERSON"))
        self.deleteLineAction.setText(self.main.get_text("DELETE_PERSON"))
        self.statistikMenu.setTitle(self.main.get_text("STATISTICS"))
        self.anz_pers_Action.setText(self.main.get_text("NUMBER_PERSON"))
        self.othersMenu.setTitle(self.main.get_text("OTHERS"))
        self.langu_Action.setText(self.main.get_text("LANGUAGE"))


class MainWindowToolbars():
    def __init__(self, parent):
        super().__init__()

        self.main = parent

        bgColor       = 'rgb(7, 244, 247)' 
        bgBrightColor = 'rgb(224, 255, 255)' 

        # ----- Left Toolbar -------------------------------------------------------------------- #
        self.navToolBar = QToolBar(self.main)
        self.navToolBar.setIconSize(QSize(50, 50));
        self.main.addToolBar(Qt.LeftToolBarArea, self.navToolBar)
        self.navToolBar.setStyleSheet('background-color:' + bgColor + ';width:50px;')
        self.navToolBar.setFixedHeight(200)

        self.fileToolbarAction = QAction(QIcon("icons/file.png"), self.main.get_text("DATA"), self.main)
        self.fileToolbarAction.triggered.connect(self.switch_to_file_menu)
        self.navToolBar.addAction(self.fileToolbarAction)

        self.outToolbarAction = QAction(QIcon("icons/person.png"), self.main.get_text("PERSON"), self.main)
        self.outToolbarAction.triggered.connect(self.switch_to_person_menu)
        self.navToolBar.addAction(self.outToolbarAction)

        self.statToolbarAction = QAction(QIcon("icons/diagram.png"), self.main.get_text("STATISTICS"), self.main)
        self.statToolbarAction.triggered.connect(self.switch_to_statistik_menu)
        self.navToolBar.addAction(self.statToolbarAction)

        # ----- 2nd Left Toolbar ---------------------------------------------------------------- #
        self.detailToolBar = QToolBar(self.main)
        self.detailToolBar.setIconSize(QSize(40, 40));
        self.main.addToolBar(Qt.LeftToolBarArea, self.detailToolBar)
        self.detailToolBar.setStyleSheet('background-color:' + bgBrightColor + ';width:50px;')
        self.switchDetailToolbar("Nav")
    def switchDetailToolbar(self, name):
        self.detailToolBar.clear()

        if name == "Nav":
            self.detailToolBar.addAction(self.main.menu.newProjectAction)
            self.detailToolBar.addAction(self.main.menu.openProjectAction)
            self.detailToolBar.addAction(self.main.menu.importAction)
            self.detailToolBar.addAction(self.main.menu.exportAction)
            self.detailToolBar.addAction(self.main.menu.exitAction)

        elif name == "Person":
            self.detailToolBar.addAction(self.main.menu.newPersAction)
            self.detailToolBar.addAction(self.main.menu.copyLineAction)
            self.detailToolBar.addAction(self.main.menu.deleteLineAction)      

        elif name == "Statistik":  
            self.detailToolBar.addAction(self.main.menu.anz_pers_Action)
    def switch_to_file_menu(self):
        self.main.add_status_message( "switch_to_file_menu" )  # called from MainWindowToolbars
        self.switchDetailToolbar("Nav")
    def switch_to_person_menu(self):
        self.main.add_status_message( "switch_to_person_menu" )  # called from MainWindowToolbars
        self.switchDetailToolbar("Person")        
    def switch_to_statistik_menu(self):
        self.main.add_status_message( "switch_to_person_menu" )  # called from MainWindowToolbars
        self.switchDetailToolbar("Statistik")    
    def refresh_texts(self):
        self.fileToolbarAction.setText(self.main.get_text("DATA"))
        self.outToolbarAction.setText(self.main.get_text("PERSON"))
        self.statToolbarAction.setText(self.main.get_text("STATISTICS"))
