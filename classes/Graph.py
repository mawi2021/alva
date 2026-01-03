from PyQt5.QtWidgets import QMainWindow, QLabel, QScrollArea
from PyQt5.QtGui     import QPainter, QBrush, QColor, QFont, QPixmap, QPalette
from PyQt5.QtCore    import Qt
from PyQt5.QtGui     import *
from PyQt5.QtCore    import *
from PyQt5.QtWidgets import *

# classes GraphAncestor & GraphDescendant & GraphList

class GraphAncestor(QMainWindow):
    # ----- Read GUI Content from UI File ---------------------------- *
    def __init__(self, main, idList, lineList, minYear, maxYear):
        super().__init__()
        self.main       = main
        self.rootPid    = ""
        
        # each record includes: x, y, sex, mother (id), father (id), partners (list)
        # each partner record includes: fam_id, id, sex
        self.ids    = idList
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

        self.calc_coords()

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
        for pid in self.ids:
            print(pid)
            self.paintBox(painter, pid)

        for line in self.lineList:
            boxL = self.ids[line["boxLeft"]]
            boxR = self.ids[line["boxRight"]]
            painter.drawLine(int(boxL["x"] + self.boxWidth / 2), boxL["y"],
                             int(boxR["x"] + self.boxWidth / 2), boxR["y"] + self.shortBoxHeight)
    def paintBox(self, painter, persID):
        box = self.ids[persID]
        x = box["x"]
        y = box["y"]
        line = 1

        # Background Color of box depending on persons sex
        if box["SEX"] == "m":
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
        text = box["GIVN"]
        painter.drawText( x + self.margin, y + line * self.lineHeight, text )  # Vorname
        line = line + 1
        painter.drawText( x + self.margin, y + line * self.lineHeight, box["SURN"])  # Nachname

        # ID 
        painter.drawText(x - self.margin, y + int((line - 2.3) * self.lineHeight), str(persID))

        # Birth
        line = line + 1
        painter.setFont(QFont(self.fontFace, self.fontSize, QFont.Normal))
        painter.drawText( x + self.margin, y + line * self.lineHeight, box["birth"], )

        # Death
        line = line + 1
        painter.drawText( x + self.margin, y + line * self.lineHeight, box["death"], )
    def calc_coords(self):
        # Simple approach; optimization is a later step #
        self.xMax = self.windowOffset
        for persID in self.ids:
            box = self.ids[persID]
            # y-Coordinate - start with upper left corner
            box["y"] = self.boxOffset + (box["year"] - self.minYear) * self.dotPerYear

            # x-Coordinate - start with upper left corner
            if box["father"] == -1 and box["mother"] == -1:
                box["x"] = self.xMax
                self.xMax = self.xMax + self.boxWidth + self.boxOffset
            else:
                box["x"] = 0
        
        # adjust child in the middle below parents
        found = True
        while found:
            found = False
            for persID in self.ids:
                box = self.ids[persID]
                if box["x"] > 0:
                    continue

                idFather = box["father"]
                if idFather != -1:
                    if self.ids[idFather]["x"] == 0:
                        continue

                idMother = box["mother"]
                if idMother != -1:
                    if self.ids[idMother]["x"] == 0:
                        continue            

                # adjust
                if   idFather == -1: box["x"] = self.ids[idMother]["x"]
                elif idMother == -1: box["x"] = self.ids[idFather]["x"]
                else: box["x"] = int(( self.ids[idFather]["x"] + self.ids[idMother]["x"] ) / 2)
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


class GraphDescendant(QMainWindow):
    # ----- Read GUI Content from UI File ---------------------------- *
    def __init__(self, main, idList, lineList, minYear, maxYear):
        super().__init__()
        self.main       = main
        self.rootPid    = ""
        
        # each record includes: x, y, sex, mother (id), father (id), partners (list)
        # each partner record includes: fam_id, id, sex
        self.ids    = idList
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

        self.calc_coords()

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
        for pid in self.ids:
            print(pid)
            self.paintBox(painter, pid)

        for line in self.lineList:
            boxL = self.ids[line["boxLeft"]]
            boxR = self.ids[line["boxRight"]]
            painter.drawLine(int(boxL["x"] + self.boxWidth / 2), boxL["y"],
                             int(boxR["x"] + self.boxWidth / 2), boxR["y"] + self.shortBoxHeight)
    def paintBox(self, painter, persID):
        box = self.ids[persID]
        x = box["x"]
        y = box["y"]
        line = 1

        # Background Color of box depending on persons sex
        if box["SEX"] == "m":
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
        text = box["GIVN"]
        painter.drawText( x + self.margin, y + line * self.lineHeight, text )  # Vorname
        line = line + 1
        painter.drawText( x + self.margin, y + line * self.lineHeight, box["SURN"])  # Nachname

        # ID 
        painter.drawText(x - self.margin, y + int((line - 2.3) * self.lineHeight), str(persID))

        # Birth
        line = line + 1
        painter.setFont(QFont(self.fontFace, self.fontSize, QFont.Normal))
        painter.drawText( x + self.margin, y + line * self.lineHeight, box["birth"], )

        # Death
        line = line + 1
        painter.drawText( x + self.margin, y + line * self.lineHeight, box["death"], )
    def calc_coords(self):
        # Simple approach; optimization is a later step #
        self.xMax = self.windowOffset
        for persID in self.ids:
            box = self.ids[persID]
            # y-Coordinate - start with upper left corner
            box["y"] = self.boxOffset + (box["year"] - self.minYear) * self.dotPerYear

            # x-Coordinate - start with upper left corner
            if box["children"] == []:
                box["x"] = self.xMax
                self.xMax = self.xMax + self.boxWidth + self.boxOffset
            else:
                box["x"] = 0
        
        # adjust child in the middle below parents
        found = True
        while found:
            found = False
            for persID in self.ids:
                box = self.ids[persID]
                if box["x"] > 0:
                    continue

                if len(box["children"]) == 0:
                    continue  # Kann das vorkommen?

                child_left = box["children"][0]
                if self.ids[child_left]["x"] == 0:
                    continue

                child_right = box["children"][len(box["children"])-1]  # can be the same as child_left
                if self.ids[child_right]["x"] == 0:
                    continue            

                # adjust
                box["x"] = int(( self.ids[child_left]["x"] + self.ids[child_right]["x"] ) / 2)
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


class GraphList():
    def __init__(self, main):
        super(GraphList, self).__init__()
        self.main = main
        self.list = []
    def add_graph_ancestor(self, idList, lineList, minYear, maxYear):
        graph = GraphAncestor(self.main, idList, lineList, minYear, maxYear)
        self.list.append(graph)
        return graph
    def add_graph_descendant(self, idList, lineList, minYear, maxYear):
        graph = GraphDescendant(self.main, idList, lineList, minYear, maxYear)
        self.list.append(graph)
        return graph    
    def setPerson(self, id):
        if id == "":
            return
        for graph in self.list:
            graph.setPerson(id)
    def update(self):
        for graph in self.list:
            graph.update()
    def clear(self):
        for graph in self.list:
            graph.clearGraph()
    def close(self):
        for graph in self.list:
            graph.close()
            self.list.remove(graph)
