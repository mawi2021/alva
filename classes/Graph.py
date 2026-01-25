from PyQt5.QtWebChannel       import QWebChannel
from PyQt5.QtWidgets          import QMainWindow
from PyQt5.QtCore             import QUrl, QObject, pyqtSlot, pyqtSignal
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets          import *
import os
import webbrowser

# classes GraphHTML & GraphList & Bridge

class GraphHtml(QMainWindow):   
    # ----- Read GUI Content from UI File ---------------------------- *
    def __init__(self, main, idList, lineList, minYear, maxYear, mode):
        super().__init__()
  
        self.main       = main

        self.ids        = idList
        self.lines      = lineList
        self.minYear    = minYear
        self.maxYear    = maxYear
        self.mode       = mode
        
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

        if mode == "ancestor":
            self.calc_coords_anc()
        else:
            self.calc_coords_desc()

        self.window = QWebEngineView()
        self.setCentralWidget(self.window)

        self.bridge = Bridge()   # to have the click-event-listener
        self.bridge.clicked.connect(self.on_clicked)

        channel = QWebChannel(self.window.page())
        channel.registerObject("pyBridge", self.bridge)
        self.window.page().setWebChannel(channel)

        if mode == "ancestor":
            html = self.get_html_anc()
        else:
            html = self.get_html_desc()

        base_dir = os.path.abspath(os.path.dirname(__file__) + os.sep + "..")
        self.base_url = QUrl.fromLocalFile(base_dir + os.sep)
        self.window.setHtml(html, self.base_url)        
        self.resize(1000, 1000)
    @pyqtSlot(str, int, int)
    def calc_coords_anc(self):
        # Simple approach; optimization is a later step ;o) #
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

                if box["father"] == -1 and box["mother"] == -1:
                    continue  # Kann das vorkommen?

                if box["father"] != -1:
                    pers_left = box["father"]
                else:
                    pers_left = box["mother"]

                if self.ids[pers_left]["x"] == 0:
                    continue

                if box["mother"] != -1:      
                    pers_right = box["mother"]   # can be the same as pers_left
                else:
                    pers_right = box["father"]   # can be the same as pers_left
                
                if self.ids[pers_right]["x"] == 0:
                    continue            

                # adjust
                box["x"] = int(( self.ids[pers_left]["x"] + self.ids[pers_right]["x"] ) / 2)
                found = True
        
        self.yMax = 2 * self.boxOffset + (self.maxYear - self.minYear) * self.dotPerYear + self.boxHeight
    def calc_coords_desc(self):
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
    def get_html_pre(self):
        ret = "<!DOCTYPE html>\n" + \
              "<html>\n" + \
              "<head>\n" + \
              "  <meta name='viewport' content='width=device-width, initial-scale=1'>\n" + \
              "  <script type='text/javascript' src='qrc:///qtwebchannel/qwebchannel.js'></script>\n" + \
              "  <link rel='stylesheet' href='styles/app.css'>\n" + \
              "</head>\n" + \
              "<body>\n" + \
              "  <script>\n" + \
              "  (function() {\n" + \
              "      function initChannel() {\n" + \
              "      new QWebChannel(qt.webChannelTransport, function(channel) {\n" + \
              "          window.pyBridge = channel.objects.pyBridge;\n" + \
              "          document.querySelectorAll('.clickable').forEach(function(el) {\n" + \
              "          el.addEventListener('click', function(ev) {\n" + \
              "              const id = el.id || '';\n" + \
              "              const x = Math.round(ev.clientX);\n" + \
              "              const y = Math.round(ev.clientY);\n" + \
              "              if (window.pyBridge && window.pyBridge.onDivClicked) {\n" + \
              "              window.pyBridge.onDivClicked(id, x, y);\n" + \
              "              }\n" + \
              "          }, { passive: true });\n" + \
              "          });\n" + \
              "      });\n" + \
              "      }\n" + \
              "      if (document.readyState === 'complete' || document.readyState === 'interactive') {\n" + \
              "      initChannel();\n" + \
              "      } else {\n" + \
              "      document.addEventListener('DOMContentLoaded', initChannel, { once: true });\n" + \
              "      }\n" + \
              "  })();\n" + \
              "  </script>\n" + \
              "  <div class='layer' style='width:" + str(self.xMax) + "px;height:" + str(self.yMax) + "px;'>\n"

        # svg begin
        ret = ret + '<svg xmlns="http://www.w3.org/2000/svg"' + \
                    '  width="'  + str(self.xMax) + \
                    '" height="' + str(self.yMax) + '"  style="position:absolute;top:0;left:0;border:1px solid #ccc;">\n'    

        # scale with years (<line>)
        ret = ret + '  <line x1="0" y1="0" x2="0" y2="' + str(round(self.yMax)) + '" stroke="white" stroke-width="1" />\n'
        for i in range(self.minYear, self.maxYear+21):
            if i % 10 == 0:
                y = int(round(i - self.minYear) * self.dotPerYear + self.boxOffset) 
                ret = ret + \
                    '  <line x1="0" y1="' + str(y) + '" x2="10" y2="' + str(y) + '" stroke="white" stroke-width="1" />\n' + \
                    '  <text x="15" y="' + str(y+4) + '" font-size="11" fill="white">' + str(i) + '</text>\n'  # 6 = half font size

        return ret
    def get_html_anc(self):   # Ancestors = Vorfahren
        ret = self.get_html_pre()

        # Lines between boxes #
        for line in self.lines: 
            box1 = line["boxLeft"]
            box2 = line["boxRight"]
            person1 = self.ids[box1]
            person2 = self.ids[box2]

            if self.rechtwinklig:
                a = 5  # depends on padding
                ret = ret + \
                    '<line x1="' + str(round(person2["x"] + self.boxWidth/2) + a) + \
                        '" y1="' + str(round(person2["y"] + self.minHeight + 10)) + \
                        '" x2="' + str(round(person2["x"] + self.boxWidth/2) + a) + \
                        '" y2="' + str(round(person1["y"] - 30)) + \
                        '" stroke="black" stroke-width="1" />' + \
                    '<line x1="' + str(round(person2["x"] + self.boxWidth/2) + a) + \
                        '" y1="' + str(round(person1["y"] - 30)) + \
                        '" x2="' + str(round(person1["x"] + self.boxWidth/2) + a) + \
                        '" y2="' + str(round(person1["y"] - 30)) + \
                        '" stroke="black" stroke-width="1" />' + \
                    '<line x1="' + str(round(person1["x"] + self.boxWidth/2) + a) + \
                        '" y1="' + str(round(person1["y"] - 30)) + \
                        '" x2="' + str(round(person1["x"] + self.boxWidth/2) + a) + \
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

        # boxes with person data (<div>) and plus-icon for new children #
        for key in self.ids:
            person = self.ids[key]
            if person["SEX"] == 'm':
                sex_class = 'man '
            elif person["SEX"] in ('f', 'w'):
                sex_class = 'woman '
            
            if person["finished"] == 'X':
                finished_class = "solid "
            else:
                finished_class = "dotted "

            ret = ret + "\n" + \
                  "<div class='box' style='top: " + str(person["y"]) + "px; left: " + str(person["x"]) + "px;'>\n" + \
                  "  <div id='" + str(person["id"]) + "' class='box_inner clickable " + sex_class + finished_class + "'>\n" + \
                  "    <b>"  + person["GIVN"] + \
                  "    <br>" + person["SURN"] + "</b>" + \
                  "    <br>" + person["birth"] + \
                  "    <br>" + person["death"] + \
                  "  </div>\n" + \
                  "  <div id='" + str(person["id"]) + "_add_child' class='clickable' style='position:relative;top:-3px;'>" + \
                  "    <img src='icons/cross.png'>\n" + \
                  "  </div>\n" + \
                  "</div>\n"

            # id, url(s) and up / down for ancestors and descendants
            ret = ret + self.get_html_click_icons(person)

        ret = ret + "\n  </div>\n</body>\n</html>"
        return ret
    def get_html_desc(self):    # Descentants = Nachfahren
        ret = self.get_html_pre()

        # Lines between boxes #
        for line in self.lines: 
            box1 = line["boxLeft"]
            box2 = line["boxRight"]
            person1 = self.ids[box1]
            person2 = self.ids[box2]

            if self.rechtwinklig:
                a = 5  # depends on padding
                ret = ret + \
                    '<line x1="' + str(round(person2["x"] + self.boxWidth/2) + a) + \
                        '" y1="' + str(round(person2["y"] + self.minHeight + 10)) + \
                        '" x2="' + str(round(person2["x"] + self.boxWidth/2) + a) + \
                        '" y2="' + str(round(person2["y"] + self.minHeight + 30)) + \
                        '" stroke="black" stroke-width="1" />' + \
                    '<line x1="' + str(round(person2["x"] + self.boxWidth/2) + a) + \
                        '" y1="' + str(round(person2["y"] + self.minHeight + 30)) + \
                        '" x2="' + str(round(person1["x"] + self.boxWidth/2) + a) + \
                        '" y2="' + str(round(person2["y"] + self.minHeight + 30)) + \
                        '" stroke="black" stroke-width="1" />' + \
                    '<line x1="' + str(round(person1["x"] + self.boxWidth/2) + a) + \
                        '" y1="' + str(round(person2["y"] + self.minHeight + 30)) + \
                        '" x2="' + str(round(person1["x"] + self.boxWidth/2) + a) + \
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

        # boxes with person data (<div>) and plus-icon for new children #
        for key in self.ids:
            person = self.ids[key]
            if person["SEX"] == 'm':
                sex_class = 'man '
            elif person["SEX"] in ('f', 'w'):
                sex_class = 'woman '
            
            if person["finished"] == 'X':
                finished_class = "solid "
            else:
                finished_class = "dotted "

            ret = ret + "\n" + \
                  "<div class='box' style='top: " + str(person["y"]) + "px; left: " + str(person["x"]) + "px;'>\n" + \
                  "  <div id='" + str(person["id"]) + "' class='box_inner clickable " + sex_class + finished_class + "'>\n" + \
                  "    <b>"  + person["GIVN"] + \
                  "    <br>" + person["SURN"] + "</b>" + \
                  "    <br>" + person["birth"] + \
                  "    <br>" + person["death"] + \
                  "  </div>\n" + \
                  "  <div id='" + str(person["id"]) + "_add_child' class='clickable' style='position:relative;top:-3px;'>" + \
                  "    <img src='icons/cross.png'>\n" + \
                  "  </div>\n" + \
                  "</div>\n"

            # id, url(s) and up / down for ancestors and descendants
            ret = ret + self.get_html_click_icons(person)

        return ret + "\n  </div>\n</body>\n</html>"
    def get_html_click_icons(self, person):
        # persID to box (upper right corner outside of box)
        ret = "\n<div style='position:absolute;top:" + str(round(person["y"] -13)) + \
                "px; left:" + str(round(person["x"] + self.boxWidth) + 8) + "px;'>" + \
                "  " + str(person["id"]) + "\n</div>\n"

        # globe-icon for external websites
        cnt = 0
        if person["url"] != "":
            urls = person["url"].split("\n")
            for url in urls:
                url = url.strip()
                if url == "": 
                    continue
                ret = ret + "\n<div id='" + str(person["id"]) + "_" + str(cnt+1) + "_url' class='clickable' style='position:absolute;top:" + \
                    str(round(person["y"] + cnt * 18 + 2))  + \
                    "px; left:" + str(round(person["x"] + self.boxWidth) + 15) + "px;'>" + \
                "  <img src='icons/world2.png'>\n</div>\n"
                cnt = cnt + 1

        # Ancestors + Descendants (arrows up and down)
        ret = ret + "\n<div id='" + str(person["id"]) + "_ancestors' class='clickable' style='position:absolute;top:" + \
                str(round(person["y"] + cnt * 18 + 2)) + \
                "px; left:" + str(round(person["x"] + self.boxWidth) + 15) + "px;'>" + \
                " <img src='icons/up.png' height='16px'>\n</div>\n"
        cnt = cnt + 1
        ret = ret + "\n<div id='" + str(person["id"]) + "_descendants' class='clickable' style='position:absolute;top:" + \
                str(round(person["y"] + cnt * 18 + 2)) + \
                "px; left:" + str(round(person["x"] + self.boxWidth) + 15) + "px;'>" + \
                " <img src='icons/down.png' height='16px'>\n</div>\n"

        return ret
    def on_clicked(self, element_id: str, x: int, y: int):  # acting on click event (on a div with person box)
        try:
            if element_id.endswith('_add_child'):  # create new child
                persID = int(element_id.split('_add_child')[0])
                self.main.create_person()
                childID = self.main.get_id()
                sex = self.main.get_sex(persID)
                if sex in ("f", "w"):
                    self.main.set_mother(childID, persID)
                else:
                    self.main.set_father(childID, persID)
                self.main.set_person(childID)
                self.refresh_page_anc()

            elif element_id.endswith('_url'):  # navigate to url in browser
                tmp = element_id.split('_')
                nr = int(tmp[1])  # wievielte url soll gezeigt werden?
                persID = int(tmp[0])
                urls = self.main.get_url(persID)
                if urls != "":
                    url_list = urls.split("\n")
                    if len(url_list) >= nr:
                        webbrowser.open(url_list[nr-1])

            elif element_id.endswith('_ancestors'):  # navigate to ancestors (up)
                persID = int(element_id.split('_ancestors')[0])
                self.main.set_person(persID)
                self.ids, self.lines, self.minYear, self.maxYear = self.main.get_ancestors()
                self.calc_coords_anc()
                new_html = self.get_html_anc()
                self.window.setHtml(new_html, self.base_url)

            elif element_id.endswith('_descendants'):  # navigate to descendants (down)
                persID = int(element_id.split('_descendants')[0])
                self.main.set_person(persID)
                self.ids, self.lines, self.minYear, self.maxYear = self.main.get_descendants()
                self.calc_coords_desc()
                new_html = self.get_html_desc()
                self.window.setHtml(new_html, self.base_url)

            else:  # show person in detail view
                persID = int(element_id)
                self.main.set_person(persID)
        except: 
            self.main.add_status_message(self.main.get_text("ERROR") + ": GraphHtml => on_clicked()")
    def refresh_page_anc(self):
        for key in self.ids:
            root = self.ids[key]["id"]
            break
        self.ids, self.lines, self.minYear, self.maxYear = self.main.get_ancestors(root)
        self.calc_coords_anc()
        new_html = self.get_html_anc()
        self.window.setHtml(new_html, self.base_url)
    def refresh_page_desc(self):
        for key in self.ids:
            root = self.ids[key]["id"]
            break
        self.ids, self.lines, self.minYear, self.maxYear = self.main.get_descendants(root)
        self.calc_coords_desc()
        new_html = self.get_html_desc()
        self.window.setHtml(new_html, self.base_url)


class GraphList():
    def __init__(self, main):
        super(GraphList, self).__init__()
        self.main = main
        self.list = []
    def add_graph_ancestor_html(self, idList, lineList, minYear, maxYear):
        graph = GraphHtml(self.main, idList, lineList, minYear, maxYear, "ancestor")
        self.list.append(graph)
        return graph
    def add_graph_descendant_html(self, idList, lineList, minYear, maxYear):
        graph = GraphHtml(self.main, idList, lineList, minYear, maxYear, "descendant")
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


class Bridge(QObject):
    clicked = pyqtSignal(str, int, int)  # id, x, y
    @pyqtSlot(str, int, int)
    def onDivClicked(self, element_id: str, x: int, y: int):  # Called from JavaScript
        self.clicked.emit(element_id, x, y)  # calls GraphDescendantHtml=>on_clicked
