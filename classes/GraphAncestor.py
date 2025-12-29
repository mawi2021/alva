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
        self.rootPid    = ""
        
        # each record includes: x, y, sex, mother (id), father (id), partners (list)
        # each partner record includes: fam_id, id, sex
        self.boxList    = idList
        self.lineList   = lineList
        self.minYear    = minYear
        self.maxYear    = maxYear
        self.dotPerYear = 6
        
        self.lineHeight = 14
        self.margin     = 10
        self.fontSize   = 8
        self.fontFace   = "Tahoma"

        self.boxWidth       = 180
        self.boxOffset      = 50
        self.windowOffset   = 100
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

        self.setGeometry(400, 400, 1200, 800)   # self.xMax, self.yMax)
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

        # Drawings independent on boxes:
        painter.drawRect(0, 0, int(self.xMax - 20), int(self.yMax - 20))
        painter.drawLine(50, 0, 50, self.yMax)
        for i in range((self.maxYear - self.minYear), self.maxYear, 10):
            j = round(i/10) * 10
            y = self.boxOffset + (j - self.minYear) * self.dotPerYear
            painter.drawLine(45, y, 55, y)
            painter.drawText(10, y, str(j))

        self.paint(event, painter)

        painter.end()   # new
    def paint(self, event, painter): 
        for pid in self.boxList:
            print(pid)
            self.paintBox(painter, pid)

        for line in self.lineList:
            boxL = self.boxList[line[0]]
            boxR = self.boxList[line[1]]
            painter.drawLine(int(boxL["x"] + self.boxWidth / 2), boxL["y"],
                             int(boxR["x"] + self.boxWidth / 2), boxR["y"] + self.shortBoxHeight)
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

        # 2 lines with the name
        painter.setPen(self.fontColor)
        painter.setFont(QFont(self.fontFace, self.fontSize, QFont.ExtraBold))
        text = box["name"]["firstname"]
        painter.drawText( x + self.margin, y + line * self.lineHeight, text )  # Vorname
        line = line + 1
        painter.drawText( x + self.margin, y + line * self.lineHeight, box["name"]["surname"])  # Nachname

        # ID 
        painter.drawText(x - self.margin, y + int((line - 2.3) * self.lineHeight), pid[2:-1])

        # Birth
        line = line + 1
        painter.setFont(QFont(self.fontFace, self.fontSize, QFont.Normal))
        painter.drawText(
            x + self.margin,
            y + line * self.lineHeight,
            "* " + box["birth"]["date"] + " " + box["birth"]["place"],
        )

        # Death
        line = line + 1
        painter.drawText(
            x + self.margin,
            y + line * self.lineHeight,
            "+ " + box["death"]["date"] + " " + box["death"]["place"],
        )

        # # ---------------------- *
        # # Show all Partners here *
        # # ---------------------- *
                
        # # Partner
        # if box["partners"]:
        #     cnt = 0
        #     for partnerPid in box["partners"]:
        #         cnt = cnt + 1
        #         y2 = y + cnt * self.shortBoxHeight + 1
        #         line = 1
                
        #         ret, sex = self.data.getSex(partnerPid)
        #         if ret and sex == "m":
        #             painter.setBrush(QBrush(self.colorMan, Qt.SolidPattern))
        #             painter.setPen(self.frameColorMan)
        #         else:
        #             painter.setBrush(QBrush(self.colorWoman, Qt.SolidPattern))
        #             painter.setPen(self.frameColorWoman)
        #         painter.drawRect(x, y2, self.boxWidth, self.shortBoxHeight)
                
        #         painter.setPen(self.partnerFontColor)

        #         # Marriage
        #         fam = self.data.getFamilyForPair(pid,partnerPid)
        #         ret, marrStruc = self.data.getMarriageForFam(fam)
        #         if ret:
        #             text = "oo " + marrStruc["date"] + " " + marrStruc["place"]
        #         else:
        #             text = "oo"
        #         painter.drawText( x + self.margin, y2 + line * self.lineHeight, text )
                
        #         # Name
        #         ret, nameArr = self.data.getName(partnerPid)
        #         if ret:
        #             line = line + 1
        #             painter.setFont(QFont(self.fontFace, self.fontSize, QFont.ExtraBold))
        #             painter.drawText(
        #                 x + self.margin,
        #                 y2 + line * self.lineHeight,
        #                 nameArr["firstname"] + " " + nameArr["surname"],
        #             )
                    
        #         # Birth
        #         ret, eventArr = self.data.getBirthData(partnerPid)  # date - place - source
        #         if ret:
        #             line = line + 1
        #             painter.setFont(QFont(self.fontFace, self.fontSize, QFont.Normal))
        #             painter.drawText(
        #                 x + self.margin,
        #                 y2 + line * self.lineHeight,
        #                 "* " + eventArr["date"] + " " + eventArr["place"],
        #             )
                    
        #         # Death
        #         ret, eventArr = self.data.getDeathData(partnerPid)  # date - place - source
        #         if ret:
        #             line = line + 1
        #             painter.drawText(
        #                 x + self.margin,
        #                 y2 + line * self.lineHeight,
        #                 "+ " + eventArr["date"] + " " + eventArr["place"],
        #             )
        # painter.setPen(self.fontColor)

        # # extra frame for setting this person as a central person
        # if pid == self.rootPid:
        #     painter.setPen(self.centralColor)
        #     painter.setBrush(QBrush(Qt.NoBrush))
        #     for i in range(0,4):
        #         painter.drawRect(x - i, y - i, self.boxWidth + 2, self.shortBoxHeight + 2)

        return
    def _calcCoords(self):
        # Simple approach; optimization is a later step #
        self.xMax = self.windowOffset
        for pid in self.boxList:
            box = self.boxList[pid]

            # y-Coordinate - start with upper left corner
            box["y"] = self.boxOffset + (box["year"] - self.minYear) * self.dotPerYear

            # x-Coordinate - start with upper left corner
            if box["idFather"] == "" and box["idMother"] == "":
                box["x"] = self.xMax
                self.xMax = self.xMax + self.boxWidth + self.boxOffset

            # Person Data
            pers = self.data.getPersonForDrawBox(pid)
            box["name"]  = pers["name"]
            box["birth"] = pers["birth"]
            box["death"] = pers["death"]
            box["sex"]   = pers["sex"]
        
        # adjust child in the middle below parents
        found = True
        while found:
            found = False
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
                else: box["x"] = int(( self.boxList[idFather]["x"] + self.boxList[idMother]["x"] ) / 2)
                found = True
        
        self.yMax = 2 * self.boxOffset + (self.maxYear - self.minYear) * self.dotPerYear + self.boxHeight
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
    def setAncestor(self, idList, lineList, minYear, maxYear):
        #called from PersonWidget.py
        self.idList   = idList
        self.lineList = lineList
        self.minYear  = minYear
        self.maxYear  = maxYear