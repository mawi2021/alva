from PyQt5.QtWidgets import QMainWindow, QLabel, QScrollArea
from PyQt5.QtGui import QPainter, QBrush, QColor, QFont, QPixmap, QPalette
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class Graph(QMainWindow):

    # ----- Read GUI Content from UI File ---------------------------- *
    def __init__(self, main, data, id):
        super().__init__()
        self.main       = main
        self.data       = data

        self.gedWindow  = QMainWindow()
        self.rootPid    = ""
        self.boxNumMax  = 0
        self.xMitte     = 0
        self.yMitte     = 0
        self.yRootMitte = 0
        self.xRootMitte = 0
        
        # List of people id: {}
        # each record includes: x, y, sex, relation, mother (id), father (id), partners (list)
        # each partner record includes: fam_id, id, sex
        self.boxList = {}
        self.lineList = []
        
        self.lineHeight = 14
        self.margin = 10
        self.fontSize = 8
        self.fontFace = "Tahoma"

        self.boxWidth = 180
        self.boxOffset = 50
        self.windowOffset = 10
        self.shortBoxHeight = int(4 * self.lineHeight + 0.5 * self.margin)
        self.boxHeight      = int(9 * self.lineHeight + 0.5 * self.margin)
        self.doNotRepaint = False

        self.colorMan = QColor(205, 164, 118, 255)
        self.frameColorMan = QColor("black")
        self.colorWoman = QColor(239, 223, 207, 255)
        self.frameColorWoman = QColor("white")
        self.frameColorBloodline = Qt.red
        self.backgroundColor = QColor(220,220,220)
        self.fontColor = Qt.black
        self.partnerFontColor = QColor(100,100,100)
        self.shadowColor = QColor(220,220,220,255)
        self.centralColor = QColor("purple")

        self.setPerson(id)

        self.yMax = 900
        self.xMax = 1150
        self.setGeometry(400, 400, self.xMax, self.yMax)
        self.vertical = False
        self.label = QLabel()
        self.pixmap = QPixmap(self.xMax, self.yMax)
        self.label.setPixmap(self.pixmap)
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        self.scrollArea = QScrollArea()
        self.scrollArea.setBackgroundRole(QPalette.Dark)
        self.scrollArea.setWidget(self.label)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded) 
        self.scrollArea.setVisible(True)
        self.scrollArea.setWidgetResizable(True)
        self.setCentralWidget(self.scrollArea)               
        
        # self.setCentralWidget(self.label)
        self.label.mousePressEvent = self.onMouseClick
    def onMouseClick(self, event):
        x = event.pos().x()
        y = event.pos().y()
        
        self.doNotRepaint = True

        for pid in self.boxList:
            box = self.boxList[pid]
            if x >= box["x"] and x < box["x"] + self.boxWidth:
                if y >= box["y"] and y <= box["y"] + self.shortBoxHeight:
                    self.main.widget.setPerson(pid)
                    self.doNotRepaint = False
                    return
                # Person itself - no match; check partners:
                cnt = 0
                if box["partners"]:
                    for partner in box["partners"]:
                        cnt = cnt + 1
                        yPartner = box["y"] + cnt * self.shortBoxHeight
                        if y >= yPartner and y <= yPartner + self.shortBoxHeight:
                            self.main.widget.setPerson(partner)
                            self.doNotRepaint = False
                            return
    def paintEvent(self, event):
        pixi = QPixmap(self.xMax, self.yMax)
        self.label.setPixmap(pixi)
        painter = QPainter(self.label.pixmap())

        # painter.begin(self) # new

        brush = QBrush()
        brush.setColor(self.backgroundColor)
        brush.setStyle(Qt.SolidPattern)
        painter.setBrush(brush)
        painter.setPen(self.fontColor)

        painter.drawRect(0, 0, int(self.xMax - 1), int(self.yMax - 1))
        
        if self.vertical:
            self.paintVertical(event, painter)
        else:
            self.paintHorizontal(event, painter)

        painter.end()   # new
    def paintHorizontal(self, event, painter): 
        for pid in self.boxList:
            self.paintBox(painter, pid)
            print(pid)

        for line in self.lineList:
            # print("boxL: " + line["boxLeft"])
            boxL = self.boxList[line["boxLeft"]]
            boxR = self.boxList[line["boxRight"]]
            painter.drawLine(boxL["x"] + self.boxWidth, boxL["y"] + int(self.shortBoxHeight / 2),
                             boxR["x"],                 boxR["y"] + int(self.shortBoxHeight / 2))
    def paintVertical(self, event, painter):
        pass
    def paintBox(self, painter, pid):

        box = self.boxList[pid]
        x = box["x"]
        y = box["y"]
        line = 1

        # Background Color of box depending on persons sex
        if box["sex"] == "m":
            painter.setBrush(QBrush(self.colorMan, Qt.SolidPattern))
            painter.setPen(self.frameColorMan)
        else:
            painter.setBrush(QBrush(self.colorWoman, Qt.SolidPattern))
            painter.setPen(self.frameColorWoman)

        # colored box
        painter.drawRect(x, y, self.boxWidth, self.shortBoxHeight)

        # Bloodline
        if box["relation"] in ["Opa", "Oma", "Vater", "Mutter", "Sohn", "Tochter", "Enkelsohn", 
                              "Enkeltochter"]:
            painter.setPen(self.frameColorBloodline)
            painter.drawRect(x-2, y-2, self.boxWidth + 4, self.shortBoxHeight + 2)
            painter.drawRect(x-1, y-1, self.boxWidth + 2, self.shortBoxHeight)

        painter.setPen(self.fontColor)

        # 2 lines with the name
        ret, nameArr = self.data.getName(pid)
        painter.setFont(QFont(self.fontFace, self.fontSize, QFont.ExtraBold))
        if ret:
            if box["relation"] == "":
                text = nameArr["firstname"]
            else:
                text = "(" + box["relation"] + ") " + nameArr["firstname"]
            painter.drawText( x + self.margin, y + line * self.lineHeight, text )  # Vorname
            line = line + 1
        if len(nameArr) > 1:
            painter.drawText(
                x + self.margin, y + line * self.lineHeight, nameArr["surname"]
            )  # Nachname

        # ID 
        painter.drawText(x - self.margin, y + int((line - 2.3) * self.lineHeight), pid[2:-1])

        # Birth
        line = line + 1
        ret, eventArr = self.data.getBirthData(pid)  # date - place 
        painter.setFont(QFont(self.fontFace, self.fontSize, QFont.Normal))
        if ret:
            painter.drawText(
                x + self.margin,
                y + line * self.lineHeight,
                "* " + eventArr["date"] + " " + eventArr["place"],
            )

        # Death
        line = line + 1
        ret, eventArr = self.data.getDeathData(pid)  # date - place - source
        if ret:
            painter.drawText(
                x + self.margin,
                y + line * self.lineHeight,
                "+ " + eventArr["date"] + " " + eventArr["place"],
            )

        # ---------------------- *
        # Show all Partners here *
        # ---------------------- *
                
        # Partner
        if box["partners"]:
            cnt = 0
            for partnerPid in box["partners"]:
                cnt = cnt + 1
                y2 = y + cnt * self.shortBoxHeight + 1
                line = 1
                
                ret, sex = self.data.getSex(partnerPid)
                if ret and sex == "m":
                    painter.setBrush(QBrush(self.colorMan, Qt.SolidPattern))
                    painter.setPen(self.frameColorMan)
                else:
                    painter.setBrush(QBrush(self.colorWoman, Qt.SolidPattern))
                    painter.setPen(self.frameColorWoman)
                painter.drawRect(x, y2, self.boxWidth, self.shortBoxHeight)
                
                painter.setPen(self.partnerFontColor)

                # Marriage
                fam = self.data.getFamilyForPair(pid,partnerPid)
                ret, marrStruc = self.data.getMarriageForFam(fam)
                if ret:
                    text = "oo " + marrStruc["date"] + " " + marrStruc["place"]
                else:
                    text = "oo"
                painter.drawText( x + self.margin, y2 + line * self.lineHeight, text )
                
                # Name
                ret, nameArr = self.data.getName(partnerPid)
                if ret:
                    line = line + 1
                    painter.setFont(QFont(self.fontFace, self.fontSize, QFont.ExtraBold))
                    painter.drawText(
                        x + self.margin,
                        y2 + line * self.lineHeight,
                        nameArr["firstname"] + " " + nameArr["surname"],
                    )
                    
                # Birth
                ret, eventArr = self.data.getBirthData(partnerPid)  # date - place - source
                if ret:
                    line = line + 1
                    painter.setFont(QFont(self.fontFace, self.fontSize, QFont.Normal))
                    painter.drawText(
                        x + self.margin,
                        y2 + line * self.lineHeight,
                        "* " + eventArr["date"] + " " + eventArr["place"],
                    )
                    
                # Death
                ret, eventArr = self.data.getDeathData(partnerPid)  # date - place - source
                if ret:
                    line = line + 1
                    painter.drawText(
                        x + self.margin,
                        y2 + line * self.lineHeight,
                        "+ " + eventArr["date"] + " " + eventArr["place"],
                    )
        painter.setPen(self.fontColor)

        # extra frame for setting this person as a central person
        if pid == self.rootPid:
            painter.setPen(self.centralColor)
            painter.setBrush(QBrush(Qt.NoBrush))
            for i in range(0,4):
                painter.drawRect(x - i, y - i, self.boxWidth + 2, self.shortBoxHeight + 2)

        return
    def setVertical(self, value): # True / False
        self.vertical = value
    def setPerson(self, pid):
        if self.rootPid == pid:
            return
        
        self.rootPid = pid

        parentList        = []  # List of pids
        grandparentList   = {}
        parentsiblingList = {}  # Uncles and Aunts
        cousinList        = {}  # List of pids
        childList         = {}  # List of pids
        grandchildList    = {}

        # Parents
        fatherID, motherID = self.data.getParentsIDs(self.rootPid)
        if fatherID != "":
            parentList.append(fatherID)
        if motherID != "":
            parentList.append(motherID)
        
        # Grandparents
        x = self.windowOffset
        for pid in parentList:
            fatherID, motherID = self.data.getParentsIDs(pid)
            if fatherID != "":
                grandparentList[fatherID] = {"x": x, "y": 0, "sex": "m", "relation": "Opa"}
            if motherID != "":
                grandparentList[motherID] = {"x": x, "y": 0, "sex": "w", "relation": "Oma"}
            
        # Parents, Uncles and Aunts
        x = x + self.boxWidth + self.boxOffset
        for key in grandparentList:
            person = grandparentList[key]
            ret, list = self.data.getChildren(key)
            for elem in list:
                if elem not in parentsiblingList:
                    self.lineList.append({"boxLeft":key, "boxRight": elem})
                    ret, sex = self.data.getSex(elem)
                    if elem in parentList:
                        if sex == "m":
                            parentsiblingList[elem] = {"x": x, "y": 0, "sex": sex, "relation": "Vater"}
                        else:
                            parentsiblingList[elem] = {"x": x, "y": 0, "sex": sex, "relation": "Mutter"}                        
                    else:
                        if sex == "m":
                            parentsiblingList[elem] = {"x": x, "y": 0, "sex": sex, "relation": "Onkel"}
                        else:
                            parentsiblingList[elem] = {"x": x, "y": 0, "sex": sex, "relation": "Tante"}
                if person["sex"] == "m":
                    parentsiblingList[elem]["father"] = key
                else:
                    parentsiblingList[elem]["mother"] = key
        # If no grandparents, then no grandparents found - add parent boxes manually
        if len(grandparentList) == 0:
            for elem in parentList:
                if elem not in parentsiblingList:
                    ret, sex = self.data.getSex(elem)
                    if sex == "m":
                        parentsiblingList[elem] = {"x": x, "y": 0, "sex": sex, "relation": "Vater"}
                    else:
                        parentsiblingList[elem] = {"x": x, "y": 0, "sex": sex, "relation": "Mutter"}                        

        # Brothers, Sisters, Cousins and me
        x = x + self.boxWidth + self.boxOffset
        for key in parentsiblingList:
            person = parentsiblingList[key]
            ret, list = self.data.getChildren(key)
            for elem in list:
                if elem not in cousinList:
                    self.lineList.append({"boxLeft":key, "boxRight": elem})
                    ret, sex = self.data.getSex(elem)
                    if elem == self.rootPid:
                        cousinList[elem] = {"x": x, "y": 0, "sex": sex, "relation": ""}
                    elif key in parentList:
                        if sex == "m":
                            cousinList[elem] = {"x": x, "y": 0, "sex": sex, "relation": "Bruder"}
                        else:
                            cousinList[elem] = {"x": x, "y": 0, "sex": sex, "relation": "Schwester"}
                    else:
                        if sex == "m":
                            cousinList[elem] = {"x": x, "y": 0, "sex": sex, "relation": "Cousin"}
                        else:
                            cousinList[elem] = {"x": x, "y": 0, "sex": sex, "relation": "Cousine"}
                if person["sex"] == "m":
                    cousinList[elem]["father"] = key
                else:
                    cousinList[elem]["mother"] = key
        # If no parents, then no siblings/cousins found - add myself manually
        if len(parentsiblingList) == 0:
            ret, sex = self.data.getSex(self.rootPid)
            cousinList[self.rootPid] = {"x": x, "y": 0, "sex": sex, "relation": ""}
            
        # Children and Nephews, Grancousins
        x = x + self.boxWidth + self.boxOffset
        for key in cousinList:
            person = cousinList[key]
            ret, list = self.data.getChildren(key)
            for elem in list:
                if elem not in childList:
                    self.lineList.append({"boxLeft":key, "boxRight": elem})
                    ret, sex = self.data.getSex(elem)
                    if key == self.rootPid:
                        if sex == "m":
                            childList[elem] = {"x": x, "y": 0, "sex": sex, "relation": "Sohn"}
                        else:
                            childList[elem] = {"x": x, "y": 0, "sex": sex, "relation": "Tochter"}
                    else:
                        if person["relation"] == "Bruder" or person["relation"] == "Schwester":
                            # if parents are Brother/Sister:
                            if sex == "m":
                                childList[elem] = {"x": x, "y": 0, "sex": sex, "relation": "Neffe"}
                            else:
                                childList[elem] = {"x": x, "y": 0, "sex": sex, "relation": "Nichte"}
                        else:
                            # if parents are Cousins
                            if sex == "m":
                                childList[elem] = {"x": x, "y": 0, "sex": sex, "relation": "Neffe 2. Grades"}
                            else:
                                childList[elem] = {"x": x, "y": 0, "sex": sex, "relation": "Nichte 2. Grades"}
                if person["sex"] == "m":
                    childList[elem]["father"] = key
                else:
                    childList[elem]["mother"] = key

        # Grandchildren
        x = x + self.boxWidth + self.boxOffset
        for key in childList:
            person = childList[key]
            ret, list = self.data.getChildren(key)
            for elem in list:
                if elem not in grandchildList:
                    self.lineList.append({"boxLeft":key, "boxRight": elem})
                    ret, sex = self.data.getSex(elem)
                    if person["relation"] == "Sohn" or person["relation"] == "Tochter":
                        if sex == "m":
                            grandchildList[elem] = {"x": x, "y": 0, "sex": sex, "relation": "Enkelsohn"}
                        else:
                            grandchildList[elem] = {"x": x, "y": 0, "sex": sex, "relation": "Enkeltochter"}
                    elif person["relation"] == "Neffe" or person["relation"] == "Nichte":
                        if sex == "m":
                            grandchildList[elem] = {"x": x, "y": 0, "sex": sex, "relation": "Großneffe"}
                        else:
                            grandchildList[elem] = {"x": x, "y": 0, "sex": sex, "relation": "Großnichte"}
                    else:
                        if sex == "m":
                            grandchildList[elem] = {"x": x, "y": 0, "sex": sex, "relation": "Großneffe 2. Grades"}
                        else:
                            grandchildList[elem] = {"x": x, "y": 0, "sex": sex, "relation": "Großnichte 2. Grades"}
                if person["sex"] == "m":
                    grandchildList[elem]["father"] = key
                else:
                    grandchildList[elem]["mother"] = key

        # Fill Boxes, Add Partners, Calculate yMax
        y = self.windowOffset
        for key in grandparentList: # Partners of Grandparents are ignored
            grandparentList[key]["y"] = y
            grandparentList[key]["partners"] = []
            y = y + self.shortBoxHeight # + self.boxOffset   
        yMax = y
        y1 = y
            
        y = self.windowOffset
        for key in parentsiblingList:
            parentsiblingList[key]["y"] = y
            ret, parentsiblingList[key]["partners"] = self.data.getPartners(key)
            if parentsiblingList[key]["partners"]:
                for gp in parentsiblingList[key]["partners"]:
                    if gp in parentsiblingList:
                        # remove this partner in partner list
                        parentsiblingList[key]["partners"].remove(gp)
            # Are there still Partners?
            if parentsiblingList[key]["partners"]:
                y = y + self.boxOffset + (len(parentsiblingList[key]["partners"]) + 1) * self.shortBoxHeight          
            else: y = y + self.boxOffset + self.shortBoxHeight
        yMax = max(y, yMax)
        y2 = y
            
        y = self.windowOffset
        for key in cousinList:
            cousinList[key]["y"] = y
            ret, cousinList[key]["partners"] = self.data.getPartners(key)
            if cousinList[key]["partners"]:
                y = y + self.boxOffset + (len(cousinList[key]["partners"]) + 1) * self.shortBoxHeight          
            else: y = y + self.boxOffset + self.shortBoxHeight    
        yMax = max(y, yMax)
        y3 = y

        y = self.windowOffset
        for key in childList:
            childList[key]["y"] = y
            ret, childList[key]["partners"] = self.data.getPartners(key)
            if childList[key]["partners"]:
                y = y + self.boxOffset + (len(childList[key]["partners"]) + 1) * self.shortBoxHeight          
            else: y = y + self.boxOffset + self.shortBoxHeight
        yMax = max(y, yMax)
        y4 = y

        y = self.windowOffset
        for key in grandchildList:
            grandchildList[key]["y"] = y
            ret, grandchildList[key]["partners"] = self.data.getPartners(key)
            if grandchildList[key]["partners"]:
                y = y + self.boxOffset + (len(grandchildList[key]["partners"]) + 1) * self.shortBoxHeight          
            else: y = y + self.boxOffset + self.shortBoxHeight
        yMax = max(y, yMax)
        y5 = y

        self.yMax = int(yMax + self.windowOffset)
        
        # Norm y-Values in the centre of verticale axis
        self.boxList = {}
        for key in grandparentList:
            grandparentList[key]["y"] = grandparentList[key]["y"] + int((self.yMax - y1) / 2)
            self.boxList[key] = grandparentList[key]            
        for key in parentsiblingList:
            parentsiblingList[key]["y"] = parentsiblingList[key]["y"] + int((self.yMax - y2) / 2)
            self.boxList[key] = parentsiblingList[key]            
        for key in cousinList:
            cousinList[key]["y"] = cousinList[key]["y"] + int((self.yMax - y3) / 2)
            self.boxList[key] = cousinList[key]        
        for key in childList:
            childList[key]["y"] = childList[key]["y"] + int((self.yMax - y4) / 2)
            self.boxList[key] = childList[key]                    
        for key in grandchildList:
            grandchildList[key]["y"] = grandchildList[key]["y"] + int((self.yMax - y5) / 2)
            self.boxList[key] = grandchildList[key]     
    def clearGraph(self):
        # self.person["Grandparents"]   = []
        # self.person["Parents"]        = []  # List of pids
        # self.person["Children"]       = []  # List of pids
        # self.person["Siblings"]       = []  # List of pids
        # self.person["Partners"]       = []  # List of pids
        # self.person["Grandchildren"]  = []
        # self.person["Parentsiblings"] = []

        # self.label.pixmap().fill(self.backgroundColor)
        # self.update();
        self.main.graphList.update()

