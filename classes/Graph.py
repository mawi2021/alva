from PyQt5.QtWidgets          import QMainWindow, QLabel, QScrollArea
from PyQt5.QtGui              import QPainter, QBrush, QColor, QFont, QPixmap, QPalette
from PyQt5.QtCore             import Qt, QUrl
from PyQt5.QtGui              import *
from PyQt5.QtCore             import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets          import *
import os

# classes GraphAncestor & GraphDescendant & GraphDescendantHtml & GraphList

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
        self.ids        = idList
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
        self.main.graphList.update()


class GraphDescendantHtml(QMainWindow):
    # ----- Read GUI Content from UI File ---------------------------- *
    def __init__(self, main, idList, lineList, minYear, maxYear):
        super().__init__()
  
        self.main       = main

        self.ids        = idList
        self.lines      = lineList
        self.minYear    = minYear
        self.maxYear    = maxYear
        
        self.lineHeight     = 14
        self.margin         = 10
        self.minHeight      = 50  # should be the same as in css file
        self.dotPerYear     = 6
        self.boxWidth       = 150
        self.boxOffset      = 50
        self.windowOffset   = 100
        self.shortBoxHeight = int(4 * self.lineHeight + 0.5 * self.margin)
        self.boxHeight      = int(9 * self.lineHeight + 0.5 * self.margin)
        self.boxHeight      = int(9 * self.lineHeight + 0.5 * self.margin)
        self.boxOffset      = 50
        self.windowOffset   = 100
        self.rechtwinklig   = True   # waagerechte und senkrechte Verbinder

        self.calc_coords()
        self.window = QWebEngineView()
        html = self.get_html()
        base_dir = os.path.abspath(os.path.dirname(__file__) + os.sep + "..")
        base_url = QUrl.fromLocalFile(base_dir + os.sep)
        self.window.setHtml(html, base_url)        
        self.setCentralWidget(self.window)
        self.resize(1000, 1000)
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
    def get_html(self):
        ret = "<!DOCTYPE html>\n" + \
              "<html>\n" + \
              "<head><link rel='stylesheet' href='styles/app.css'></head>\n" + \
              "<body>\n" + \
              "  <div class='layer' style='width:'" + str(self.xMax) + "px;height:" + str(self.yMax) + "px;+'>\n"

        # svg begin
        ret = ret + '<svg xmlns="http://www.w3.org/2000/svg"' + \
                    '  width="'  + str(self.xMax) + \
                    '" height="' + str(self.yMax) + '"  style="position:absolute;top:0;left:0;border:1px solid #ccc;">\n'    

        # scale with years (<line>)
        ret = ret + '  <line x1="0" y1="0" x2="0" y2="' + str(round(self.yMax)) + '" stroke="black" stroke-width="1" />\n'
        for i in range(self.minYear, self.maxYear+21):
            if i % 10 == 0:
                y = int(round(i - self.minYear) * self.dotPerYear + self.boxOffset) 
                ret = ret + \
                    '  <line x1="0" y1="' + str(y) + '" x2="10" y2="' + str(y) + '" stroke="black" stroke-width="1" />\n' + \
                    '  <text x="15" y="' + str(y+4) + '" font-size="11" fill="black">' + str(i) + '</text>\n'  # 6 = half font size

        # Lines between boxes #
        for line in self.lines: 
            box1 = line["boxLeft"]
            box2 = line["boxRight"]
            person1 = self.ids[box1]
            person2 = self.ids[box2]

            if self.rechtwinklig:
                ret = ret + \
                    '<line x1="' + str(round(person2["x"] + self.boxWidth/2)) + \
                        '" y1="' + str(round(person2["y"] + self.minHeight + 10)) + \
                        '" x2="' + str(round(person2["x"] + self.boxWidth/2)) + \
                        '" y2="' + str(round(person2["y"] + self.minHeight + 30)) + \
                        '" stroke="black" stroke-width="1" />' + \
                    '<line x1="' + str(round(person2["x"] + self.boxWidth/2)) + \
                        '" y1="' + str(round(person2["y"] + self.minHeight + 30)) + \
                        '" x2="' + str(round(person1["x"] + self.boxWidth/2)) + \
                        '" y2="' + str(round(person2["y"] + self.minHeight + 30)) + \
                        '" stroke="black" stroke-width="1" />' + \
                    '<line x1="' + str(round(person1["x"] + self.boxWidth/2)) + \
                        '" y1="' + str(round(person2["y"] + self.minHeight + 30)) + \
                        '" x2="' + str(round(person1["x"] + self.boxWidth/2)) + \
                        '" y2="' + str(round(person1["y"])) + \
                        '" stroke="black" stroke-width="1" />'
            else:
                ret = ret + \
                    '<line x1="' + str(round(person1["x"] + self.boxWidth/2)) + \
                        '" y1="' + str(round(person1["y"])) + \
                        '" x2="' + str(round(person2["x"] + self.boxWidth/2)) + \
                        '" y2="' + str(round(person2["y"] + self.minHeight + 10)) + \
                        '" stroke="black" stroke-width="1" />'
                
        ret = ret + '</svg>'

        # boxes with person data (<div>) #
        for key in self.ids:
            person = self.ids[key]
            if person["SEX"] == 'm':
                sex_class = 'man'
            elif person["SEX"] in ('f', 'w'):
                sex_class = 'woman'
            ret = ret + "\n<div class='box " + sex_class + "' style='top: " + str(person["y"])  + \
                  "px; left: " + str(person["x"]) + "px;'><b>" + \
                           person["GIVN"] + \
                  "<br>" + person["SURN"] + \
                  "</b><br>" + person["birth"] + \
                  "<br>" + person["death"] + \
                  "</div>\n"
            
        ret = ret + "\n  </div>\n</body>\n</html>"
        return ret


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
    def add_graph_descendant_html(self, idList, lineList, minYear, maxYear):
        graph = GraphDescendantHtml(self.main, idList, lineList, minYear, maxYear)
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
