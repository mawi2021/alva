# Sources:
#   https://www.geeksforgeeks.org/pyqt5-qtabwidget/
#   https://www.tutorialspoint.com/pyqt/pyqt_qlineedit_widget.htm

from PyQt5.QtWidgets import QTabWidget, QVBoxLayout, QWidget, QLabel, QLineEdit, QFormLayout, \
                            QHBoxLayout, QVBoxLayout, QPushButton, QTextEdit, QRadioButton, \
                            QButtonGroup, QCompleter, QInputDialog, QDialog, QSizePolicy, \
                            QGroupBox, QCheckBox, QScrollArea
from PyQt5.QtCore    import *
from functools       import partial

class PersonWidget(QScrollArea):

    def __init__(self, main):
        super().__init__()
        self.main          = main
        self.famWidgetList = [] 
        # self.famWidgetList[i]["childRows"][j]["childLbl"].text() is the text of j-th child in i-th family
        # self.famWidgetList[i]["childRows"][j]["childNavBtn"].text() is the ID of j-th child in i-th family

        self.navigationListBack = []
        self.ID                 = -1
        self.persLbl            = QLabel("")
        self.clickTxt           = "<klick hier>"
        self.childWidgetPos     = -1

        self.initUI()
        self.bgColorNormal = 'background-color:rgb(252, 252, 242)'
                
    def get_ID(self):
        return self.ID
    def initUI(self):
        content_widget = QWidget()   
        layout         = QVBoxLayout(content_widget)
        self.setWidget(content_widget)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded) 
        self.setWidgetResizable(True)

        # Initialize tab screen
        qTabWidget = QTabWidget()

        self.tabGeneral = QWidget()
        self.eSexGroup = QButtonGroup(objectName="general>sexGroup") # must be globally, otherwise no signal received
        qTabWidget.addTab(self.tabGeneral, "Allgemein")
        self.initUI_add_general_fields()
        
        self.tabParents = QWidget()
        qTabWidget.addTab(self.tabParents, "Eltern")
        self.initUI_add_parents_fields()
        
        self.tabFamily  = QWidget()
        self.formFamilyLayout = QFormLayout()
        qTabWidget.addTab(self.tabFamily, "Partner und Kinder")
        self.initUI_add_family_fields()

        # Central Person #        
        layout.addWidget(self.persLbl)
        self.persLbl.setStyleSheet("background-color:rgb(128,255,255);padding:10px;font-weight:bold;font-size:12px;border:1px solid gray;")

        # Button Line above Tab Widget
        hboxB = QHBoxLayout()
        layout.addLayout(hboxB)

        self.backButton = QPushButton("🡸", self)
        self.backButton.clicked.connect(self._navigateBack)
        hboxB.addWidget(self.backButton)

        self.addButton = QPushButton("Neue Person", self)
        self.addButton.clicked.connect(self.main.create_person)
        hboxB.addWidget(self.addButton)

        self.copyButton = QPushButton("Person kopieren", self)
        self.copyButton.clicked.connect(self.main.copy_person)
        hboxB.addWidget(self.copyButton)

        self.ancButton = QPushButton("Vorfahren", self)
        self.ancButton.clicked.connect(self.main.open_graph_ancestors)
        hboxB.addWidget(self.ancButton)

        self.descButton = QPushButton("Nachfahren", self)
        self.descButton.clicked.connect(self.main.open_graph_descendants)
        hboxB.addWidget(self.descButton)

        # Add box layout, add table to box layout and add box layout to widget
        layout.addWidget(qTabWidget) 
        self.setLayout(layout) 
    def initUI_add_general_fields(self):
        # for new fields also check method set_person_details()
        # ----- PERSON ----- #
        persGB         = QGroupBox("Person")
        persGB.setStyleSheet("QGroupBox {font-weight:bold;padding-top:10px;margin:5px;}")
        persGB.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        formPersLayout = QFormLayout()
        persGB.setLayout(formPersLayout)
                
        # ID
        eId = QLabel("", objectName="general>id")
        formPersLayout.addRow("ID", eId)

        # Finished
        eFinished = QCheckBox("", objectName="finished")
        eFinished.stateChanged.connect(partial(self.on_editing_finished, "finished"))
        formPersLayout.addRow("Fertig", eFinished)

        # Firstname
        eFirstname = QLineEdit("", objectName="GIVN")
        eFirstname.editingFinished.connect(partial(self.on_editing_finished, "GIVN"))
        formPersLayout.addRow("Vorname", eFirstname)

        # Surname and Birthname
        eSurname = QLineEdit("", objectName="SURN")
        eSurname.editingFinished.connect(partial(self.on_editing_finished, "SURN"))
        lBSurname = QLabel("geb.")
        eBSurname = QLineEdit("", objectName="birthname")
        eBSurname.editingFinished.connect(partial(self.on_editing_finished, "birthname"))
        hboxN = QHBoxLayout()
        hboxN.addWidget(eSurname)
        hboxN.addWidget(lBSurname)
        hboxN.addWidget(eBSurname)
        formPersLayout.addRow("Nachname", hboxN)

        # Sex #
        self.eSexGroup.buttonClicked.connect(self._onSexStateClicked)
        eSexMan = QRadioButton("männlich", objectName="general>sexMan")
        self.eSexGroup.addButton(eSexMan)
        eSexWoman = QRadioButton("weiblich", objectName="general>sexWoman")
        self.eSexGroup.addButton(eSexWoman)
        eSexOhne = QRadioButton("k.A.", objectName="general>sexOhne")
        self.eSexGroup.addButton(eSexOhne)
        hboxS = QHBoxLayout()
        hboxS.addWidget(eSexMan)
        hboxS.addWidget(eSexWoman)
        hboxS.addWidget(eSexOhne)
        formPersLayout.addRow("Geschlecht", hboxS)

        # Birth #
        hboxB = QHBoxLayout()
        lBDat = QLabel("Datum (Tag.Monat.Jahr)")
        hboxB.addWidget(lBDat)
        eBirthDat = QLineEdit("", objectName="BIRT_DATE")
        # eBirthDat.setInputMask("00.00.0000; ")  # 0 = Pflicht-Ziffer, _ = Placeholder
        # eBirthDat.setPlaceholderText("TT.MM.JJJJ")
        eBirthDat.setFixedWidth(70)
        eBirthDat.editingFinished.connect(partial(self.on_editing_finished, "BIRT_DATE"))
        hboxB.addWidget(eBirthDat)
        lBirthDatEstim = QLabel("     Datum geschätzt")
        eBirthDatEstim = QCheckBox("", objectName="guess_birth")
        eBirthDatEstim.stateChanged.connect(partial(self.on_editing_finished, "guess_birth"))
        lBPlac = QLabel("     Ort")
        eBirthPlac = QLineEdit("", objectName="BIRT_PLAC")
        eBirthPlac.editingFinished.connect(partial(self.on_editing_finished, "BIRT_PLAC"))
        hboxB.addWidget(lBirthDatEstim)
        hboxB.addWidget(eBirthDatEstim)
        hboxB.addWidget(lBPlac)
        hboxB.addWidget(eBirthPlac)
        formPersLayout.addRow("Geburt:", hboxB)

        # Death #
        hboxD = QHBoxLayout()
        lDDat = QLabel("Datum (Tag.Monat.Jahr)")
        hboxD.addWidget(lDDat)
        eDeathDat = QLineEdit("", objectName="DEAT_DATE")
        # eDeathDat.setInputMask("00.00.0000; ")  # 0 = Pflicht-Ziffer, _ = Placeholder
        # eDeathDat.setPlaceholderText("TT.MM.JJJJ")
        eDeathDat.setFixedWidth(70)
        eDeathDat.editingFinished.connect(partial(self.on_editing_finished, "DEAT_DATE"))
        lDeathDatEstim = QLabel("     Datum geschätzt")
        eDeathDatEstim = QCheckBox("", objectName="guess_death")
        eDeathDatEstim.stateChanged.connect(partial(self.on_editing_finished, "guess_death"))
        lDPlac = QLabel("     Ort")
        eDeathPlac = QLineEdit("", objectName="DEAT_PLAC")
        eDeathPlac.editingFinished.connect(partial(self.on_editing_finished, "DEAT_PLAC"))
        hboxD.addWidget(eDeathDat)
        hboxD.addWidget(lDeathDatEstim)
        hboxD.addWidget(eDeathDatEstim)
        hboxD.addWidget(lDPlac)
        hboxD.addWidget(eDeathPlac)
        formPersLayout.addRow("Ableben:", hboxD)

        # Comment-Types: url, comment, media, sources #
        persURLs = QTextEdit(objectName="url")
        persURLs.setAcceptRichText(False)  # => Plain-Text only
        persURLs.focusOutEvent = self.on_person_url_changed
        persURLs.setFixedHeight(200)
        persURLs.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        formPersLayout.addRow("URLs", persURLs)

        persComment = QTextEdit(objectName="comment")
        persComment.setAcceptRichText(False)  # => Plain-Text only
        persComment.focusOutEvent = self.on_person_comment_changed
        formPersLayout.addRow("Kommentar", persComment)

        persMedia = QTextEdit(objectName="media")
        persMedia.setAcceptRichText(False)  # => Plain-Text only
        persMedia.focusOutEvent = self.on_person_media_changed
        formPersLayout.addRow("Medien", persMedia)    

        persSource = QTextEdit(objectName="source")
        persSource.setAcceptRichText(False)  # => Plain-Text only
        persSource.focusOutEvent = self.on_person_source_changed
        formPersLayout.addRow("Quellen", persSource)    

        # ----- PARENTS ----- #        
        parentGB         = QGroupBox("Eltern")
        parentGB.setStyleSheet("QGroupBox {font-weight:bold;padding-top:10px;margin:5px;}")
        formParentLayout = QFormLayout()
        parentGB.setLayout(formParentLayout)

        # Father #
        eFather           = QLabel(objectName="general>father")
        fatherNavButton   = QPushButton("", self, objectName="general>fatherNav")
        hboxV = QHBoxLayout()
        hboxV.addWidget(eFather)
        eFather.mousePressEvent = partial(self._onFatherClick, eFather)
        fatherNavButton.clicked.connect(lambda xbool="", wid=fatherNavButton: self._navigateToPerson(xbool, wid))
        fatherNavButton.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed))
        fatherNavButton.setMaximumWidth(80)
        hboxV.addWidget(fatherNavButton)
        formParentLayout.addRow("Vater", hboxV)

        # Mother #
        eMother           = QLabel(objectName="general>mother")
        motherNavButton   = QPushButton("", self, objectName="general>motherNav")
        hboxM = QHBoxLayout()
        hboxM.addWidget(eMother)
        eMother.mousePressEvent = partial(self._onMotherClick, eMother)
        motherNavButton.clicked.connect(lambda xbool="", wid=motherNavButton: self._navigateToPerson(xbool, wid))
        motherNavButton.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed))
        motherNavButton.setMaximumWidth(80)
        hboxM.addWidget(motherNavButton)
        formParentLayout.addRow("Mutter", hboxM)
        
        # ----- FAMILY ----- #
        familyGB         = QLabel("Partner und Kinder")
        familyGB.setStyleSheet("QLabel {font-weight:bold;padding-top:10px; width:100%;}")
        ownFamily = QTextEdit(objectName="general>ownFamily")
        ownFamily.setStyleSheet("QTextEdit {margin:5px;padding-left:5px;}")
        ownFamily.setReadOnly(True)
        
        # ----- end ----- #
        globLayout = QVBoxLayout()
        globLayout.addWidget(persGB)
        globLayout.addWidget(parentGB)   
        globLayout.addWidget(familyGB)   
        globLayout.addWidget(ownFamily)
        self.tabGeneral.setLayout(globLayout)
    def initUI_add_parents_fields(self):
    
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
    def initUI_add_family_fields(self):
        # ----- FAMILY ----- #
        widgets = {}

        widgets["marriageDate"]     = QLineEdit("")
        widgets["marriagePlac"]     = QLineEdit("")
        widgets["partner"]          = QLabel(objectName="family>partner0")
        widgets["partnerNavButton"] = QPushButton("", self, objectName="family>partnerNav0")
        widgets["childRows"]        = []
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
        widgets["partner"].mousePressEvent = partial(self._onPartnerClick, widgets["partner"])
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
    def on_editing_finished(self, field, state=None):
        if field in ("finished", "guess_birth", "guess_death"):  # QCheckBox
            new = state == Qt.Checked
            old = not(new)
        elif field in ("comment", "media", "source", "url"):     # QTextEdit
            wid = self.tabGeneral.findChild(QTextEdit, field)
            old = self.main.get_person_attribute(self.ID, field)
            new = wid.toPlainText()
        else:                                                    # QLineEdit
            wid = self.tabGeneral.findChild(QLineEdit, field)
            old = self.main.get_person_attribute(self.ID, field)
            new = wid.text()

        if new != old:
            self.main.set_person_attribute(self.ID, field, new)
            if self.main.is_field_in_table(field):
                self.main.update_table_row(self.ID)
    def on_person_comment_changed(self, event):
        self.on_editing_finished("comment")
    def on_person_media_changed(self, event):
        self.on_editing_finished("media")
    def on_person_source_changed(self, event):
        self.on_editing_finished("source")
    def on_person_url_changed(self, event): 
        self.on_editing_finished("url")
    def refreshBackground(self):
        self.setStyleSheet(self.bgColorNormal)
    def set_checkbox(self, fieldname):
        value = self.main.get_person_attribute(self.ID, fieldname)
        wid = self.tabGeneral.findChild(QCheckBox, fieldname)
        wid.setChecked(True if value == 'X' else False)        
    def set_person(self, id):
        self.ID = id
        self.persLbl.setText(self.main.get_person_string(id))

        self.set_person_details()  # Details of the Person
        self.set_person_parents()  # Parents
        self.set_person_own_fam()  # Partner, Marriage and Children

        # Person Navigation Stack
        if self.ID >= 0:
            self.navigationListBack.append(self.ID)
        else:
            self.navigationListBack = []
    def set_person_details(self):
        wid = self.tabGeneral.findChild(QLabel,"general>id")
        if self.ID >= 0:
            wid.setText(str(self.ID))
        else:
            wid.setText("")
        
        finished = self.main.get_person_attribute(self.ID, "finished")
        widFini  = self.tabGeneral.findChild(QCheckBox,"finished")
        widFini.setChecked(finished)

        # Name #
        self.set_text_field("GIVN")           # Firstname
        self.set_text_field("SURN")           # Surname
        self.set_text_field("birthname")      # Maiden name
            
        # Sex #
        sex = self.main.get_person_attribute(self.ID, "SEX")
        widM = self.tabGeneral.findChild(QRadioButton,"general>sexMan")
        widW = self.tabGeneral.findChild(QRadioButton,"general>sexWoman")
        widO = self.tabGeneral.findChild(QRadioButton,"general>sexOhne")
        if sex == "m":           
            widM.setChecked(True)
        elif sex == "w" or sex == "f":
            widW.setChecked(True)
        elif sex == "":
            widO.setChecked(True)

        self.set_text_field("BIRT_DATE")      # Birth Date
        self.set_checkbox("guess_birth")      # Birth Year Guess
        self.set_text_field("BIRT_PLAC")      # Birth Place 
        self.set_text_field("DEAT_DATE")      # Death Date            
        self.set_checkbox("guess_death")      # Death Year Guess
        self.set_text_field("DEAT_PLAC")      # Death Place 
        self.set_textarea_field("url")        # URL 
        self.set_textarea_field("comment")    # Comment 
        self.set_textarea_field("media")      # Media 
        self.set_textarea_field("source")     # Source 
    def set_person_own_fam(self):
        famList = self.main.get_family_as_adult(self.ID)

        if len(famList) > 0:
            for famDetails in famList: #len(famList)):
                wids = self.famWidgetList[0]
                
                # Marriage #
                wids["marriageDate"].setText(famDetails.get("date",""))
                wids["marriagePlac"].setText(famDetails.get("place",""))
                
                # Partner #
                pid = famDetails.get("partnerID","")
                if pid and pid != -5:
                    wids["partner"].setText(self.main.get_person_string(pid))
                    wids["partnerNavButton"].setText(str(pid))
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
                            self._addChild(0, self.main.get_person_string(childID), str(childID))
                        else: # set texts in existing row
                            wids["childRows"][j]["childLbl"].setText(self.main.get_person_string(childID))
                            wids["childRows"][j]["childNavBtn"].setText(str(childID))
                            wids["childRows"][j]["childDelBtn"].setText("Löschen")
                    else:
                        if j == 0: # keep first line and remove content
                            wids["childRows"][j]["childLbl"].setText(self.clickTxt)
                            wids["childRows"][j]["childNavBtn"].setText("")
                            wids["childRows"][j]["childDelBtn"].setText("")
                        else: # delete all except for the first line
                            self._deleteChildRow(0, wids["childRows"][j]["childNavBtn"].text())                 
                
                # Comment #
                wids["relationComment"].setText(famDetails.get("comment",""))
                break   # only first family taken into consideration
            
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

        self.update_own_family_in_general_tab()
    def set_person_parents(self):
        widF   = self.tabGeneral.findChild(QLabel,"general>father")
        widFB  = self.tabGeneral.findChild(QPushButton,"general>fatherNav")      
        widF2  = self.tabParents.findChild(QLabel,"parents>father")
        widFB2 = self.tabParents.findChild(QPushButton,"parents>fatherNav")
        idF = self.main.get_person_attribute(self.ID, "father")
        txt = self.main.get_person_string(idF)
        if txt != "":
            widF.setText(txt)
            widFB.setText(str(idF))
            widF2.setText(txt)
            widFB2.setText(str(idF))
        else:
            widF.setText(self.clickTxt)
            widFB.setText("")
            widF2.setText(self.clickTxt)
            widFB2.setText("")
        wid = self.tabParents.findChild(QTextEdit,"parents>fatherComment")
        comm = self.main.get_person_attribute(idF, "comment")
        wid.setText(comm)
            
        widM  = self.tabGeneral.findChild(QLabel,"general>mother")
        widMB = self.tabGeneral.findChild(QPushButton,"general>motherNav")
        widM2  = self.tabParents.findChild(QLabel,"parents>mother")
        widMB2 = self.tabParents.findChild(QPushButton,"parents>motherNav")
        idM = self.main.get_person_attribute(self.ID, "mother")
        txt = self.main.get_person_string(idM)
        if txt != "":
            widM.setText(txt)
            widMB.setText(str(idM))
            widM2.setText(txt)
            widMB2.setText(str(idM))
        else:
            widM.setText(self.clickTxt)
            widMB.setText("")
            widM2.setText(self.clickTxt)
            widMB2.setText("")
        wid = self.tabParents.findChild(QTextEdit,"parents>motherComment")
        comm = self.main.get_person_attribute(idM, "comment")
        wid.setText(comm)        
    def set_text_field(self, fieldname):
        value = self.main.get_person_attribute(self.ID, fieldname)
        if fieldname in ("BIRT_DATE", "DEAT_DATE"):
            if value != "":
                value = self.main.convert_date_to_hr(value)
        wid = self.tabGeneral.findChild(QLineEdit, fieldname)
        wid.setText(value)
    def set_textarea_field(self, fieldname):
        value = self.main.get_person_attribute(self.ID, fieldname)
        wid = self.tabGeneral.findChild(QTextEdit, fieldname)
        wid.setText(value)
    def showSelectPersDlg(self, sex, title, exclPers, oldText, caller):

        # Get person string #
        completionList = self.main.get_person_strings_for_value_help(exclPers,sex)

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
            if text == "": # Delete the former assignment, if available
                if caller == 'child':
                    if sex == "m": # stands for: except man
                        self.main.delete_father(self.ID)
                    else: # is "w" and stands for: except woman
                        self.main.delete_father(self.ID)
                elif caller == "partner":
                    pass
                return True, "", self.clickTxt
                
            pos    = text.find(":")
            persID = int(text[3:pos])
            text   = text[pos+2:]
            
            if caller == 'child':
                if sex == "m": # stands for: except man
                    self.main.set_person_attribute(self.ID, "mother", persID)
                else: # is "w" and stands for: except woman
                    self.main.set_person_attribute(self.ID, "father", persID)
            elif caller == "partner":
                pass
            return True, persID, text
        
        return False, "", "" 
    def update_own_family_in_general_tab(self):  # updates General tab field "Partner und Kinder"
        wid = self.tabGeneral.findChild(QTextEdit,"general>ownFamily")  #Read Only Widget
        famList = self.main.get_family_as_adult(self.ID)
        txt = ""
        first = True

        for famObj in famList:
            if not first:
                txt = txt + "<hr>"
            else:
                first = False

            txt = txt + "Famile: " + str(famObj["id"])
            partnerID = famObj.get("partnerID","")
            if partnerID != "":
                txt = txt + "<br>Partner: " + self.main.get_person_string(partnerID)
            childrenID = famObj.get("childrenID","")
            for childID in childrenID:
                txt = txt + "<br>Kind: " + self.main.get_person_string(childID)

        wid.setText(txt)

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
            self.main.set_person(id)
            self.navigationListBack.pop(idx) # remove element from back-array
            self.ID = id
    def _navigateToPerson(self, xbool, wid):
        # xbool is a dummy value, probably a button number #
        id = int(wid.text())
        self.main.set_person(id)
        self.ID = id
    def _onChildClick(self, wid, event):
        old_text = wid.text()  # is the current person describing text

        for row in self.famWidgetList[0]["childRows"]:
            if row["childLbl"] == wid:
                widBtn = row["childNavBtn"] 
                try:
                    old_persID = int(widBtn.text())
                except:
                    old_persID = -1
                break      
                
        # Person picker dialog and completer #
        dlg = QInputDialog(self)
        dlg.setWindowTitle("Kind")
        dlg.setLabelText('Name, Geburt, Ableben:')
        if old_text == self.clickTxt:
            dlg.setTextValue("")    
        else:
            dlg.setTextValue(old_text)
        dlg.resize(500,100)
        childDlg = dlg.findChild(QLineEdit)       
        completionList = self.main.get_person_strings_for_value_help(self.ID,"")
        completer = QCompleter(completionList, childDlg)
        completer.setFilterMode(Qt.MatchContains)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        childDlg.setCompleter(completer)
        
        # Show Dialog and process return value #
        ret, new_text = (dlg.exec_() == QDialog.Accepted, dlg.textValue(), )
        if ret:
            if new_text != old_text:
                if old_persID != -1: # delete old parent-child assignment
                    self.main.delete_father(old_persID)
                    self.main.delete_mother(old_persID)
                
                if  new_text == "":
                    wid.setText(self.clickTxt)
                    widBtn.setText("")
                else:
                    wid.setText(new_text)  # label for person string
                    new_persID = int(new_text[3:].split(":",2)[0])  # ID of new child 
                    partnerID = int(self.famWidgetList[0]["partnerNavButton"].text())  # partnerID and self.ID are parent IDs
                    sex = self.main.get_sex(self.ID)
                    if sex == "m":
                        self.main.set_father(new_persID, self.ID)
                        self.main.set_mother(new_persID, partnerID)
                    else:
                        self.main.set_mother(new_persID, self.ID)
                        self.main.set_father(new_persID, partnerID)
                    widBtn.setText(str(new_persID))

        self.update_own_family_in_general_tab()
    def _onDeleteChildRow(self, xbool, childID):
        self.main.delete_father(childID)        
        self.main.delete_mother(childID)        
        self._deleteChildRow(0, childID)
    def _onEditingMarriageDateFinished(self, wid, idx):
        old = self.main.get_marriage_date(self.ID, idx)
        new = wid.text()
        if old != new:
            self.main.set_marriage_date(self.ID, idx, wid.text())
            self.update_own_family_in_general_tab()
    def _onEditingMarriagePlaceFinished(self, wid, idx):
        old = self.main.get_marriage_place(self.ID, idx)
        new = wid.text()
        if old != new:
            self.main.set_marriage_place(self.ID, idx, wid.text())
            self.update_own_family_in_general_tab()
    def _onEditingRelationCommentFinished(self, wid, idx):
        famIDs = self.main.get_family_ids_as_adult(self.ID)
        if len(famIDs) > idx:
            famID = famIDs[idx]
            old = self.main.get_family_attribute(famID, "comment")
            new = wid.toPlainText()
            if old != new:
                self.main.set_family_attribute(famID, "comment", wid.toPlainText())
    def _onFatherClick(self, wid, event):
        widText = wid.text()
        
        # Show dialog #
        ret, id, text = self.showSelectPersDlg("w", "Vater", self.ID, widText, "child")
        
        if ret:
            widB  = self.tabGeneral.findChild(QPushButton,"general>fatherNav")
            widB.setText(str(id))
            widB  = self.tabParents.findChild(QPushButton,"parents>fatherNav")
            widB.setText(str(id))
            
            wid  = self.tabGeneral.findChild(QLabel,"general>father")
            wid.setText(text)
            wid  = self.tabParents.findChild(QLabel,"parents>father")
            wid.setText(text)
    def _onFatherCommentChanged(self, event):
        wid = self.tabParents.findChild(QTextEdit,"parents>fatherComment")
        father = self.main.get_father(self.ID)
        self.main.set_comment(father, wid.toPlainText())
    def _onMotherClick(self, wid, event):
        widText = wid.text()
        
        # Show dialog #
        ret, id, text = self.showSelectPersDlg("m", "Mutter", self.ID, widText, "child")
        if ret:
            widB  = self.tabGeneral.findChild(QPushButton,"general>motherNav")
            widB.setText(str(id))
            widB  = self.tabParents.findChild(QPushButton,"parents>motherNav")
            widB.setText(str(id))
            
            wid  = self.tabGeneral.findChild(QLabel,"general>mother")
            wid.setText(text)
            wid  = self.tabParents.findChild(QLabel,"parents>mother")
            wid.setText(text)
    def _onMotherCommentChanged(self, event):
        wid = self.tabParents.findChild(QTextEdit,"parents>motherComment")
        mother = self.main.get_mother(self.ID)
        self.main.set_comment(mother, wid.toPlainText())
    def _onNewChild(self, xbool, wid):
        self._addChild(0, self.clickTxt, "") # 0 stands for null-th partner box
    def _onNewRelationshipClick(self, event):
        pass
    def _onPartnerClick(self, wid, event):
        widText = wid.text()

        sex = self.main.get_sex(self.ID)
        if sex == None:
            sex = ''
            
        # Show dialog #
        ret, id, text = self.showSelectPersDlg(sex, "Partner", self.ID, widText, "partner")

        if ret:
            widB = self.tabFamily.findChild(QPushButton,"family>partnerNav0")
            widB.setText(id)
            
            widL = self.tabFamily.findChild(QLabel,"family>partner0")
            widL.setText(text)

            # Get Families. If none exists, create it
            fid_arr = self.main.get_family_ids_as_adult(self.ID)

            # Handle with changes
            if id != "":
                if len(fid_arr) == 0:
                    fid = self.main.create_family()
                else:
                    fid = fid_arr[0]  # TODO: Welche Familie ist richtig? Bei mehreren Ehen ist das nicht klar

                ret, sex_partner = self.main.get_sex(id)
                if ( sex == '' or sex == 'm' or sex_partner == 'w' ) and sex_partner != 'm':
                    self.main.set_wife(fid, id)
                    self.main.set_husband(fid,self.ID)
                else:
                    self.main.set_husband(fid,id)
                    self.main.set_wife(fid,self.ID)

            else:   # Assignment deleted
                if len(fid_arr) > 0:
                    fid = fid_arr[0]  # TODO: Welche Familie ist richtig? Bei mehreren Ehen ist das nicht klar
                    if sex == "m":
                        self.main.delete_wife(fid)
                    else:
                        self.main.delete_husband(fid)

            self.update_own_family_in_general_tab()
    def _onSexStateClicked(self):
        old = self.main.get_sex(self.ID)        
        widM = self.tabGeneral.findChild(QRadioButton,"general>sexMan")
        widW = self.tabGeneral.findChild(QRadioButton,"general>sexWoman")
        if   widM.isChecked(): new = "m"
        elif widW.isChecked(): new = "w"
        else:                  new = ""
        
        if new != old:
            self.main.set_sex(self.ID, new)
            self.main.update_table_row(self.ID) # always update due to coloring of id column

