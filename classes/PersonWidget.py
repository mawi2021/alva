# Sources:
#   https://www.geeksforgeeks.org/pyqt5-qtabwidget/
#   https://www.tutorialspoint.com/pyqt/pyqt_qlineedit_widget.htm

import sys
from PyQt5.QtWidgets import QTabWidget, QVBoxLayout, QWidget, QLabel, QLineEdit, QFormLayout, \
                            QHBoxLayout, QVBoxLayout, QPushButton, QTextEdit, QRadioButton, \
                            QButtonGroup, QCompleter, QInputDialog, QDialog, QSizePolicy, \
                            QGroupBox
from PyQt5.QtCore import *
import json

class PersonWidget(QWidget):

    def __init__(self, main, configData, data):
        super().__init__()
        self.main       = main
        self.configData = configData
        self.data       = data
        
        self.navigationListBack = []
        self.ID                 = ""
        self.clickTxt           = "<klick hier>"

        self.initUI()
        # TODO: Auslagern in Config.py
        self.bgColorNormal = 'background-color:rgb(255, 254, 235)'
                
    # ----- UI RELATED -------------------------------------------------------------------------- #
    def initUI(self):
        self.qTabWidget = QTabWidget()

        # Initialize tab screen
        self.tabGeneral = QWidget()
        self.tabParents = QWidget()
        self.tabFamily  = QWidget()
        self.tabRaw     = QWidget()

        self.eMarriageDat      = QLineEdit()
        self.eMarriagePlac     = QLineEdit()
        self.ePartner          = QLabel()
        self.ePartnerNavButton = QPushButton("", self)
        self.eChild            = QLabel()
        self.eChildNavButton   = QPushButton("", self)
        self.newChildButton    = QPushButton("", self)
        self.eRelationComment  = QTextEdit()
        self.newRelationship   = QPushButton("", self)

        # Add tabs
        self.eSexGroup = QButtonGroup(objectName="general>sexGroup") # must be globally, otherwise no signal received
        self.qTabWidget.addTab(self.tabGeneral, "Allgemein")
        self._addGeneralFields()
        
        self.qTabWidget.addTab(self.tabParents, "Eltern")
        self._addParentsFields()
        
        self.qTabWidget.addTab(self.tabFamily, "Partner und Kinder")
        self._addFamilyFields()
        
        self.qTabWidget.addTab(self.tabRaw, "Raw")
        self._addRawFields()

        # Button Line above Tab Widget
        hboxB = QHBoxLayout()

        self.backButton = QPushButton("🡸", self)
        self.backButton.clicked.connect(self._navigateBack)
        hboxB.addWidget(self.backButton)

        self.addButton = QPushButton("Neue Person", self)
        self.addButton.clicked.connect(self._onAddPerson)
        hboxB.addWidget(self.addButton)

        self.addButton = QPushButton("Grafik öffnen", self)
        self.addButton.clicked.connect(self._onOpenGraph)
        hboxB.addWidget(self.addButton)

        # Add box layout, add table to box layout and add box layout to widget
        self.layout = QVBoxLayout()
        self.layout.addLayout(hboxB)
        self.layout.addWidget(self.qTabWidget) 
        self.setLayout(self.layout) 

    def _addGeneralFields(self):
        
        eId               = QLabel("", objectName="general>id")
        eFirstname        = QLineEdit("", objectName="general>firstname")
        eSurname          = QLineEdit("", objectName="general>surname")
        eSexMan           = QRadioButton("männlich", objectName="general>sexMan")
        eSexWoman         = QRadioButton("weiblich", objectName="general>sexWoman")
        eSexOhne          = QRadioButton("k.A.", objectName="general>sexOhne")
        eBirthDat         = QLineEdit("", objectName="general>birthDat")
        eBirthPlac        = QLineEdit("", objectName="general>birthPlac")
        eDeathDat         = QLineEdit("", objectName="general>deathDat")
        eDeathPlac        = QLineEdit("", objectName="general>deathPlac")
        persURLs          = QTextEdit(objectName="general>urls")
        persComment       = QTextEdit(objectName="general>comment")
        persMedia         = QTextEdit(objectName="general>media")
        persSource        = QTextEdit(objectName="general>source")

        eFather           = QLabel(objectName="general>father")
        fatherNavButton   = QPushButton("", self, objectName="general>fatherNav")
        eMother           = QLabel(objectName="general>mother")
        motherNavButton   = QPushButton("", self, objectName="general>motherNav")

        marriageDat       = QLineEdit(objectName="general>marrDat")
        marriagePlac      = QLineEdit(objectName="general>marrPlac")
        ePartner          = QLabel(objectName="general>partner")
        ePartnerNavButton = QPushButton("", self)
        eChild            = QLabel(objectName="general>child")
        eChildNavButton   = QPushButton("", self)


        # ----- PERSON ----- #
        persGB         = QGroupBox("Person")
        persGB.setStyleSheet("QGroupBox {font-weight:bold;padding-top:10px;margin:5px;}")
        formPersLayout = QFormLayout()
        persGB.setLayout(formPersLayout)
                
        # ID
        formPersLayout.addRow("ID", eId)

        # Firstname
        eFirstname.editingFinished.connect(self._onEditingFirstnameFinished)
        formPersLayout.addRow("Vorname", eFirstname)

        # Surname
        eSurname.editingFinished.connect(self._onEditingSurnameFinished)
        formPersLayout.addRow("Nachname", eSurname)

        # Sex #
        self.eSexGroup.buttonClicked.connect(self._onSexStateClicked)
        self.eSexGroup.addButton(eSexMan)
        self.eSexGroup.addButton(eSexWoman)
        self.eSexGroup.addButton(eSexOhne)
        hboxS = QHBoxLayout()
        hboxS.addWidget(eSexMan)
        hboxS.addWidget(eSexWoman)
        hboxS.addWidget(eSexOhne)
        formPersLayout.addRow("Geschlecht", hboxS)

        # Birth #
        eBirthDat.editingFinished.connect(self._onEditingBirthDateFinished)
        eBirthPlac.editingFinished.connect(self._onEditingBirthPlaceFinished)
        hboxB = QHBoxLayout()
        hboxB.addWidget(eBirthDat)
        hboxB.addWidget(eBirthPlac)
        formPersLayout.addRow("Geburt: Datum/Ort", hboxB)

        # Death #
        eDeathDat.editingFinished.connect(self._onEditingDeathDateFinished)
        eDeathPlac.editingFinished.connect(self._onEditingDeathPlaceFinished)
        hboxD = QHBoxLayout()
        hboxD.addWidget(eDeathDat)
        hboxD.addWidget(eDeathPlac)
        formPersLayout.addRow("Ableben: Datum/Ort", hboxD)

        # Comment #
        #persURLs.textChanged.connect(self._onPersURLsChanged)
        persURLs.focusOutEvent = self._onPersURLsChanged
        formPersLayout.addRow("URLs", persURLs)
        
        persComment.focusOutEvent = self._onPersCommentChanged
        formPersLayout.addRow("Kommentar", persComment)
        
        persMedia.focusOutEvent = self._onPersMediaChanged
        formPersLayout.addRow("Medien", persMedia)    

        persSource.focusOutEvent = self._onPersSourceChanged
        formPersLayout.addRow("Quellen", persSource)    

        # ----- PARENTS ----- #        
        parentGB         = QGroupBox("Eltern")
        parentGB.setStyleSheet("QGroupBox {font-weight:bold;padding-top:10px;margin:5px;}")
        formParentLayout = QFormLayout()
        parentGB.setLayout(formParentLayout)

        # Father #
        hboxV = QHBoxLayout()
        hboxV.addWidget(eFather)
        eFather.mousePressEvent = self._onFatherClick1
        fatherNavButton.clicked.connect(self._navigateToFather)
        fatherNavButton.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed))
        fatherNavButton.setMaximumWidth(80)
        hboxV.addWidget(fatherNavButton)
        formParentLayout.addRow("Vater", hboxV)

        # Mother #
        hboxM = QHBoxLayout()
        hboxM.addWidget(eMother)
        eMother.mousePressEvent = self._onMotherClick1
        motherNavButton.clicked.connect(self._navigateToMother)
        motherNavButton.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed))
        motherNavButton.setMaximumWidth(80)
        hboxM.addWidget(motherNavButton)
        formParentLayout.addRow("Mutter", hboxM)
        
        # ----- FAMILY ----- #
        familyGB         = QGroupBox("Partner und Kinder")
        familyGB.setStyleSheet("QGroupBox {font-weight:bold;margin:5px;padding-top:10px; width:100%;}")
        formFamilyLayout = QFormLayout()
        familyGB.setLayout(formFamilyLayout)        
        
        # Hochzeit #
        marriageDat.editingFinished.connect(self._onEditingMarriageDateFinished)
        marriagePlac.editingFinished.connect(self._onEditingMarriagePlaceFinished)
        hboxMa = QHBoxLayout()
        hboxMa.addWidget(marriageDat)
        hboxMa.addWidget(marriagePlac)
        formFamilyLayout.addRow("Hochzeit: Datum/Ort", hboxMa)
        
        # Partner #
        hboxPar = QHBoxLayout()
        hboxPar.addWidget(ePartner)
        ePartner.mousePressEvent = self._onPartnerClick
        ePartnerNavButton.clicked.connect(self._navigateToPartner)
        ePartnerNavButton.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed))
        ePartnerNavButton.setMaximumWidth(80)
        hboxPar.addWidget(ePartnerNavButton)
        formFamilyLayout.addRow("Partner", hboxPar)
        
        # Child #
        hboxCh = QHBoxLayout()
        hboxCh.addWidget(eChild)
        eChild.mousePressEvent = self._onChildClick
        eChildNavButton.clicked.connect(self._navigateToChild)
        eChildNavButton.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed))
        eChildNavButton.setMaximumWidth(80)
        hboxCh.addWidget(eChildNavButton)
        formFamilyLayout.addRow("Kind", hboxCh)
        
        # ----- end ----- #
        globLayout = QVBoxLayout()
        globLayout.addWidget(persGB)
        globLayout.addWidget(parentGB)   
        globLayout.addWidget(familyGB)   
        self.tabGeneral.setLayout(globLayout)

    def _addFamilyFields(self):
        # ----- FAMILY ----- #
        formFamilyLayout = QFormLayout()
        
        # Hochzeit #
        self.eMarriageDat.editingFinished.connect(self._onEditingMarriageDateFinished)
        self.eMarriagePlac.editingFinished.connect(self._onEditingMarriagePlaceFinished)
        hboxMa = QHBoxLayout()
        hboxMa.addWidget(self.eMarriageDat)
        hboxMa.addWidget(self.eMarriagePlac)
        formFamilyLayout.addRow("Hochzeit: Datum/Ort", hboxMa)
        
        # Partner #
        hboxPar = QHBoxLayout()
        hboxPar.addWidget(self.ePartner)
        self.ePartner.mousePressEvent = self._onPartnerClick
        self.ePartnerNavButton.clicked.connect(self._navigateToPartner)
        self.ePartnerNavButton.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed))
        self.ePartnerNavButton.setMaximumWidth(80)
        hboxPar.addWidget(self.ePartnerNavButton)
        formFamilyLayout.addRow("Partner", hboxPar)
        
        # Child #
        hboxCh = QHBoxLayout()
        hboxCh.addWidget(self.eChild)
        self.eChild.mousePressEvent = self._onChildClick
        self.eChildNavButton.clicked.connect(self._navigateToChild)
        self.eChildNavButton.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed))
        self.eChildNavButton.setMaximumWidth(80)
        hboxCh.addWidget(self.eChildNavButton)
        formFamilyLayout.addRow("Kind", hboxCh)

        # Additional Child - Button #
        self.newChildButton.setText("Zeile für weiteres Kind erstellen")
        self.newChildButton.clicked.connect(self._onNewChild)
        formFamilyLayout.addRow("Weiteres Kind", self.newChildButton)

        # Comment on Family #
        self.eRelationComment.textChanged.connect(self._onEditingRelationCommentFinished)
        formFamilyLayout.addRow("Kommentar", self.eRelationComment)

        # Additional Family - Button #
        self.newRelationship.setText("Block für weitere Familie erstellen")
        self.newRelationship.clicked.connect(self._onNewRelationshipClick)
        formFamilyLayout.addRow("", self.newRelationship)

        self.tabFamily.setLayout(formFamilyLayout)

    def _addParentsFields(self):

        eFather           = QLabel(objectName="parents>father")
        fatherNavButton   = QPushButton("", self, objectName="parents>fatherNav")
        fatherComment     = QTextEdit(objectName="parents>fatherComment")
        eMother           = QLabel(objectName="parents>mother")
        motherNavButton   = QPushButton("", self, objectName="parents>motherNav")
        motherComment     = QTextEdit(objectName="parents>motherComment")
        
        # ----- PARENTS ----- #        
        formParentLayout = QFormLayout()

        # Father #
        hboxV = QHBoxLayout()
        hboxV.addWidget(eFather)
        eFather.mousePressEvent = self._onFatherClick2
        fatherNavButton.clicked.connect(self._navigateToFather)
        fatherNavButton.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed))
        fatherNavButton.setMaximumWidth(80)
        hboxV.addWidget(fatherNavButton)
        formParentLayout.addRow("Vater", hboxV)
        fatherComment.focusOutEvent = self._onFatherCommentChanged
        formParentLayout.addRow("Kommentar", fatherComment)

        # Mother #
        hboxM = QHBoxLayout()
        hboxM.addWidget(eMother)
        eMother.mousePressEvent = self._onMotherClick2
        motherNavButton.clicked.connect(self._navigateToMother)
        motherNavButton.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed))
        motherNavButton.setMaximumWidth(80)
        hboxM.addWidget(motherNavButton)
        formParentLayout.addRow("Mutter", hboxM)
        motherComment.focusOutEvent = self._onMotherCommentChanged
        formParentLayout.addRow("Kommentar", motherComment)

        self.tabParents.setLayout(formParentLayout)
        
    def _addRawFields(self):
        formLayout = QVBoxLayout()

        self.rawText = QTextEdit()
        self.rawText.setReadOnly(True)
        formLayout.addWidget(self.rawText)

        self.tabRaw.setLayout(formLayout)

    # ------------------------------------------------------------------------------------------- #
    # ----- P U B L I C ------------------------------------------------------------------------- #
    # ------------------------------------------------------------------------------------------- #

    def setPerson(self,id):
        # Called from MainWidget.py #
        self.ID = id
        ret1, data = self.data.getPerson(id)

        wid = self.tabGeneral.findChild(QLabel,"general>id")
        wid.setText(id)
        
        # Name #
        ret, name = self.data.getName(id)
        widF = self.tabGeneral.findChild(QLineEdit,"general>firstname")
        widS = self.tabGeneral.findChild(QLineEdit,"general>surname")
        if ret:
            widF.setText(name["firstname"])
            widS.setText(name["surname"])
        else:
            widF.setText("")
            widS.setText("")
            
        # Sex #
        ret, sex = self.data.getSex(id)
        widM = self.tabGeneral.findChild(QRadioButton,"general>sexMan")
        widW = self.tabGeneral.findChild(QRadioButton,"general>sexWoman")
        widO = self.tabGeneral.findChild(QRadioButton,"general>sexOhne")
        if sex == "m":           
            widM.setChecked(True)
        elif sex == "w" or sex == "f":
            widW.setChecked(True)
        elif sex == "":
            widO.setChecked(True)
            
        # Birth #
        ret, birth = self.data.getBirthData(id)
        wid1 = self.tabGeneral.findChild(QLineEdit,"general>birthDat")
        wid2 = self.tabGeneral.findChild(QLineEdit,"general>birthPlac")
        if ret:    
            wid1.setText(birth.get("date",""))
            wid2.setText(birth.get("place",""))
        else:
            wid1.setText("")
            wid2.setText("")
            
        # Death #
        ret, death = self.data.getDeathData(id)
        wid1 = self.tabGeneral.findChild(QLineEdit,"general>deathDat")
        wid2 = self.tabGeneral.findChild(QLineEdit,"general>deathPlac")
        if ret:
            wid1.setText(death.get("date",""))
            wid2.setText(death.get("place",""))
        else:
            wid1.setText("")
            wid2.setText("")
            
        # URLs #
        ret, value = self.data.getUrl(id)
        wid = self.tabGeneral.findChild(QTextEdit,"general>urls")
        wid.setText(value)
        
        # Comment #
        ret, value = self.data.getComment(id)
        wid = self.tabGeneral.findChild(QTextEdit,"general>comment")
        wid.setText(value)
        
        # Media #
        ret, value = self.data.getMedia(id)
        wid = self.tabGeneral.findChild(QTextEdit,"general>media")
        wid.setText(value)
        
        # Source #
        ret, value = self.data.getSource(id)
        wid = self.tabGeneral.findChild(QTextEdit,"general>source")
        wid.setText(value)
        
            
        # Parents #
        widF   = self.tabGeneral.findChild(QLabel,"general>father")
        widFB  = self.tabGeneral.findChild(QPushButton,"general>fatherNav")      
        widF2  = self.tabParents.findChild(QLabel,"parents>father")
        widFB2 = self.tabParents.findChild(QPushButton,"parents>fatherNav")      
        ret, idF = self.data.getFatherId(self.ID)
        txt = self.data.getPersStr(idF)
        if txt != "":
            widF.setText(txt)
            widFB.setText(idF)
            widF2.setText(txt)
            widFB2.setText(idF)
        else:
            widF.setText(self.clickTxt)
            widFB.setText("")
            widF2.setText(self.clickTxt)
            widFB2.setText("")
            
        widM  = self.tabGeneral.findChild(QLabel,"general>mother")
        widMB = self.tabGeneral.findChild(QPushButton,"general>motherNav")
        widM2  = self.tabParents.findChild(QLabel,"parents>mother")
        widMB2 = self.tabParents.findChild(QPushButton,"parents>motherNav")
        ret, idM = self.data.getMotherId(self.ID)
        txt = self.data.getPersStr(idM)
        if txt != "":
            widM.setText(txt)
            widMB.setText(idM)
            widM2.setText(txt)
            widMB2.setText(idM)
        else:
            widM.setText(self.clickTxt)
            widMB.setText("")
            widM2.setText(self.clickTxt)
            widMB2.setText("")

        # Partner, Marriage and Children #
        self.ePartner.setText(self.clickTxt)
        self.eChild.setText(self.clickTxt)

        self.rawText.clear()
        
        if ret1:
            self.rawText.insertPlainText(json.dumps(data))
            self.navigationListBack.append(id)
        else:
            self.navigationListBack = []

    def clearPerson(self):
        self.main.widget.setPerson("")
        self.ID = ""    

    def refreshBackground(self):
        self.setStyleSheet(self.bgColorNormal)
        
    # ------------------------------------------------------------------------------------------- #
    # ----- P R I V A T E ----------------------------------------------------------------------- #
    # ------------------------------------------------------------------------------------------- #

    # ----- NAVIGATION TO PERSON ---------------------------------------------------------------- #
    def _navigateBack(self):
        # ToDo: navigation back does not navigate back in graphical pane
        # beziehungsweise macht das, wenn ich irgendwohin außerhalb des frames klicke

        idx = len(self.navigationListBack) - 2
        if idx >= 0:
            id = self.navigationListBack[idx]
            self.navigationListBack.pop(idx) # remove element from back-array
            self.main.widget.setPerson(id)
            self.navigationListBack.pop(idx) # remove element from back-array
            self.ID = id
    def _navigateToMother(self):
        ret, idMother = self.data.getMotherId(self.ID)
        if ret:
            self.main.widget.setPerson(idMother)
            self.ID = idMother
    def _navigateToFather(self):
        ret, idFather = self.data.getFatherId(self.ID)
        if ret:
            self.main.widget.setPerson(idFather)
            self.ID = idFather
    def _navigateToPartner(self):
        pass
    def _navigateToChild(self):
        pass

    # ----- BUTTON EVENTS ----------------------------------------------------------------------- #
    def _onAddPerson(self):
        self.main.widget.addPerson()
    def _onOpenGraph(self):
        self.main.graphList.addGraph(self.ID)
    def _onFatherClick1(self, event):
        wid  = self.tabGeneral.findChild(QLabel,"general>father")
        self._onFatherClick(wid.text())
    def _onFatherClick2(self, event):
        wid  = self.tabParents.findChild(QLabel,"parents>father")
        self._onFatherClick(wid.text())
    def _onFatherClick(self,widText):
        # Show dialog and save data #
        ret, id, text = self._showSelectPersDlg("w", "Vater", [self.ID], widText)
        
        if ret:
            widB  = self.tabGeneral.findChild(QPushButton,"general>fatherNav")
            widB.setText(id)
            widB  = self.tabParents.findChild(QPushButton,"parents>fatherNav")
            widB.setText(id)
            
            wid  = self.tabGeneral.findChild(QLabel,"general>father")
            wid.setText(text)
            wid  = self.tabParents.findChild(QLabel,"parents>father")
            wid.setText(text)
    def _onMotherClick1(self, event):
        wid  = self.tabGeneral.findChild(QLabel,"general>mother")
        self._onMotherClick(wid.text())
    def _onMotherClick2(self, event):
        wid  = self.tabParents.findChild(QLabel,"parents>mother")
        self._onMotherClick(wid.text())
    def _onMotherClick(self, widText):
        ret, id, text = self._showSelectPersDlg("m", "Mutter", [self.ID], widText)
        if ret:
            widB  = self.tabGeneral.findChild(QPushButton,"general>motherNav")
            widB.setText(id)
            widB  = self.tabParents.findChild(QPushButton,"parents>motherNav")
            widB.setText(id)
            
            wid  = self.tabGeneral.findChild(QLabel,"general>mother")
            wid.setText(text)
            wid  = self.tabParents.findChild(QLabel,"parents>mother")
            wid.setText(text)
    def _onPartnerClick(self, event):
        pass
    def _onChildClick(self, event):
        pass
    def _onNewRelationshipClick(self, event):
        pass
    def _onNewChild(self):
        pass
    def _onEditingFirstnameFinished(self):
        ret, name = self.data.getName(self.ID)
        if not ret: 
            old = ""     
        else:
            old = name["firstname"]
        
        wid = self.tabGeneral.findChild(QLineEdit,"general>firstname")
        new = wid.text()
        
        if new != old:
            self.data.setFirstname(self.ID, wid.text())
            if self.configData["personListFields"].get("NAME>GIVN","") != "":
                self._updateListLine()
    def _onEditingSurnameFinished(self):
        ret, name = self.data.getName(self.ID)
        if not ret: 
            old = "" 
        else:      
            old = name["surname"]
        
        wid = self.tabGeneral.findChild(QLineEdit,"general>surname")
        new = wid.text()
        
        if new != old:
            self.data.setSurname(self.ID, wid.text())
            if self.configData["personListFields"].get("NAME>SURN","") != "":
                self._updateListLine()
    def _onSexStateClicked(self):
        ret, old = self.data.getSex(self.ID)
        
        widM = self.tabGeneral.findChild(QRadioButton,"general>sexMan")
        widW = self.tabGeneral.findChild(QRadioButton,"general>sexWoman")
        if   widM.isChecked(): new = "m"
        elif widW.isChecked(): new = "w"
        else:                  new = ""
        
        if new != old:
            self.data.setSex(self.ID, new)
            if self.configData["personListFields"].get("SEX","") != "":
                self._updateListLine()
    def _onEditingBirthDateFinished(self):
        ret, birth = self.data.getBirthData(self.ID)
        if not ret: 
            old = ""
        else:
            old = birth["date"]

        wid = self.tabGeneral.findChild(QLineEdit,"general>birthDat")
        new = wid.text()
        
        if new != old:
            self.data.setBirthDate(self.ID, wid.text())
            if self.configData["personListFields"].get("BIRT>DATE","") != "":
                self._updateListLine()
    def _onEditingBirthPlaceFinished(self):
        ret, birth = self.data.getBirthData(self.ID)
        if not ret: 
            old = ""
        else:
            old = birth["place"]
        
        wid = self.tabGeneral.findChild(QLineEdit,"general>birthPlac")
        new = wid.text()
        
        if new != old:
            self.data.setBirthPlace(self.ID, wid.text())
            if self.configData["personListFields"].get("BIRT>PLAC","") != "":
                self._updateListLine()
    def _onEditingDeathDateFinished(self):
        ret, death = self.data.getDeathData(self.ID)
        if not ret: 
            old = ""
        else:
            old = death["date"]
        
        wid = self.tabGeneral.findChild(QLineEdit,"general>deathDat")
        new = wid.text()
        
        if new != old:
            self.data.setDeathDate(self.ID, wid.text())
            if self.configData["personListFields"].get("DEAT>DATE","") != "":
                self._updateListLine()
    def _onEditingDeathPlaceFinished(self):
        ret, death = self.data.getDeathData(self.ID)
        if not ret: 
            old = ""
        else:
            old = death["place"]
        
        wid = self.tabGeneral.findChild(QLineEdit,"general>deathPlac")
        new = wid.text()
        
        if new != old:
            self.data.setDeathPlace(self.ID, wid.text())
            if self.configData["personListFields"].get("DEAT>PLAC","") != "":
                self._updateListLine()
    def _onEditingMarriageDateFinished(self):
        pass
    def _onEditingMarriagePlaceFinished(self):
        pass
    def _onEditingRelationCommentFinished(self):
        pass
    def _onFatherCommentChanged(self, event):
        wid = self.tabGeneral.findChild(QTextEdit,objectName="parents>fatherComment")
        self.data.setCommentMother(self.ID, wid.toPlainText())
    def _onMotherCommentChanged(self, event):
        wid = self.tabGeneral.findChild(QTextEdit,objectName="parents>motherComment")
        self.data.setCommentMother(self.ID, wid.toPlainText())
    def _onPersURLsChanged(self, event): 
        wid = self.tabGeneral.findChild(QTextEdit,"general>urls")
        self.data.setUrl(self.ID, wid.toPlainText())
    def _onPersCommentChanged(self, event):
        wid = self.tabGeneral.findChild(QTextEdit,"general>comment")
        self.data.setComment(self.ID, wid.toPlainText())
    def _onPersMediaChanged(self, event):
        wid = self.tabGeneral.findChild(QTextEdit,"general>media")
        self.data.setMedia(self.ID, wid.toPlainText())
    def _onPersSourceChanged(self, event):
        wid = self.tabGeneral.findChild(QTextEdit,"general>source")
        self.data.setSource(self.ID, wid.toPlainText())

    def _showSelectPersDlg(self, sex, title, exclPersList, oldText):
        # Geht das auch mit einer Combobox statt Inputfeld? => das Widget erlaubt es, aber man kann
        # nichts tippen, d.h. ein "Filter", also eine Werteeinschränkung ist so nicht möglich

        # Get Data #
        completionList = self.data.getCompletionModel(exclPersList,sex)

        # Create modal dialog #
        dlg = QInputDialog(self)
        dlg.setWindowTitle(title)
        dlg.setLabelText('Name, Geburt, Ableben:')
        if oldText == self.clickTxt:
            dlg.setTextValue("")    
        else:
            dlg.setTextValue(oldText)
        dlg.resize(500,100)
        
        # Get child (input line) #
        childDlg = dlg.findChild(QLineEdit)

        # Add Completer with properties to child #
        completer = QCompleter(completionList, childDlg)
        completer.setFilterMode(Qt.MatchContains)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        childDlg.setCompleter(completer)

        # Show Dialog and process return value #
        ret, text = (dlg.exec_() == QDialog.Accepted, dlg.textValue(), )
        if ret:
            if text == "": 
                if sex == "m": # stands for: except man
                    self.data.assignParent(self.ID, "", "WIFE")
                else: # is "w" and stands for: except woman
                    self.data.assignParent(self.ID, "", "HUSB")
                return True, "", self.clickTxt
                
            orig = text
            pos = text.find("@")
            if pos == -1: return False, "", ""
            text = text[pos+1:]
            
            pos = text.find("@")
            if pos == -1: return False, "", ""
            text = "@" + text[:pos+1]
            orig = self.data.getPersStr(text)
            
            if sex == "m": # stands for: except man
                self.data.assignParent(self.ID, text, "WIFE")
            else: # is "w" and stands for: except woman
                self.data.assignParent(self.ID, text, "HUSB")
            
            return True, text, orig.replace(text + " ", "")
        
        return False, "", "" 
    def _updateListLine(self):
        line = self.data.getPersonForTable(self.ID)
        self.main.widget.listFrame.updateTableHighlightedRow(line)        