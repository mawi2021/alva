# Sources:
#   https://www.geeksforgeeks.org/pyqt5-qtabwidget/
#   https://www.tutorialspoint.com/pyqt/pyqt_qlineedit_widget.htm

import sys
from PyQt5.QtWidgets import QTabWidget, QVBoxLayout, QWidget, QLabel, QLineEdit, QFormLayout, \
                            QHBoxLayout, QVBoxLayout, QPushButton, QTextEdit, QRadioButton, \
                            QButtonGroup, QCompleter, QInputDialog, QDialog, QSizePolicy, \
                            QGroupBox, QTextBrowser
from PyQt5.QtCore import *
from functools import partial
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
        self.childWidgetPos     = -1

        self.initUI()
        # TODO: Auslagern in Config.py
        self.bgColorNormal = 'background-color:rgb(255, 254, 235)'
                
    # ----- UI RELATED -------------------------------------------------------------------------- #
    def initUI(self):
        self.qTabWidget = QTabWidget()

        # Initialize tab screen
        self.tabGeneral = QWidget()
        self.eSexGroup = QButtonGroup(objectName="general>sexGroup") # must be globally, otherwise no signal received
        self.qTabWidget.addTab(self.tabGeneral, "Allgemein")
        self._addGeneralFields()
        
        self.tabParents = QWidget()
        self.qTabWidget.addTab(self.tabParents, "Eltern")
        self._addParentsFields()
        
        self.tabFamily  = QWidget()
        self.formFamilyLayout = QFormLayout()
        self.qTabWidget.addTab(self.tabFamily, "Partner und Kinder")
        self.famWidgetList = [] # <============
        self._addFamilyFields()
        
        self.tabRaw     = QWidget()
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

        ownFamily         = QTextBrowser(objectName="general>ownFamily")

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
        eFather.mousePressEvent = partial(self._onFatherClick, eFather)
        fatherNavButton.clicked.connect(lambda xbool="", wid=fatherNavButton: self._navigateToPerson(xbool, wid))
        fatherNavButton.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed))
        fatherNavButton.setMaximumWidth(80)
        hboxV.addWidget(fatherNavButton)
        formParentLayout.addRow("Vater", hboxV)

        # Mother #
        hboxM = QHBoxLayout()
        hboxM.addWidget(eMother)
        eMother.mousePressEvent = partial(self._onMotherClick, eMother)
        motherNavButton.clicked.connect(lambda xbool="", wid=motherNavButton: self._navigateToPerson(xbool, wid))
        motherNavButton.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed))
        motherNavButton.setMaximumWidth(80)
        hboxM.addWidget(motherNavButton)
        formParentLayout.addRow("Mutter", hboxM)
        
        # ----- FAMILY ----- #
        familyGB         = QGroupBox("Partner und Kinder")
        familyGB.setStyleSheet("QGroupBox {font-weight:bold;margin:5px;padding-top:10px; width:100%;}")
        formFamilyLayout = QFormLayout()
        familyGB.setLayout(formFamilyLayout)        
        
        hboxF = QHBoxLayout()
        hboxF.addWidget(ownFamily)
        formFamilyLayout.addRow("", hboxF)
        
        # ----- end ----- #
        globLayout = QVBoxLayout()
        globLayout.addWidget(persGB)
        globLayout.addWidget(parentGB)   
        globLayout.addWidget(familyGB)   
        self.tabGeneral.setLayout(globLayout)
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
        eFather.mousePressEvent = partial(self._onFatherClick, eFather)
        fatherNavButton.clicked.connect(lambda xbool="", wid=fatherNavButton: self._navigateToPerson(xbool, wid))
        fatherNavButton.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed))
        fatherNavButton.setMaximumWidth(80)
        hboxV.addWidget(fatherNavButton)
        formParentLayout.addRow("Vater", hboxV)
        fatherComment.focusOutEvent = self._onFatherCommentChanged
        formParentLayout.addRow("Kommentar", fatherComment)

        # Mother #
        hboxM = QHBoxLayout()
        hboxM.addWidget(eMother)
        eMother.mousePressEvent = partial(self._onMotherClick, eMother)
        motherNavButton.clicked.connect(lambda xbool="", wid=motherNavButton: self._navigateToPerson(xbool, wid))
        motherNavButton.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed))
        motherNavButton.setMaximumWidth(80)
        hboxM.addWidget(motherNavButton)
        formParentLayout.addRow("Mutter", hboxM)
        motherComment.focusOutEvent = self._onMotherCommentChanged
        formParentLayout.addRow("Kommentar", motherComment)

        self.tabParents.setLayout(formParentLayout)
    def _addFamilyFields(self):
        # ----- FAMILY ----- #
        widgets = {}

        widgets["marriageDate"]     = QLineEdit("")
        widgets["marriagePlac"]     = QLineEdit("")
        widgets["partner"]          = QLabel("")
        widgets["partnerNavButton"] = QPushButton("")
        widgets["childRows"]        = []
        # widgets["childRow"][i]["childLbl"]         
        # widgets["childRow"][i]["childNavBtn"]   
        # widgets["childRow"][i]["childDelBtn"]   
        widgets["newChildButton"]   = QPushButton("")
        widgets["relationComment"]  = QTextEdit()
        newRelationship = QPushButton("", self)

        self.famWidgetList.append(widgets)
        
        # Hochzeit #
        widgets["marriageDate"].editingFinished.connect(lambda wid=widgets["marriageDate"]: self._onEditingMarriageDateFinished(wid,0))
        widgets["marriagePlac"].editingFinished.connect(lambda wid=widgets["marriagePlac"]: self._onEditingMarriagePlaceFinished(wid,0))
        hboxMa = QHBoxLayout()
        hboxMa.addWidget(widgets["marriageDate"])
        hboxMa.addWidget(widgets["marriagePlac"])
        self.formFamilyLayout.addRow("Hochzeit: Datum/Ort", hboxMa)
        
        # Partner #
        hboxPar = QHBoxLayout()
        hboxPar.addWidget(widgets["partner"])
        widgets["partner"].mousePressEvent = self._onPartnerClick
        widgets["partnerNavButton"].clicked.connect(lambda xbool="", wid=widgets["partnerNavButton"]: self._navigateToPerson(xbool, wid))
        widgets["partnerNavButton"].setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed))
        widgets["partnerNavButton"].setMaximumWidth(80)
        hboxPar.addWidget(widgets["partnerNavButton"])
        self.formFamilyLayout.addRow("Partner", hboxPar)
        
        # Child #
        self.childWidgetPos = self.formFamilyLayout.rowCount()
        self._addChild(0, self.clickTxt, "")          

        # Additional Child - Button #
        widgets["newChildButton"].setText("Zeile für weiteres Kind erstellen")
        widgets["newChildButton"].clicked.connect(lambda xbool="", wid=widgets["newChildButton"]: self._onNewChild(xbool, wid))
        self.formFamilyLayout.addRow("Weiteres Kind", widgets["newChildButton"])

        # Comment on Family #
        widgets["relationComment"].textChanged.connect(lambda wid=widgets["relationComment"]: self._onEditingRelationCommentFinished(wid,0))
        self.formFamilyLayout.addRow("Kommentar", widgets["relationComment"])

        # Additional Family - Button #
        newRelationship.setText("Block für weitere Familie erstellen")
        newRelationship.clicked.connect(self._onNewRelationshipClick)
        self.formFamilyLayout.addRow("", newRelationship)

        self.tabFamily.setLayout(self.formFamilyLayout)
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
        
        # ----- Details of the Person ----- #
        self._setPersonDetails()
        
        # ----- Parents ----- #
        self._setPersonParents()

        # ----- Partner, Marriage and Children ----- #
        self._setPersonOwnFam()

        # ----- Raw Data ----- #
        self.rawText.clear()
        
        ret1, data = self.data.getPerson(self.ID)
        if ret1:
            self.rawText.insertPlainText(json.dumps(data))
            self.navigationListBack.append(self.ID)
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

    def _addChild(self, famIdx, txtLabel, txtButton):
        if len(self.famWidgetList) <= famIdx: return
                
        lbl = QLabel("")
        lbl.mousePressEvent = partial(self._onChildClick, lbl)
        lbl.setText(txtLabel)
        
        navBtn = QPushButton("")
        navBtn.clicked.connect(lambda xbool="", wid=navBtn: self._navigateToPerson(xbool, wid))
        navBtn.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed))
        navBtn.setMaximumWidth(80)
        navBtn.setText(txtButton)

        delBtn = QPushButton("")
        delBtn.clicked.connect(lambda xbool="", id=txtButton: self._onDeleteChildRow(xbool, id))
        delBtn.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed))
        delBtn.setMaximumWidth(80)
        delBtn.setText("Löschen")

        hboxCh = QHBoxLayout()
        hboxCh.addWidget(lbl)
        hboxCh.addWidget(navBtn)
        hboxCh.addWidget(delBtn)
        
        self.famWidgetList[famIdx]["childRows"].append({"childLbl": lbl,
                                                        "childNavBtn": navBtn,
                                                        "childDelBtn": delBtn})

        self.formFamilyLayout.insertRow(self.childWidgetPos, "Kind", hboxCh)
        self.childWidgetPos += 1
    def _deleteChildRow(self, famIdx, id):
        if len(self.famWidgetList) <= famIdx: return
        
        widgets = self.famWidgetList[famIdx]
        
        # Delete entry for child with ID = id #
        for i in range(len(widgets["childRows"])):
            if widgets["childRows"][i]["childNavBtn"].text() == id:
                self.formFamilyLayout.removeRow(i + 2)
                widgets["childRows"].pop(i)
                self.childWidgetPos -= 1                               
                break
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
    def _navigateToPerson(self, xbool, wid):
        # xbool is a dummy value, probably a button number #
        id = wid.text()
        self.main.widget.setPerson(id)
        self.ID = id
    def _onAddPerson(self):
        self.main.widget.addPerson()
    def _onChildClick(self, wid, event):
        oldText = wid.text()
        for row in self.famWidgetList[0]["childRows"]:
            if row["childLbl"] == wid:
                widBtn = row["childNavBtn"]  
                break      
        who = "HUSB" if self.data.getSex(self.ID) == "m" else "WIFE"
                
        # Get Data for auto #
        completionList = self.data.getCompletionModel(self.ID,"")
        
        dlg = QInputDialog(self)
        dlg.setWindowTitle("Kind")
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
                if oldText != "":
                    self.data.unassignParent(oldText, who)
                    widBtn.setText("")
                    wid.setText(self.clickTxt)
            else:
                # Get ID of child #
                orig = text
                pos = text.find("@")
                if pos == -1: return False, "", ""
                text = text[pos+1:]
                
                pos = text.find("@")
                if pos == -1: return False, "", ""
                text = "@" + text[:pos+1]
                orig = self.data.getPersStr(text)
                
                self.data.assignParent(text, self.ID, who)
                widBtn.setText(text)
                wid.setText(orig.replace(text + " ", ""))        
    def _onDeleteChildRow(self, xbool, id):
        self._deleteChildRow(0, id)
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
    def _onEditingMarriageDateFinished(self, wid, idx):
        old = self.data.getMarriageDate(self.ID, idx)
        new = wid.text()
        
        if old != new:
            self.data.setMarriageDate(self.ID, idx, wid.text())
    def _onEditingMarriagePlaceFinished(self, wid, idx):
        old = self.data.getMarriagePlace(self.ID, idx)
        new = wid.text()
        
        if old != new:
            self.data.setMarriagePlace(self.ID, idx, wid.text())
    def _onEditingRelationCommentFinished(self, wid, idx):
        old = self.data.getRelationComment(self.ID, idx)
        new = wid.toPlainText()
        
        if old != new:
            self.data.setRelationComment(self.ID, idx, wid.toPlainText())
    def _onFatherClick(self, wid, event):
        widText = wid.text()
        
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
    def _onFatherCommentChanged(self, dummy, event):
        wid = self.tabParents.findChild(QTextEdit,"parents>fatherComment")
        self.data.setCommentFather(self.ID, wid.toPlainText())
    def _onMotherClick(self, wid, event):
        widText = wid.text()
        
        # Show dialog and save data #
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
    def _onMotherCommentChanged(self, event):
        wid = self.tabParents.findChild(QTextEdit,"parents>motherComment")
        self.data.setCommentMother(self.ID, wid.toPlainText())
    def _onNewChild(self, xbool, wid):
        self._addChild(0, self.clickTxt, "") # 0 stands for null-th partner box
    def _onNewRelationshipClick(self, event):
        pass
    def _onOpenGraph(self):
        self.main.graphList.addGraph(self.ID)
    def _onPartnerClick(self, event):
        pass
    def _onPersCommentChanged(self, event):
        wid = self.tabGeneral.findChild(QTextEdit,"general>comment")
        self.data.setComment(self.ID, wid.toPlainText())
    def _onPersMediaChanged(self, event):
        wid = self.tabGeneral.findChild(QTextEdit,"general>media")
        self.data.setMedia(self.ID, wid.toPlainText())
    def _onPersSourceChanged(self, event):
        wid = self.tabGeneral.findChild(QTextEdit,"general>source")
        self.data.setSource(self.ID, wid.toPlainText())
    def _onPersURLsChanged(self, event): 
        wid = self.tabGeneral.findChild(QTextEdit,"general>urls")
        self.data.setUrl(self.ID, wid.toPlainText())
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
    def _setPersonDetails(self):
        wid = self.tabGeneral.findChild(QLabel,"general>id")
        wid.setText(self.ID)
        
        # Name #
        ret, name = self.data.getName(self.ID)
        widF = self.tabGeneral.findChild(QLineEdit,"general>firstname")
        widS = self.tabGeneral.findChild(QLineEdit,"general>surname")
        if ret:
            widF.setText(name["firstname"])
            widS.setText(name["surname"])
        else:
            widF.setText("")
            widS.setText("")
            
        # Sex #
        ret, sex = self.data.getSex(self.ID)
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
        ret, birth = self.data.getBirthData(self.ID)
        wid1 = self.tabGeneral.findChild(QLineEdit,"general>birthDat")
        wid2 = self.tabGeneral.findChild(QLineEdit,"general>birthPlac")
        if ret:    
            wid1.setText(birth.get("date",""))
            wid2.setText(birth.get("place",""))
        else:
            wid1.setText("")
            wid2.setText("")
            
        # Death #
        ret, death = self.data.getDeathData(self.ID)
        wid1 = self.tabGeneral.findChild(QLineEdit,"general>deathDat")
        wid2 = self.tabGeneral.findChild(QLineEdit,"general>deathPlac")
        if ret:
            wid1.setText(death.get("date",""))
            wid2.setText(death.get("place",""))
        else:
            wid1.setText("")
            wid2.setText("")
            
        # URLs #
        ret, value = self.data.getUrl(self.ID)
        wid = self.tabGeneral.findChild(QTextEdit,"general>urls")
        wid.setText(value)
        
        # Comment #
        ret, value = self.data.getComment(self.ID)
        wid = self.tabGeneral.findChild(QTextEdit,"general>comment")
        wid.setText(value)
        
        # Media #
        ret, value = self.data.getMedia(self.ID)
        wid = self.tabGeneral.findChild(QTextEdit,"general>media")
        wid.setText(value)
        
        # Source #
        ret, value = self.data.getSource(self.ID)
        wid = self.tabGeneral.findChild(QTextEdit,"general>source")
        wid.setText(value)        
    def _setPersonOwnFam(self):
        famList = self.data.getOwnFamily(self.ID)

        if len(famList) > 0:
            for i in range(1): #len(famList)):
                famDetails = famList[i]
                wids = self.famWidgetList[i]
                
                # Marriage #
                wids["marriageDate"].setText(famDetails.get("date",""))
                wids["marriagePlac"].setText(famDetails.get("place",""))
                
                # Partner #
                pid = famDetails.get("partnerID","")
                if pid != "":
                    wids["partner"].setText(self.data.getPersStr(pid))
                    wids["partnerNavButton"].setText(pid)
                else:
                    wids["partner"].setText(self.clickTxt)
                    wids["partnerNavButton"].setText("")
                
                # Children #
                childrenID = famDetails.get("childrenID",[])
                cntChildren = len(childrenID)
                numChildRows = len(wids["childRows"])
                
                for j in reversed(range(max(cntChildren, numChildRows))):
                    if j < cntChildren:
                        childID = childrenID[j]
                        
                        if j >= numChildRows: # not enough lines => create new row
                            self._addChild(i, self.data.getPersStr(childID), childID)
                        else: # set texts in existing row
                            wids["childRows"][j]["childLbl"].setText(self.data.getPersStr(childID))
                            wids["childRows"][j]["childNavBtn"].setText(childID)
                            wids["childRows"][j]["childDelBtn"].setText("Löschen")
                    else:
                        if j == 0: # keep first line and remove content
                            wids["childRows"][j]["childLbl"].setText(self.clickTxt)
                            wids["childRows"][j]["childNavBtn"].setText("")
                            wids["childRows"][j]["childDelBtn"].setText("")
                        else: # delete all except for the first line
                            self._deleteChildRow(i, wids["childRows"][j]["childNavBtn"].text())                 
                
                # Comment #
                wids["relationComment"].setText(famDetails.get("comment",""))
            
        else:
            # all fields empty #
            wids = self.famWidgetList[0]
            numChildren = len(wids["childRows"])
                        
            for j in reversed(range(numChildren)):
                if j == 0:
                    wids["marriageDate"].setText("")
                    wids["marriagePlac"].setText("")
                    wids["partner"].setText(self.clickTxt)
                    wids["partnerNavButton"].setText("")     
                    wids["childRows"][0]["childLbl"].setText(self.clickTxt)
                    wids["childRows"][0]["childNavBtn"].setText("")    
                    wids["childRows"][0]["childDelBtn"].setText("")    
                    wids["relationComment"].setText("")
                else:
                    self._deleteChildRow(0, wids["childRows"][j]["childNavBtn"].text())
    def _setPersonParents(self):
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
        wid = self.tabParents.findChild(QTextEdit,"parents>fatherComment")
        ret, comm = self.data.getCommentFather(self.ID)
        wid.setText(comm)
            
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
        wid = self.tabParents.findChild(QTextEdit,"parents>motherComment")
        ret, comm = self.data.getCommentMother(self.ID)
        wid.setText(comm)        
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