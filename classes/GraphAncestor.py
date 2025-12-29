from PyQt5.QtWidgets import QMainWindow, QLabel, QScrollArea
from PyQt5.QtGui import QPainter, QBrush, QColor, QFont, QPixmap, QPalette
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class GraphAncestor(QMainWindow):

    # ----- Read GUI Content from UI File ---------------------------- *
    def __init__(self, main, data, idList, lineList, minYear, maxYear):
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
        
        # each record includes: x, y, sex, mother (id), father (id), partners (list)
        # each partner record includes: fam_id, id, sex
        self.boxList  = idList
        self.lineList = lineList
        self.minYear  = minYear
        self.maxYear  = maxYear
        
        self.lineHeight = 14
        self.margin     = 10
        self.fontSize   = 8
        self.fontFace   = "Tahoma"

        self.boxWidth       = 180
        self.boxOffset      = 50
        self.windowOffset   = 10
        self.shortBoxHeight = int(4 * self.lineHeight + 0.5 * self.margin)
        self.boxHeight      = int(9 * self.lineHeight + 0.5 * self.margin)
        self.doNotRepaint   = False
        self.yMax           = 900
        self.xMax           = 1150

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

        self._calcCoords()

        self.setGeometry(400, 400, self.xMax, self.yMax)
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

        painter.drawRect(0, 0, int(self.xMax - 20), int(self.yMax - 20))
        
        # self.paint(event, painter)

        painter.end()   # new
    def paint(self, event, painter): 
        for pid in self.boxList:
            self.paintBox(painter, pid)
            print(pid)

        for line in self.lineList:
            boxL = self.boxList[line["boxLeft"]]
            boxR = self.boxList[line["boxRight"]]
            painter.drawLine(boxL["x"] + self.boxWidth, boxL["y"] + int(self.shortBoxHeight / 2),
                             boxR["x"],                 boxR["y"] + int(self.shortBoxHeight / 2))
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
    def calcCoords(self):
        # Simple approach; optimization is a later step #
        xMax = self.windowOffset
        for box in self.boxList:
            # upper left corner
            if box["idFather"] == 0 and box["idMother"] == 0:
                box["x"] = xMax
                xMax = xMax + self.boxWidth + self.boxOffset
        
        # adjust child in the middle below parents
        for pid in self.boxList:
            box = self.boxList[pid]
            if box["x"] > 0:
                continue

            idFather = box["idFather"]
            if idFather != "":
                if self.boxList[idFather]["x"] == 0:
                    continue

            idMother = box["idMother"]
            if idMother != "":
                if self.boxList[idMother]["x"] == 0:
                    continue            

            # adjust
            if   idFather == "": box["x"] = self.boxList[idMother]["x"]
            elif idMother == "": box["x"] = self.boxList[idFather]["x"]
            else: box["x"] = ( self.boxList[idFather]["x"] + self.boxList[idMother]["x"] ) / 2

        years = []
        coveredYears = 6

        # for box in self.boxList:
        #     # How many Boxes side by side?
        #     for i in range [0:coveredYears]:
        #         years[box["year"] + i] += 1
            
        #     if box["x"] == "":
        #         box["x"] = 0

        #     # Father
        #     if box.get("idFather","") == "":
                
        #     # Mother

        
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


    def calcCoords(self):   #TODO
        self.xMax = 1000
        self.yMax = 800
    def setAncestor(self, idList, lineList, minYear, maxYear):
        #called from PersonWidget.py
        self.idList   = idList
        self.lineList = lineList
        self.minYear  = minYear
        self.maxYear  = maxYear