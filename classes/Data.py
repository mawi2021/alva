# TODO: check, which imports are really necessary
from genericpath import exists
from pickle import FALSE
import sys, os, chardet
from PyQt5.QtWidgets import QInputDialog, QFileDialog, QMessageBox
from PyQt5.QtCore import QStringListModel
import json
import pandas
import time
from dateutil.parser import parse

# TODO: zu allen Log-Calls (z.B. self._addToLog()) Setter schreiben 

class Data():

    def __init__(self, main, configData):
        super(Data, self).__init__()
        self.main   = main
        self.configData = configData
        
        self.logFilename = self.configData["persLog"]

        self.jData  = {}
        self.helperPersList = {}
        self.helperFamList  = {}
        self.helperNoteList = {}

    # ----- Project ----- #
    def newProject(self):
        if not os.path.exists(self.configData["projectDir"]):
            os.makedirs(self.configData["projectDir"])

        projectName, ok = QInputDialog.getText(self.main, \
                                            'Projektname', \
                                            'Bitte geben Sie einen neuen Projektnamen an:' \
                                            )

        while True:
            if not ok: return

            fileName = self.configData["projectDir"] + "/" + projectName + ".json"

            if os.path.isfile(fileName): 
                txt = "Das Projekt " + projectName + \
                      " existiert bereits. Bitte wählen Sie einen anderen Namen"
                projectName, ok = QInputDialog.getText(self.main, 'Projektname', txt )
            elif projectName == "":
                projectName, ok = QInputDialog.getText(self.main, \
                                                'Projektname', \
                                                'Bitte geben Sie einen Projektnamen an:' \
                                            )
            else:
                break

        self.main.widget.clearWidgets()
        self.configData["currProject"] = projectName
        self.configData["currProjectFile"] = fileName
        self.main.setWindowTitle("Alva - " + projectName)  
        
        # Create Project Data File #
        self.jData = {}
        f = open(fileName, 'w', encoding=self.configData["encoding"])
        json.dump(self.jData, f, indent=4, ensure_ascii=False)
        f.close()
        
        # Fill helper list for fast Access of jData #
        self._fillHelperLists()
    def openProject(self):
        print("Data.openProject")

        items = []

        # Search for files in "data" subdirectory
        files = os.listdir(self.configData["projectDir"])
        for file in files:
            if file.endswith(".json"):
                items.append(file.removesuffix(".json"))

        if len(items) == 0:
            QMessageBox.information( 
                self.main, \
                "Öffnen nicht möglich", \
                "Es wurde noch kein Projekt angelegt", \
                buttons=QMessageBox.Ok
            )
            return

        item, ok = QInputDialog.getItem(self.main, "Auswahl des Projektes", \
            "Projekte", items, 0, False)

        if not ok:
            print("  Auswahl abgebrochen")
            return

        if not item:
            print("Kein Projekt ausgewählt")
            return

        print("  Auswahl Projekt: " + item)
        self.setProject(item)
    def setProject(self,name):
        # Called from main.py and internally (openProject) #
        self.configData["currProjectFile"] = self.configData["projectDir"] + "/" + name + ".json"
        
        if ( not os.path.isfile(self.configData["currProjectFile"]) ):
            self.configData["currProjectFile"] = ""
            return
    
        self.main.setWindowTitle("Alva - " + name)  
        self.configData["currProject"] = name

        with open(self.configData["currProjectFile"], encoding=self.configData["encoding"]) as f:
            self.jData = json.load(f)
        self._fillHelperLists()
            
        # Check log file and update if desired #
        self._updateFromLog(2)    

        # In case, graphs are open, windows are closed
        self.main.widget.closeGraphs()

        # Fill PersonListWidget (Table) from columns, which are actually shown
        data = self._selectPersonList()
        if len(data) > 0:
            self.main.widget.listFrame.fillTable(data)
            self.main.widget.setPerson(self.jData["INDI"][0]["id"])      
        else:
            self.main.widget.clearWidgets()
            # Create Person, if none is available #
            self.main.widget.addPerson()

    # ----- Import / Export ----- #
    def importData(self):
        # ----- Get Filename, which is to be imported ----- #
        fileDlg = QFileDialog()
        fileStruc = fileDlg.getOpenFileName( self.main, \
                'Wählen Sie die zu importierende Datei aus', \
                "MyImport/", \
                "Gedcom (*.ged);;Excel (*.xlsx);;CSV (*.csv);;Json (*.json)"
            )
        fileName = fileStruc[0]

        # Stop if nothing chosen
        if fileName == "":
            return

        # ----- Create new project ----- #
        if self.configData["currProject"] != "":
            self.main.widget.clearWidgets()
        self.newProject()
        
        # ----- Process Data: convert Files to json ----- #
        if fileName:
            if fileName[-4:] == ".ged":
                self._convertDataFormatGedToJson(fileName)
            elif fileName[-4:] == ".csv":
                self._convertDataFormatCsvToJson(fileName)
            elif fileName[-5:] == ".json":
                self._convertDataFormatJsonToJson(fileName)
            elif fileName[-5:] == ".xlsx":
                self._convertDataFormatXlsxToJson(fileName)
            else:
                QMessageBox.information(self.main, \
                    "Einlesen nicht möglich", \
                    "Das gewählte Format wurde noch nicht implementiert", \
                    buttons=QMessageBox.Ok
                  )
                return
            
        # ----- Read json File ----- #
        with open(self.configData["currProjectFile"], \
                  encoding=self.configData["encoding"]) as f:
            self.jData = json.load(f)
        f.close()
        self._fillHelperLists()

        # ----- Show Data in Table ----- #
        data = self._selectPersonList()
        if len(data) > 0:
            self.main.widget.listFrame.fillTable(data)
        else:
            self.main.widget.clearWidgets()
    def exportData(self):
        # Conversion of json fle to ged file
        fileDlg = QFileDialog()
        fname = fileDlg.getOpenFileName( self.main, \
                'Wählen Sie die umzuwandelnde json Datei aus', \
                "MyImport/", \
                "Json (*.json)"
            )
        file_from = fname[0]
        file_to = fname[0][0:-5] + ".ged"
        
        # Stop if nothing chosen
        if file_from == "":
            return
        
        note_cnt = 1
        note_obj = []

        # ----- Header ----- #
        fw = open(file_to, 'w', encoding='utf8')
        fw.write("0 HEAD\n")
        fw.write("1 SOUR Alva\n")
        fw.write("2 CORP (private)\n")
        fw.write("3 ADDR https://alva.ur-ahn.de\n")
        fw.write("1 SUBM @SUB@\n")
        fw.write("1 GEDC\n")
        fw.write("2 VERS 5.5\n")
        fw.write("2 FORM LINEAGE-LINKED\n")
        fw.write("1 CHAR UTF-8\n")
        fw.write("1 LANG German\n")
        fw.write("0 @SUB@ SUBM\n")
        fw.write("1 NAME Manuela Kugel\n")
        fw.write("1 ADDR \n")
        fw.write("2 CONT mawi@online.de\n")
        fw.close()
        
        # ----- Read json File ----- #
        with open(file_from, encoding="utf-8") as json_file:
            data = json.load( json_file )
        
        # ----- Each Person ----- #
        i = 0
        for obj in data["INDI"]:
            f = open(file_to, 'a', encoding='utf8')
            
            i = i + 1
            if i % 250 == 0:
                print("Konvertiere " + str(i) + ". Person ")    
            
            if "id" in obj:
                f.write("0 @" + str(obj["id"]) + "@ INDI\n")
                
            if "NAME" in obj:
                if "id" in obj["NAME"]:
                    f.write("1 NAME " + obj["NAME"]["id"] + "\n")
                if "GIVN" in obj["NAME"]:
                    f.write("2 GIVN " + obj["NAME"]["GIVN"] + "\n")
                if "SURN" in obj["NAME"]:
                    f.write("2 SURN " + obj["NAME"]["SURN"] + "\n")
            
            if "SEX" in obj:
                if obj["SEX"] == "m":
                    f.write("1 SEX M\n")
                elif obj["SEX"] == "w":
                    f.write("1 SEX F\n")
                
            if "BIRT" in obj:
                f.write("1 BIRT\n")
                if "DATE" in obj["BIRT"]:
                    found, date = self._convertDateToGedFormat(obj["BIRT"]["DATE"])
                    if found:
                        f.write("2 DATE " + date + "\n")
                if "PLAC" in obj["BIRT"]:
                    f.write("2 PLAC " + obj["BIRT"]["PLAC"] + "\n")
            
            if "DEAT" in obj:
                f.write("1 DEAT\n")
                if "DATE" in obj["DEAT"]:
                    found, date = self._convertDateToGedFormat(obj["DEAT"]["DATE"])
                    if found:
                        f.write("2 DATE " + date + "\n")
                if "PLAC" in obj["DEAT"]:
                    f.write("2 PLAC " + obj["DEAT"]["PLAC"] + "\n")
            
            if "CHR" in obj:  # Taufe
                f.write("1 CHR\n")  
                if "DATE" in obj["CHR"]:
                    found, date = self._convertDateToGedFormat(obj["CHR"]["DATE"])
                    if found:
                        f.write("2 DATE " +date + "\n")
        
            if "FAMC" in obj: # my parents - can only happen once
                f.write("1 FAMC @" + str(obj["FAMC"]) + "@\n")
                
            if "FAMS" in obj:
                for fams in obj["FAMS"]:
                    f.write("1 FAMS @" + str(fams) + "@\n")
            
            # Comments
            if "comment" in obj:
                f.write("1 NOTE @N" + str(note_cnt) + "@\n")
                note_obj.append({note_cnt: "Tauf-Eintrag/Kommentar: " + obj["comment"]})
                note_cnt = note_cnt + 1
            if "comment_father" in obj:
                f.write("1 NOTE @N" + str(note_cnt) + "@\n")
                note_obj.append({note_cnt: "Tauf-Eintrag >> Vater: " + obj["comment_father"]})
                note_cnt = note_cnt + 1
            if "comment_mother" in obj:
                f.write("1 NOTE @N" + str(note_cnt) + "@\n")
                note_obj.append({note_cnt: "Tauf-Eintrag >> Mutter: " + obj["comment_mother"]})
                note_cnt = note_cnt + 1            
            
            f.close()
            
        print("Export Personen abgeschlossen")
            
        # ----- Each Family ----- #
        i = 0
        for obj in data["FAM"]:
            f = open(file_to, 'a', encoding='utf8')
            
            i = i + 1
            if i % 100 == 0:
                print("Konvertiere " + str(i) + ". Familie ")    

            if "id" in obj:
                if str(obj["id"])[0] != 'F':
                    f.write("0 @F" + str(obj["id"]) + "@ FAM\n")
                else:
                    f.write("0 @" + str(obj["id"]) + "@ FAM\n")
            
            if "HUSB" in obj:
                if str(obj["HUSB"])[0] != 'I':
                    f.write("1 HUSB @I" + str(obj["HUSB"]) + "@\n")
                else:
                    f.write("1 HUSB @" + str(obj["HUSB"]) + "@\n")
                
            if "WIFE" in obj:
                if str(obj["WIFE"])[0] != 'I':
                    f.write("1 WIFE @I" + str(obj["WIFE"]) + "@\n")
                else:
                    f.write("1 WIFE @" + str(obj["WIFE"]) + "@\n")
            
            if "CHIL" in obj:
                for chil in obj["CHIL"]:
                    if chil[0] != 'I':
                        f.write("1 CHIL @I" + chil + "@\n")
                    else:
                        f.write("1 CHIL @" + chil + "@\n")
        
            if "MARR" in obj:        
                f.write("1 MARR\n")
                if "DATE" in obj["MARR"]:
                    found, date = self._convertDateToGedFormat(obj["MARR"]["DATE"])
                    if found:
                        f.write("2 DATE " +date + "\n")
                if "PLAC" in obj["MARR"]:
                    f.write("2 PLAC " + obj["MARR"]["PLAC"] + "\n")
        
            # Kommentare (Vater, Mutter, Ehe)
            if "comment" in obj:
                f.write("1 NOTE @N" + str(note_cnt) + "@\n")
                note_obj.append({note_cnt: "Ehe-Eintrag der Eltern: " + obj["comment"]})
                note_cnt = note_cnt + 1
            if "comment_father" in obj:
                f.write("1 NOTE @N" + str(note_cnt) + "@\n")
                note_obj.append({note_cnt: "Ehe-Eintrag der Eltern >> Bräutigam: " + obj["comment_father"]})
                note_cnt = note_cnt + 1
            if "comment_mother" in obj:
                f.write("1 NOTE @N" + str(note_cnt) + "@\n")
                note_obj.append({note_cnt: "Ehe-Eintrag der Eltern >> Braut: " + obj["comment_mother"]})
                note_cnt = note_cnt + 1            
            
            f.close()
            
        print("Export Familien abgeschlossen")
            
        i = 0
        for obj in note_obj:
            i = i + 1
            if i % 500 == 0:
                print("Konvertiere " + str(i) + ". Kommentar")    

            f = open(file_to, 'a', encoding='utf8')
            for key in obj:
                obj[key] = obj[key].replace("\n", " ")
                
                if len(obj[key]) >= 70:
                    f.write("0 @N" + str(key) + "@ NOTE " + obj[key][0:70] + "\n")
                    obj[key] = obj[key][70:]
                else:
                    f.write("0 @N" + str(key) + "@ NOTE " + obj[key] + "\n")
                    obj[key] = ""
                    
                while len(obj[key]) > 0:
                    if len(obj[key]) >= 70:
                        f.write("1 CONC " + obj[key][0:70] + "\n")
                        obj[key] = obj[key][70:]
                    else:
                        f.write("1 CONC " + obj[key] + "\n")
                        obj[key] = ""

            f.close()
            
        print("Export Kommentare abgeschlossen")
            
        # ----- Footer ----- #
        fw = open(file_to, 'a', encoding='utf8')
        fw.write("0 TRLR\n")
        f.close()
        
        print("----- Export abgeschlossen -----")
    def _convertDateToGedFormat(self, date):
        dayStr = ""
        monthStr = ""
        yearStr = ""
        monthArr = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
        
        if len(date) == 10:
            
            num = date[0:2]
            if num.isnumeric():
                if 1 <= int(num) and int(num) <= 31:
                    dayStr = num
            
            num = date[3:5]
            if num.isnumeric():
                if 1 <= int(num) and int(num) <= 12:
                    monthStr = num
            
            num = date[6:10]
            if num.isnumeric():
                yearStr = num
                
        if yearStr == "":
            return False, ""
        elif monthStr == "":
            return True, yearStr
        elif dayStr == "":
            return True, monthArr[int(monthStr)-1] + " " + yearStr
        else:
            return True, dayStr + " " + monthArr[int(monthStr)-1] + " " + yearStr
    def _convertDataFormatXlsxToJson(self,fname):
        df = pandas.read_excel(fname, sheet_name="Taufen Alle", dtype=str)
        first = True
        
        print("Start Lesen der Daten aus der Excel-Datei")
        
        # Initialize File
        f = open(self.configData["currProjectFile"], 'w', encoding='utf8')
        f.write("{\n\"INDI\":\n[\n")
        f.close()

        print("Ende Lesen der Daten aus der Excel-Datei, Beginn Verarbeitung")

        # Each Row in Excel File
        for i in range(df.Vorname._values.size):
            if str(df.ID._values[i]) == "nan":
                continue        
            if i % 100 == 0 and i > 0:
                print("Konvertiere " + str(i) + ". Person ")    
            
            obj = {}
            if df.ID._values[i][0] != 'I':
                obj["id"] = 'I' + str(df.ID._values[i])
            else:
                obj["id"] = str(df.ID._values[i])
            obj["NAME"] = {}
            lv_comment = ""
            
            # Name and Sex
            obj["NAME"]["id"] = ""
            if str(df.Vorname._values[i]) != "nan":
                obj["NAME"]["GIVN"] = df.Vorname._values[i]
                obj["NAME"]["id"]   = df.Vorname._values[i] + " "
            if str(df.Nachname._values[i]) != "nan":
                obj["NAME"]["SURN"] = df.Nachname._values[i]
                obj["NAME"]["id"]   = obj["NAME"]["id"] + "/" + df.Nachname._values[i] + "/"
            if str(df.Geschlecht._values[i]) != "nan":
                obj["SEX"] = df.Geschlecht._values[i]
            if str(df.Seite._values[i])   != "nan" or \
               str(df.Nummer._values[i])  != "nan":
                lv_comment = "Geburt: KB Lohsa Seite "
                if str(df.Seite._values[i]) != "nan":
                    lv_comment = lv_comment + str(df.Seite._values[i])
                lv_comment = lv_comment + " #"
                if str(df.Nummer._values[i]) != "nan":
                    lv_comment = lv_comment + str(df.Nummer._values[i])
                lv_comment = lv_comment + " "
                if str(df.GebJahr._values[i]) != "nan":
                    lv_comment = lv_comment + str(int(df.GebJahr._values[i]))
                    
            # Birth
            if str(df.GebJahr._values[i])  != "nan" or \
               str(df.gebDatum._values[i]) != "nan" or \
               str(df.GebOrt._values[i])   != "nan":
                obj["BIRT"] = {}
                if str(df.gebDatum._values[i]) != "nan":
                    obj["BIRT"]["DATE"] = df.gebDatum._values[i]
                elif str(df.GebJahr._values[i]) != "nan":
                    obj["BIRT"]["DATE"] = df.GebJahr._values[i]
                if str(df.GebOrt._values[i]) != "nan":
                    obj["BIRT"]["PLAC"] = df.GebOrt._values[i]
            
            # Christening (= Taufe)
            if str(df.Taufe._values[i]) != "nan":
                obj["CHR"] = {}
                obj["CHR"]["DATE"] = df.Taufe._values[i]
                
            # Marriage - Comments
            if str(df["#Ehe"]._values[i]) != "nan":
                fams = str(df["#Ehe"]._values[i])
                if fams != "---":
                    obj["FAMS"] = fams.split("\n")
                    j = 0
                    while j < len(obj["FAMS"]):
                        if obj["FAMS"][j][0] != 'F':
                            obj["FAMS"][j] = 'F' + obj["FAMS"][j]
                        j = j + 1
                        
            if str(df.Ehepartner._values[i]) != "nan":
                lv_comment = lv_comment + "\nPartner: " + str(df.Ehepartner._values[i])                
                            
            # Death
            if str(df.Tod._values[i]) != "nan" or str(df.SterbeOrt._values[i]) != "nan":
                obj["DEAT"] = {}
                if str(df.Tod._values[i]) != "nan":
                    obj["DEAT"]["DATE"] = df.Tod._values[i]
                if str(df.SterbeOrt._values[i]) != "nan":
                    obj["DEAT"]["PLAC"] = df.SterbeOrt._values[i]
                    
            if str(df.Vater._values[i]) != "nan":
                if str(df.Vater._values[i]) != "nan":
                    obj["comment_father"] = str(df.Vater._values[i])
                
            if str(df.Mutter._values[i]) != "nan":
                if str(df.Mutter._values[i]) != "nan":
                    obj["comment_mother"] = str(df.Mutter._values[i])
            
            # Comment    
            if str(df.Kommentar._values[i]) != "nan":
                lv_comment = lv_comment + "\n" + df.Kommentar._values[i]
            if lv_comment != "":
                obj["comment"] = lv_comment
                
            # No Children
            if str(df["Keine Nachkommen"]._values[i]) != "nan":
                obj["no_children"] = "X"
                
            # Family where I am a child
            if str(df["#Ehe Eltern"]._values[i]) != "nan":
                famc = str(df["#Ehe Eltern"]._values[i])
                if famc != "---":
                    if famc[0] != 'F':
                        obj["FAMC"] = 'F' + famc
                    else:
                        obj["FAMC"] = famc
                
            # Unehelich?
            if str(df["Unehelich"]._values[i]) != "nan":
                obj["unehelich"] = "X"           
                                   
            # :TODO: "Verwandt", "Baum"
            
            # Write Data to File
            f = open(self.configData["currProjectFile"], 'a', encoding='utf8')
            if first:
                first = False
            else:
                f.write(",\n")
            json.dump(obj, f, indent=4, ensure_ascii=False)
            f.close()
            
        print("Ende Verarbeitung Personen, Beginn Speicherung als json-Datei")

        # Close INDI Brackets, open FAM Brackets
        f = open(self.configData["currProjectFile"], 'a', encoding='utf8')
        f.write("\n],\n\"FAM\":\n[\n")
        f.close()
        
        # ===== Out Family List ================================================================= #
        # Create Family List, which includes all children
        first = True
        
        df = pandas.read_excel("C:/Users/D026557/JOB/PROJEKTE/2021_01_Python/Project_002/MyImport/KB_Ehen.xlsx", sheet_name="Ehen Alle", dtype=str)
        
        for i in range(df["Ehe ID"]._values.size):
            if str(df["Ehe ID"]._values[i]) == "nan":
                continue        
            if i % 100 == 0:
                print("Konvertiere " + str(i) + ". Ehe ")    
            
            obj = {}   
            if str(df["Ehe ID"]._values[i])[0] != 'F':         
                obj["id"] = 'F' + str(df["Ehe ID"]._values[i])
            else:
                obj["id"] = str(df["Ehe ID"]._values[i])
            
            # He
            if str(df["ID Er"]._values[i]) != "nan":
                if str(df["ID Er"]._values[i])[0] != 'I':
                    obj["HUSB"] = 'I' + str(df["ID Er"]._values[i])
                else:
                    obj["HUSB"] = str(df["ID Er"]._values[i])
            
            lv_comment = ""
            if str(df["Stand Er"]._values[i]) != "nan":
                lv_comment = str(df["Stand Er"]._values[i])
            if str(df["Vorname Er"]._values[i]) != "nan":
                lv_comment = lv_comment + " " + str(df["Vorname Er"]._values[i])
            if str(df["Familienname"]._values[i]) != "nan":
                lv_comment = lv_comment + " " + str(df["Familienname"]._values[i]) + ";"
            if str(df["Beruf Er"]._values[i]) != "nan":
                lv_comment = lv_comment + " Tätigkeit: " + str(df["Beruf Er"]._values[i]) + ";"
            if str(df["Vater Er"]._values[i]) != "nan":
                lv_comment = lv_comment + " Vater oder Kommentar: " + str(df["Vater Er"]._values[i]) + ";"
            if str(df["Ort Er"]._values[i]) != "nan":
                lv_comment = lv_comment + " stammt aus " + str(df["Ort Er"]._values[i]) + ";"
            if str(df["Geb Er"]._values[i]) != "nan":
                lv_comment = lv_comment + " Alter bei Eheschließung/geboren: " + str(df["Geb Er"]._values[i]) 
            if lv_comment != "":
                obj["comment_father"] = lv_comment
            
            # She
            if str(df["ID Sie"]._values[i]) != "nan":
                if str(df["ID Sie"]._values[i])[0] != 'I':
                    obj["WIFE"] = 'I' + str(df["ID Sie"]._values[i])
                else:
                    obj["WIFE"] = str(df["ID Sie"]._values[i])
            
            lv_comment = ""
            if str(df["Stand Sie"]._values[i]) != "nan":
                lv_comment = str(df["Stand Sie"]._values[i])
            if str(df["Vorname Sie"]._values[i]) != "nan":
                lv_comment = lv_comment + " " + str(df["Vorname Sie"]._values[i])
            if str(df["Nachname Sie"]._values[i]) != "nan":
                lv_comment = lv_comment + " " + str(df["Nachname Sie"]._values[i]) + ";"
            if str(df["Vater/ehem. Mann Sie"]._values[i]) != "nan":
                lv_comment = lv_comment + " Vater/exEhemann oder Kommentar: " + str(df["Vater/ehem. Mann Sie"]._values[i]) + ";"
            if str(df["Ort Sie"]._values[i]) != "nan":
                lv_comment = lv_comment + " stammt aus " + str(df["Ort Sie"]._values[i]) + ";"
            if str(df["Geb Sie"]._values[i]) != "nan":
                lv_comment = lv_comment + " Alter bei Eheschließung/geboren: " + str(df["Geb Sie"]._values[i]) 
            if lv_comment != "":
                obj["comment_mother"] = lv_comment
                                    
            # Marriage
            if str(df["Seite"]._values[i]) != "nan" or \
               str(df["Nummer"]._values[i]) != "nan" or \
               str(df["Jahr"]._values[i]) != "nan" or \
               str(df["Datum"]._values[i]) != "nan" or \
               str(df["Ort der Trauung"]._values[i]) != "nan":
                   
                obj["MARR"] = {}
                
                if str(df["Datum"]._values[i]) != "nan":
                    obj["MARR"]["DATE"] = str(df["Datum"]._values[i])
                elif str(df["Jahr"]._values[i]) != "nan":
                    obj["MARR"]["DATE"] = str(df["Jahr"]._values[i])
                    
                if str(df["Ort der Trauung"]._values[i]) != "nan":
                    obj["MARR"]["PLAC"] = str(df["Ort der Trauung"]._values[i])
                    
                if str(df["Seite"]._values[i]) != "nan" or \
                   str(df["Nummer"]._values[i]) != "nan" or \
                   str(df["Jahr"]._values[i]) != "nan":
                       
                    obj["MARR"]["comment"] = "Ehen KB Lohsa Seite "
                    if str(df.Seite._values[i]) != "nan":
                        obj["MARR"]["comment"] = obj["MARR"]["comment"] + str(df.Seite._values[i])
                    obj["MARR"]["comment"] = obj["MARR"]["comment"] + "/"
                    if str(df.Nummer._values[i]) != "nan":
                        obj["MARR"]["comment"] = obj["MARR"]["comment"] + str(df.Nummer._values[i])
                    obj["MARR"]["comment"] = obj["MARR"]["comment"] + "/"
                    if str(df.Jahr._values[i]) != "nan":
                        obj["MARR"]["comment"] = obj["MARR"]["comment"] + str(int(df.Jahr._values[i]))
                        
            # Children
            if str(df["Geschw1"]._values[i]) != "nan":
                obj["CHIL"] = []
                if str(df["Geschw1"]._values[i])[0] != 'I':
                    obj["CHIL"].append('I' + str(df["Geschw1"]._values[i]))
                else:
                    obj["CHIL"].append(str(df["Geschw1"]._values[i]))
            if str(df["Geschw2"]._values[i]) != "nan":
                if str(df["Geschw2"]._values[i])[0] != 'I':
                    obj["CHIL"].append('I' + str(df["Geschw2"]._values[i]))
                else:
                    obj["CHIL"].append(str(df["Geschw2"]._values[i]))
            if str(df["Geschw3"]._values[i]) != "nan":
                if str(df["Geschw3"]._values[i])[0] != 'I':
                    obj["CHIL"].append('I' + str(df["Geschw3"]._values[i]))
                else:
                    obj["CHIL"].append(str(df["Geschw3"]._values[i]))
            if str(df["Geschw4"]._values[i]) != "nan":
                if str(df["Geschw4"]._values[i])[0] != 'I':
                    obj["CHIL"].append('I' + str(df["Geschw4"]._values[i]))
                else:
                    obj["CHIL"].append(str(df["Geschw4"]._values[i]))
            if str(df["Geschw5"]._values[i]) != "nan":
                if str(df["Geschw5"]._values[i])[0] != 'I':
                    obj["CHIL"].append('I' + str(df["Geschw5"]._values[i]))
                else:
                    obj["CHIL"].append(str(df["Geschw5"]._values[i]))
            if str(df["Geschw6"]._values[i]) != "nan":
                if str(df["Geschw6"]._values[i])[0] != 'I':
                    obj["CHIL"].append('I' + str(df["Geschw6"]._values[i]))
                else:
                    obj["CHIL"].append(str(df["Geschw6"]._values[i]))
            if str(df["Geschw7"]._values[i]) != "nan":
                if str(df["Geschw7"]._values[i])[0] != 'I':
                    obj["CHIL"].append('I' + str(df["Geschw7"]._values[i]))
                else:
                    obj["CHIL"].append(str(df["Geschw7"]._values[i]))
            if str(df["Geschw8"]._values[i]) != "nan":
                if str(df["Geschw8"]._values[i])[0] != 'I':
                    obj["CHIL"].append('I' + str(df["Geschw8"]._values[i]))
                else:
                    obj["CHIL"].append(str(df["Geschw8"]._values[i]))
            if str(df["Geschw9"]._values[i]) != "nan":
                if str(df["Geschw9"]._values[i])[0] != 'I':
                    obj["CHIL"].append('I' + str(df["Geschw9"]._values[i]))
                else:
                    obj["CHIL"].append(str(df["Geschw9"]._values[i]))
            if str(df["Geschw10"]._values[i]) != "nan":
                if str(df["Geschw10"]._values[i])[0] != 'I':
                    obj["CHIL"].append('I' + str(df["Geschw10"]._values[i]))
                else:
                    obj["CHIL"].append(str(df["Geschw10"]._values[i]))
            if str(df["Geschw11"]._values[i]) != "nan":
                if str(df["Geschw11"]._values[i])[0] != 'I':
                    obj["CHIL"].append('I' + str(df["Geschw11"]._values[i]))
                else:
                    obj["CHIL"].append(str(df["Geschw11"]._values[i]))
            if str(df["Geschw12"]._values[i]) != "nan":
                if str(df["Geschw12"]._values[i])[0] != 'I':
                    obj["CHIL"].append('I' + str(df["Geschw12"]._values[i]))
                else:
                    obj["CHIL"].append(str(df["Geschw12"]._values[i]))
                        
            f = open(self.configData["currProjectFile"], 'a', encoding='utf8')
            if first:
                first = False
            else:
                f.write(",\n")
            json.dump(obj, f, indent=4, ensure_ascii=False)
            f.close()
            
        # Close FAM Brackets
        f = open(self.configData["currProjectFile"], 'a', encoding='utf8')
        f.write("\n]\n}")
        f.close()

        print("Konvertierung abgeschlossen")

        return
    def _convertDataFormatGedToJson(self, fname):

        # ----- Read Source File ----- #
        bytes = min(2048, os.path.getsize(fname))
        raw = open(fname, 'rb').read(bytes)
        result = chardet.detect(raw)
        encoding = result['encoding']
       
        f = open(fname, 'r', encoding=encoding)
        lines = f.readlines()
        f.close()
        
        # Start with empty file #
        f = open(self.configData["currProjectFile"], 'w', encoding='utf8')
        f.close()

        cnt = 0
        tab = []
        first = True
        firstPrint = True
        obj = {}
        lastKey0 = ""
        newKey = ""

        for line in lines: # file could be opened
            cnt = cnt + 1
            level = 0
            value = ""
            key   = ""
            
            # get level - key - value
            line = line.strip()
            elements = line.split(" ", 2) # split into level, obj, key
            if len(elements) >= 1:
                level = int(elements[0])
            if len(elements) >= 2:
                if level == 0 and len(elements) >= 3:
                    value = elements[1]
                else:
                    key = elements[1]
            if len(elements) >= 3:
                if level == 0:
                    key = elements[2]
                else:
                    value = elements[2]
            
            # call recursion and write into file
            if level == 0 and not first:
                obj = self._runRecursion(tab)
                for newKey in obj.keys():
                    break
    
                # braces, colons, new lines and indentation - magic ;o)
                f = open(self.configData["currProjectFile"], 'a', encoding='utf8')
                if not firstPrint:
                    if lastKey0 != newKey:
                        f.write("\n    ],\n    \"" + newKey + "\":\n    [\n")
                    else:
                        f.write(",\n")
                else:
                    f.write("{\n    \"" + newKey + "\":\n    [\n")
                    firstPrint = False
                lastKey0 = newKey

                # write data from obj structure into file
                json.dump(obj[newKey], f, indent=4, ensure_ascii=False)
                f.close()
            elif level == 0:
                first = False

            tab.append({"level": level, "key": key, "value": value})

        # Once again after finishing the loop
        obj = self._runRecursion(tab)
        f = open(self.configData["currProjectFile"], 'a', encoding='utf8')
        
        # braces, colons, new lines and indentation - magic ;o)
        for newKey in obj.keys(): break
        if lastKey0 != newKey:
            f.write("\n    ],\n    \"" + newKey + "\":\n    [\n")
        else:
            f.write(",\n")        

        # Write last Entity #
        json.dump(obj[newKey], f, indent=4, ensure_ascii=False)
        
        # Closing Brackets
        f.write("\n]\n}")
        f.close()
    def _convertDataFormatJsonToJson(self,file):
        
        # ----- Figure out codepage of file ----- #
        bytes = min(32, os.path.getsize(file))
        raw = open(file, 'rb').read(bytes)
        result = chardet.detect(raw)
        encoding = result['encoding']
        # TODO: does not work always => dirty:
        if encoding == "ascii": encoding = "utf-8"

        # ----- Read Data ----- #
        with open(file, encoding=encoding) as f:
            jData = json.load(f)
        f.close()
        
        # ----- Write Data to Target ----- #
        f = open(self.configData["currProjectFile"], 'w', \
                 encoding=self.configData["encoding"])
        json.dump(jData, f, indent=4, ensure_ascii=False)        
    def _convertDataFormatCsvToJson(self,file):
        # print("Data.readCsvFile")

        # :TODO: Ist erste Zeile mit Daten oder Spaltenüberschriften?
        # :TODO: Das ist die Reihenfolge der Felder ("Mapping"), die irgendwie anders 
        # pro Datei erzeugt werden muss, z.B. durch Abfrage
        fields        = []
        numFields     = 0
        oldLine       = ""
        familyNum     = 0
        jData         = {}
        jData["INDI"] = []
        jData["FAM"]  = []
        person        = {}
        trans         = {}

        bytes = min(32, os.path.getsize(file))
        raw = open(file, 'rb').read(bytes)
        result = chardet.detect(raw)
        encoding = result['encoding']
        # TODO: does not work always => dirty:
        if encoding == "ascii": encoding = "utf-8"

        f = open(file, 'r', encoding=encoding)
        lineNr = 0
        for line in f:
            # First line describes the fields #
            if lineNr == 0:
                line = line[1:-1].lower()
                fields = line.split('","')
                numFields = len(fields) 
                lineNr = 1
                emptyPerson = {}
                for field in fields:
                    emptyPerson[field] = ""
                continue
                
            lineNr = lineNr + 1
                
            line = oldLine + line.strip()

            temp = line
            if temp[0] == '"':
                temp = temp[1:]
            if temp[-1:] != '"':
                temp = temp + '"'
            temp = temp.replace(',,', ',"",') # not all lines are escaped
            temp = temp.replace(',,', ',"",') # do twice!
            elements = temp.split('","')
            if len(elements) < numFields:
                oldLine = line + "\n"
                continue
            else:
                oldLine = ""

            person = emptyPerson
            trans = {}
            fam = {}

            cnt = -1
            for element in elements:
                cnt = cnt + 1 
                fieldname = fields[cnt]
                person[fieldname] = element
            
            # ----- Person ----- #
            trans["comment"] = ""
            print("ID: " + person.get("id",""))
            if person.get("id","") == "": print( "FEHLER, keine ID")

            if "id" in fields:
                trans["id"] = "@I" + person["id"] + "@"

            if "vorname" in fields or "gebname" in fields or "nachname" in fields:
                if "vorname" in fields:
                    if person["vorname"] != "":
                        trans["NAME"] = {}
                        trans["NAME"]["GIVN"] = person["vorname"]
                if "gebname" in fields:
                    if person["gebname"] != "":
                        if "NAME" not in trans:
                            trans["NAME"] = {}
                        trans["NAME"]["SURN"] = person["gebname"]
                        
                if "nachname" in fields:
                    if person["nachname"] != "":
                        if "NAME" not in trans:
                            trans["NAME"] = {}
                        if "SURN" in trans["NAME"]:
                            trans["NAME"]["SURN"] = trans["NAME"]["SURN"] + " " + person["gebname"]
                        else:
                            trans["NAME"]["SURN"] = person["gebname"]
                                            
            if "geschlecht" in fields:
                if person["geschlecht"] != "":
                    trans["SEX"] = person["geschlecht"]
                
            if "gebdat" in fields or "gebort" in fields:
                if "gebdat" in fields:
                    if person["gebdat"] != "":
                        trans["BIRT"] = {}
                        trans["BIRT"]["DATE"] = person["gebdat"]
                if "gebort" in fields:
                    if person["gebort"] != "":
                        if "BIRT" not in trans:
                            trans["BIRT"] = {}
                        trans["BIRT"]["PLAC"] = person["gebort"]
                    
            if "gebregister" in fields:
                if person["gebregister"] != "0":
                    trans["comment"] = trans["comment"] + "\nGeburtsregister: " + person["gebregister"]
            
            if "sterbedat" in fields or "sterbeort" in fields:
                if "sterbedat" in fields:
                    if person["sterbedat"] != "":
                        trans["DEAT"] = {}
                        trans["DEAT"]["DATE"] = person["sterbedat"]
                if "sterbeort" in fields:
                    if person["sterbeort"] != "":
                        if "DEAT" not in trans:
                            trans["DEAT"] = {}
                        trans["DEAT"]["PLAC"] = person["sterbeort"]
                    
            if "sterberegister" in fields:
                if person["sterberegister"] != "0":
                    trans["comment"] = trans["comment"] + "\nSterberegister: " + person["sterberegister"]
            
            if "ehepartner" in fields:
                if person["ehepartner"] != "":
                    trans["comment"] = trans["comment"] + "\nEhepartner: " + person["ehepartner"]
            
            if "kinder" in fields:
                if person["kinder"] != "":
                    trans["comment"] = trans["comment"] + "\nKinder: " + person["kinder"]
                
            if "quelle" in fields:
                if person["quelle"] != "":
                    trans["comment"] = trans["comment"] + "\nQuelle: " + person["quelle"]
            
            if "kommentar" in fields:
                if person["kommentar"] != "":
                    trans["comment"] = trans["comment"] + "\nKommentar: " + person["kommentar"]
            
            if "url" in fields:
                if person["url"] != "":
                    trans["comment"] = trans["comment"] + "\nURL: " + person["url"]
            
            if "url2" in fields:
                if person["url2"] != "":
                    trans["comment"] = trans["comment"] + "\nURL2: " + person["url2"]
            
            if "url3" in fields:
                if person["url3"] != "":
                    trans["comment"] = trans["comment"] + "\nURL3: " + person["url3"]
            
            if "url4" in fields:
                if person["url4"] != "":
                    trans["comment"] = trans["comment"] + "\nURL4: " + person["url4"]
                        
            if "kinderlos" in fields:
                if person["kinderlos"] != "":
                    trans["comment"] = trans["comment"] + "\nKinderlos: " + person["kinderlos"]

            # ----- Family ----- #
            if "idvater" in fields:
                if person["idvater"] != "":
                    fam["HUSB"] = "@I" + person["idvater"] + "@"
            if "idmutter" in fields:
                if person["idmutter"] != "":
                    fam["WIFE"] = "@I" + person["idmutter"] + "@"

            # Family already there? #
            fam["CHIL"] = []
            found = False
            for family in jData["FAM"]:
                if family.get("HUSB","") == fam.get("HUSB","") and family.get("WIFE","") == fam.get("WIFE",""):
                    family["CHIL"].append(trans["id"])
                    fam["id"] = family["id"]
                    found = True
                    break
            
            if not found:
                familyNum = familyNum + 1
                fam["id"] = "@F" + str(familyNum) + "@"
                fam["CHIL"].append(trans["id"])
                jData["FAM"].append(fam)
                
            trans["FAMC"] = fam["id"]                    
            jData["INDI"].append(trans)
            
        # Set FAMS #
        for fam in jData["FAM"]:
            
            husb = fam.get("HUSB","")
            if husb != "":
                for obj in jData["INDI"]:
                    if obj["id"] == husb:
                        if "FAMS" in obj:
                            obj["FAMS"].append(fam["id"])
                        else:
                            obj["FAMS"] = [fam["id"]]
                        break
                            
            wife = fam.get("WIFE","")
            if wife != "":
                for obj in jData["INDI"]:
                    if obj["id"] == wife:
                        if "FAMS" in obj:
                            obj["FAMS"].append(fam["id"])
                        else:
                            obj["FAMS"] = [fam["id"]]
                        break
            
        f = open(self.configData["currProjectFile"], 'w', encoding='utf8')
        json.dump(jData, f, indent=4, ensure_ascii=False)
        f.close()
    def _runRecursion(self, tab):
        obj = {}

        while True:
            if tab == []:
                return obj
            line = tab[0]
            tab.pop(0) # remove first table entry

            if len(tab) == 0:
                nextLevel = 0
            else:
                nextLevel = tab[0]["level"] # level of next line
            
            if nextLevel <= line["level"]:
                # check, if key: value is not appropriate anymore and we need key: [value1, value2, ...]
                if line["key"] in obj.keys():
                    if type(obj[line["key"]]) is list:
                        obj[line["key"]].append(line["value"])
                    else:
                        obj[line["key"]] = [ obj[line["key"]], line["value"]]
                elif line["key"] in ["FAMS","CHIL"]:         # FAMS - CHIL - ? => []
                    if not line["key"] in obj:
                        obj[line["key"]] = []
                    obj[line["key"]].append(line["value"])
                elif line["key"] == "MARR":
                    if not "MARR" in obj:
                        obj["MARR"] = {}
                elif line["key"] == "NAME":
                    if not "NAME" in obj:
                        obj["NAME"] = {}
                else:
                    obj[line["key"]] = line["value"]

                if nextLevel < line["level"]:
                    break
            else:
                nextObj = self._runRecursion(tab)
                if line["value"] != "":
                    nextObj["id"] = line["value"]
                obj[line["key"]] = nextObj

        return obj

    # -----SAVE + LOG ----- #
    def _addToLog(self, id, field, value, mode):
        f = open(self.logFilename, "a", encoding="utf-8")
        f.write('"' + str(time.time()) + '","' + self.configData["currProject"] + '","INDI","' + \
                str(id) + '","' + str(field) + '","' + str(value) + '","' + mode + '"\n')
        f.close()
    def _addToFamLog(self,id,field,value,mode):
        f = open(self.logFilename, "a", encoding="utf-8")
        f.write('"' + str(time.time()) + '","' + self.configData["currProject"] + '","FAM","' + \
                str(id) + '","' + str(field) + '","' + str(value) + '","' + mode + '"\n')
        f.close()
    def _addToNoteLog(self,id,field,value,mode):
        f = open(self.logFilename, "a", encoding="utf-8")
        f.write('"' + str(time.time()) + '","' + self.configData["currProject"] + '","NOTE","' + \
                str(id) + '","' + str(field) + '","' + str(value) + '","' + mode + '"\n')
        f.close()
    def _removeFromLog(self):
        tmpContent = ""
        first = True
        if exists(self.logFilename):
            f = open(self.logFilename, 'r', encoding="utf-8")
            for line in f:
                fields = line.split('","')
                if len(fields) > 1:
                    if fields[1] == self.configData["currProject"]:
                        continue
                if first:
                    tmpContent = line
                    first = False
                else:
                    tmpContent = "\n" + line
            f.close()
            
        f = open(self.logFilename, 'w', encoding="utf-8")
        f.write(tmpContent)
        f.close()        
    def save(self):
        # Save current data #
        self._saveJData()
        
        # Remove changed data from log file #
        self._removeFromLog()
    def _saveFromLog(self):
        # Called at the beginning, when checking for not considered changes #
        
        # timestamp; INDI or FAM; id; field; value; mode - add (+) or remove (-)
        # TODO: erst temporäre Kopie jData und darauf arbeiten und nur, wenn alles geklappt hat,
        # zurück auf jData kopieren
        # TODO: remove in mode berücksichtigen
        # TODO: wenn ein Wert Teil einer Liste und nicht nur ein Wert ist, dann wird's doof
        
        if exists(self.logFilename):
            f = open(self.logFilename, 'r', encoding="utf-8")
            
            error = False
            for line in f:
                if line == "": continue
                if line[-1] == "\n": line = line[:-1]
                if line == "": continue
                if line[-1] == '"':  line = line[:-1]
                if line == "": continue
                    
                fields = line.split('","')
                if len(fields) >= 7:
                    if fields[1] == self.configData["currProject"]:
                        id   = fields[3]
                        col  = fields[4]
                        val  = fields[5]
                        mode = fields[6] # add (+) or remove (-) => TODO

                        if fields[2] == "INDI":

                            # find person #
                            idx = self.helperPersList.get(id,"")
                            if idx == "" and col == "id":
                                if "INDI" not in self.jData:
                                    self.jData["INDI"] = []
                                idx = len(self.helperPersList)
                                self.jData["INDI"].append({"id": val})
                                self.helperPersList[id] = idx
                                continue
                            
                            # self.jData["INDI"], self.jData["INDI"][idx] = self._saveFromLogLine( \    
                            self.jData["INDI"] = self._saveFromLogLine( \
                                    fields[2], self.jData["INDI"], self.jData["INDI"][idx], \
                                    self.helperPersList, col, val, mode 
                                )
                            
                        elif fields[2] == "FAM":
                            
                            # find family #
                            idx = self.helperFamList.get(id,"")
                            if idx == "" and col == "id":
                                if "FAM" not in self.jData:
                                    self.jData["FAM"] = []
                                idx = len(self.helperFamList)
                                self.jData["FAM"].append({"id": val})
                                self.helperFamList[id] = idx
                                continue

                            # self.jData["FAM"], self.jData["FAM"][idx] = self._saveFromLogLine( \
                            self.jData["FAM"] = self._saveFromLogLine( \
                                    fields[2], self.jData["FAM"], self.jData["FAM"][idx], \
                                    self.helperPersList, col, val, mode 
                                )
                            
                        elif fields[2] == "NOTE":
                            
                            # find note / comment / url #
                            idx = self.helperNoteList.get(id,"")
                            if idx == "" and col == "id":
                                if "NOTE" not in self.jData:
                                    self.jData["NOTE"] = []
                                idx = len(self.helperNoteList)
                                self.jData["NOTE"].append({"id": val})
                                self.helperNoteList[id] = idx
                                continue

                            # self.jData["NOTE"], self.jData["NOTE"][idx] = self._saveFromLogLine( \
                            self.jData["NOTE"] = self._saveFromLogLine( \
                                    fields[2], self.jData["NOTE"], self.jData["NOTE"][idx], \
                                    self.helperNoteList, col, val, mode 
                                )                        
                                                    
            if not error:
                self._removeFromLog()
                self._saveJData()
    def _saveFromLogLine(self, objType, jDataList, jData, idxList, col, val, mode):
        
        # Which column is affected? #
        pos = col.find(">")
        
        if pos == -1:
            if mode == "+":
                # lists; add values if necessary #
                if ( objType == "INDI" and col == "FAMS") or \
                   ( objType == "FAM" and col == "CHIL"):
                    jData[col] = [val]
                else:
                    jData[col] = val

            elif mode == "-":
                # special case whole INDI object #
                if ( objType == "INDI" and col == "INDI") or \
                   ( objType == "FAM" and col == "FAM") or \
                   ( objType == "NOTE" and col == "NOTE"): 
                    jDataList.remove(jData)
                    i = 0
                    idxList = {}
                    for obj in jDataList: 
                        idxList[i] = obj.get("id","")
                        i = i + 1 
                    return jDataList
                        
                # List Object #
                elif isinstance(jData[col], list):
                    if val != "":
                        jData[col].remove(val)
                        
                # Simple Field #
                else:
                    jData.pop(col)
                    
        # 2-Level-field #
        else:
            field1 = col[0:pos]
            field2 = col[pos+1:]
            
            if mode == "+":
                if field1 not in jData:
                    jData[field1] = {}    
                jData[field1][field2] = val
                
            elif mode == "-":
                jData[field1][field2].remove(val)                
            
        return jDataList #, jData
    def _saveJData(self):
        # Save current data #
        filename = self.configData["projectDir"] + "/" + self.configData["currProject"] + ".json"
        f = open(filename, "w", encoding="utf-8")
        json.dump(self.jData, f, indent=4, ensure_ascii=False)
        f.close()
    def _updateFromLog(self,mode):
        
        # TODO: compare old and new data
        found = False
        if exists(self.logFilename):
            f = open(self.logFilename, 'r', encoding="utf-8")
            for line in f:
                fields = line.split('","')
                if len(fields) > 1:
                    if fields[1] == self.configData["currProject"]:
                        found = True
                        break
            f.close()

        # Save current Data #
        if found:
            qm = QMessageBox()
            qm.setWindowTitle("Speichern?")
            qm.setText("Es gibt ungesicherte Änderungen. Änderungen speichern?")
            qm.setStandardButtons(QMessageBox.Yes|QMessageBox.No|QMessageBox.Cancel)
            btnYes    = qm.button(QMessageBox.Yes)
            btnNo     = qm.button(QMessageBox.No)
            btnCancel = qm.button(QMessageBox.Cancel)
            btnYes.setText("Ja")
            btnNo.setText("Nein")
            btnCancel.setText("Abbruch")
            qm.exec_()
            if qm.clickedButton() == btnYes:
                if mode == 1: # Save at exit
                    self.save()
                else:
                    self._saveFromLog()
            elif qm.clickedButton() == btnCancel:
                return False

        return True
        
    # ----- GETTER ----- #
    def getBirthData(self, id):
        # called from Graph.py #
        return self._getEvent(id, "BIRT")
    def getChildren(self, id):
        # called from Graph.py #
        children = []
        ret, pers = self.getPerson(id)
        if ret:
            fams = pers.get("FAMS",[])
            for fam in fams:
                ret, famDic = self.getFamily(fam)
                if ret:
                    list = famDic.get("CHIL",[])
                    for elem in list:
                        children.append(elem)
            return True, children
        return False, []
    def getComment(self, id):
        ret, pers = self.getPerson(id)
        if ret:
            val = pers.get("comment","")
            if val != "":
                return True, val
        return False, ""    
    def getCommentFather(self, id):
        ret, pers = self.getPerson(id)
        if ret:
            if "comment_father" in pers:
                return True, pers["comment_father"]
        return False, ""
    def getCommentMother(self, id):
        ret, pers = self.getPerson(id)
        if ret:
            if "comment_mother" in pers:
                return True, pers["comment_mother"]
        return False, ""
    def getCompletionModel(self,idList,sexNot):
        list = []
        
        for obj in self.jData["INDI"]:
            if obj["id"] in idList: continue
            if "SEX" in obj:
                if obj["SEX"] == sexNot: continue
            
            ret, line = self.getPersSelStr(obj,"")
            if ret: list.append(line)
        
        #return QStringListModel(list)
        return list
    def getDeathData(self, id):
        # called from Graph.py #
        return self._getEvent(id, "DEAT")
    def _getEvent(self, id, evtStr):
        # called from Graph.py #
        obj = {}
        ret, pers = self.getPerson(id)
        if ret:
            event = pers.get(evtStr)
            if event != None and type(event) is dict:
                obj["date"]  = event.get("DATE","")
                obj["place"] = event.get("PLAC","")
                return True, obj
        return False, {}
    def getFamily(self,fId):
        # called from PersonWidget.py #
        if fId in self.helperFamList:
            return True, self.jData["FAM"][self.helperFamList[fId]]
        return False, {}
    def getFamilies(self,pId):
        ret, pers = self.getPerson(pId)
        if not ret: return ""
        return pers.get("FAMS",[])
    def getFamilyForPair(self, pId1, pId2):
        # called from Graph.py #
        ret, pers1 = self.getPerson(pId1)
        if not ret: return ""
        ret, pers2 = self.getPerson(pId2)
        if not ret: return ""
        
        fams1 = pers1.get("FAMS",[])
        fams2 = pers2.get("FAMS",[])
        for fam in fams1:
            if fam in fams2:
                return fam
        return ""
    def getFatherId(self, id):
        ret, pers = self.getPerson(id)
        if ret:
            if "FAMC" in pers:
                ret, fam = self.getFamily(pers["FAMC"])
                if ret:
                    idF = fam.get("HUSB","")
                    if idF != "":
                        return True, idF
        return False, ""
    def getMarriageDate(self, id, idx):
        ret, pers = self.getPerson(id)
        if ret:
            fams = pers.get("FAMS",[])
            if len(fams) > idx:
                fam = fams[idx]
                ret, famObj = self.getFamily(fam)
                if ret:
                    marr = famObj.get("MARR")
                    if marr != None:
                        return marr.get("DATE","")
        return ""
    def getMarriageForFam(self, fId):
        # called from Graph.py #
        obj = {}
        ret, fam = self.getFamily(fId)
        if ret:
            if "MARR" in fam:
                obj["date"]  = fam["MARR"].get("DATE","")
                obj["place"] = fam["MARR"].get("PLAC","")
                return True, obj
        return False, {}
    def getMarriagePlace(self, id, idx):
        ret, pers = self.getPerson(id)
        if ret:
            fams = pers.get("FAMS",[])
            if len(fams) > idx:
                fam = fams[idx]
                ret, famObj = self.getFamily(fam)
                if ret:
                    marr = famObj.get("MARR")
                    if marr != None:
                        return marr.get("PLAC","")
        return ""
    def getMedia(self, id):
        ret, pers = self.getPerson(id)
        if ret:
            val = pers.get("media","")
            if val != "":
                return True, val
        return False, ""    
    def getMotherId(self, id):
        ret, pers = self.getPerson(id)
        if ret:
            if "FAMC" in pers:
                ret, fam = self.getFamily(pers["FAMC"])
                if ret:
                    idM = fam.get("WIFE","")
                    if idM != "":
                        return True, idM
        return False, ""
    def getName(self, id):
        # called from Graph.py #
        name = {}
        ret, pers = self.getPerson(id)
        if ret:
            if "NAME" in pers:
                name["firstname"] = pers["NAME"].get("GIVN","")
                name["surname"]   = pers["NAME"].get("SURN","")
                return True, name
        return False, {}
    def getNextFamId(self):
        cnt = 0
        
        while True:
            cnt = cnt + 1
            id = "@F" + str(cnt) + "@"
            if id not in self.helperFamList:
                break

        return id
    def _getNextNoteId(self):
        cnt = 0
        
        while True:
            cnt = cnt + 1
            id = "@N" + str(cnt) + "@"
            if id not in self.helperNoteList:
                break

        return id
    def getNextPersonId(self):
        cnt = 0
        
        while True:
            cnt = cnt + 1
            id = "@I" + str(cnt) + "@"
            if id not in self.helperPersList:
                break

        return id
    def _getNoteObj(self, id):
        if id in self.helperNoteList:
            return True, self.jData["NOTE"][self.helperNoteList[id]]
        return False, {}    
    def getOwnFamily(self, id):
        objects = []
        ret, pers = self.getPerson(id)
        if ret:
            fams = pers.get("FAMS",[])
            for fam in fams:
                obj = {}
                ret, famDetails = self.getFamily(fam)
                if not ret: continue
                
                # ID #
                obj["id"] = fam
                
                # Marriage date and place #
                marr = famDetails.get("MARR")
                if marr != None:
                    obj["date"]  = marr.get("DATE","")
                    obj["place"] = marr.get("PLAC","")
                    
                # Partner #
                husb = famDetails.get("HUSB","")
                wife = famDetails.get("WIFE","")
                if husb == id and wife != "":
                    obj["partnerID"] = wife
                elif wife == id and husb != "":
                    obj["partnerID"] = husb
                    
                # Children #
                chil = famDetails.get("CHIL")
                if chil != None:
                    obj["childrenID"] = chil
                    
                # Comments #
                comm = famDetails.get("comment","")
                commHe = famDetails.get("comment_father","")
                commShe = famDetails.get("comment_mother","")
                if commHe != "":
                    if comm != "":
                        comm += "\nEr: " + commHe
                    else:
                        comm = "Er: " + commHe
                if commShe != "":
                    if comm != "":
                        comm += "\nSie: " + commShe
                    else:
                        comm = "Sie: " + commShe
                if comm != "":
                    obj["comment"] = comm
                    
                objects.append(obj)
        return objects
    def getParentsDict(self, id):
        # called from PersonWidget + Graph.py #
        obj = {}
        ret, pers = self.getPerson(id)
        if ret:
            obj["comment_father"] = pers.get("comment_father","")
            obj["comment_mother"] = pers.get("comment_mother","")
            if "FAMC" in pers:
                ret, fam = self.getFamily(pers["FAMC"])
                if ret:
                    obj["fatherId"] = fam.get("HUSB","")
                    obj["motherId"] = fam.get("WIFE","")
                    if obj["comment_father"] == "" and obj["fatherId"] != "":
                        ret, nameDic = self.getName(obj["fatherId"])
                        if ret:
                            obj["comment_father"] = nameDic["firstname"] + " " + nameDic["surname"]
                    if obj["comment_mother"] == "" and obj["motherId"] != "":
                        ret, nameDic = self.getName(obj["motherId"])
                        if ret:
                            obj["comment_mother"] = nameDic["firstname"] + " " + nameDic["surname"]
                    return True, obj
        return False, {}    
    def getParentsIDs(self, id):
        # called from Graph.py #
        ret, pers = self.getPerson(id)
        if ret:
            if "FAMC" in pers:
                ret, fam = self.getFamily(pers["FAMC"])
                if ret:
                    return fam.get("HUSB",""), fam.get("WIFE","")
        return "", ""
    def getPartners(self, id):
        # called from Graph.py #
        partners = []
        ret, pers = self.getPerson(id)
        if ret:
            fams = pers.get("FAMS",[])
            for fam in fams:
                ret, famDic = self.getFamily(fam)
                if ret:
                    if id == famDic.get("HUSB"):
                        part = famDic.get("WIFE")
                        if part != None:
                            partners.append(part)
                    elif id == famDic.get("WIFE"):
                        part = famDic.get("HUSB")
                        if part != None:
                            partners.append(part)                            
            if len(partners) > 0:
                return True, partners
        return False, []
    def getPerson(self,id):
        # called from PersonWidget.py #
        if id in self.helperPersList:
            return True, self.jData["INDI"][self.helperPersList[id]]
        return False, {}
    def getPersonForTable(self,id):
        if self.helperPersList.get(id) == None:
            return
            
        # List of key fields, which is used for the table #
        fields = self.configData["personListFields"].keys()

        for obj in self.jData["INDI"]:
            if obj["id"] == id:
                pers = obj
                break
        
        line = []
        
        for key in fields:
            
            if key in pers:
                line.append(pers[key])
                
            elif key.find(">") > 0:
                pos = key.find(">")
                pre = key[0:pos]
                post = key[pos+1:]
                if pre in pers:
                    if post in pers[pre]:
                        line.append(pers[pre][post])
                    else:
                        line.append("")
                else:
                    line.append("")
                    
            else:
                line.append("")
        
        return line
    def getPersonIdx(self,id):
        # called from PersonWidget.py #
        if id in self.helperPersList:
            return True, self.helperPersList[id]
        return False, {}
    def getPersSelStr(self,obj,id):
        # Parameter: filled either obj or id #
        if obj == None and id != "":
            if "INDI" not in self.jData: return False, ""
            ret, obj = self.getPerson(id)
            if not ret: return False, ""
        elif obj == None:
            return False, ""
        
        line = obj["id"] + " " + self.getPersStr(obj["id"]) 
        return True, line
    def getPersStr(self,id):
        ret, obj = self.getPerson(id)
        if not ret: return ""
        
        line = ""
        
        # Parameter: filled either obj or id #
        if "NAME" in obj:
            line = "<b>"
            if "GIVN" in obj["NAME"]:
                line = line + obj["NAME"]["GIVN"] + " "
            if "SURN" in obj["NAME"]:
                line = line + obj["NAME"]["SURN"] + " "
            line += "</b>"
        if "BIRT" in obj:
            line = line + "/ geb. "
            if "DATE" in obj["BIRT"]:
                line = line + obj["BIRT"]["DATE"] + " "
            if "PLAC" in obj["BIRT"]:
                line = line + " in " + obj["BIRT"]["PLAC"] + " "
        if "DEAT" in obj:
            line = line + "/ gest. "
            if "DATE" in obj["DEAT"]:
                line = line + obj["DEAT"]["DATE"] + " "
            if "PLAC" in obj["DEAT"]:
                line = line + "in " + obj["DEAT"]["PLAC"] + " "
                
        return line
    def getRelationComment(self, id, idx):
        ret, pers = self.getPerson(id)
        if ret:
            fams = pers.get("FAMS",[])
            if len(fams) > idx:
                famID = fams[idx]
                ret, fam = self.getFamily(famID)
                if ret:
                    return fam.get("comment","")
        return ()
    def getSex(self, id):
        # called from Graph.py #
        ret, pers = self.getPerson(id)
        if ret:
            sex = pers.get("SEX","").lower()
            if sex != "":
                return True, sex
        return False, ""
    def getUrl(self, id):
        ret, pers = self.getPerson(id)
        if ret:
            val = pers.get("url","")
            if val != "":
                return True, val
        return False, ""    
    def getSource(self, id):
        ret, pers = self.getPerson(id)
        if ret:
            val = pers.get("source","")
            if val != "":
                return True, val
        return False, ""    
           
    # ----- Setter ----- #
    def setBirthDate(self,id,value):
        idx = self.helperPersList.get(id,"")
        if idx == "": return
        
        # Logging #
        self._addToLog(id, "BIRT>DATE", value, "+")
        
        # json Data #
        if not "BIRT" in self.jData["INDI"][idx]:
            self.jData["INDI"][idx]["BIRT"] = {}
        self.jData["INDI"][idx]["BIRT"]["DATE"] = value
    def setBirthPlace(self,id,value):
        idx = self.helperPersList.get(id,"")
        if idx == "": return
        
        # Logging #
        self._addToLog(id, "BIRT>PLAC", value, "+")
        
        # json Data #
        if not "BIRT" in self.jData["INDI"][idx]:
            self.jData["INDI"][idx]["BIRT"] = {}
        self.jData["INDI"][idx]["BIRT"]["PLAC"] = value
    def setComment(self, id, value):
        idx = self.helperPersList.get(id,"")
        if idx == "": return
        
        # Logging #
        self._addToLog(id, "comment", value, "+")
        
        # json Data #
        self.jData["INDI"][idx]["comment"] = value               
    def setCommentFather(self, id, value):
        idx = self.helperPersList.get(id,"")
        if idx == "": return
        
        # Logging #
        self._addToLog(id, "comment_father", value, "+")
        
        # json Data #
        self.jData["INDI"][idx]["comment_father"] = value        
    def setCommentMother(self, id, value):
        idx = self.helperPersList.get(id,"")
        if idx == "": return
        
        # Logging #
        self._addToLog(id, "comment_mother", value, "+")
        
        # json Data #
        self.jData["INDI"][idx]["comment_mother"] = value        
    def setDeathDate(self,id,value):
        idx = self.helperPersList.get(id,"")
        if idx == "": return
        
        # Logging #
        self._addToLog(id, "DEAT>DATE", value, "+")
        
        # json Data #
        if not "DEAT" in self.jData["INDI"][idx]:
            self.jData["INDI"][idx]["DEAT"] = {}
        self.jData["INDI"][idx]["DEAT"]["DATE"] = value
    def setDeathPlace(self,id,value):
        idx = self.helperPersList.get(id,"")
        if idx == "": return
        
        # Logging #
        self._addToLog(id, "DEAT>PLAC", value, "+")
        
        # json Data #
        if not "DEAT" in self.jData["INDI"][idx]:
            self.jData["INDI"][idx]["DEAT"] = {}
        self.jData["INDI"][idx]["DEAT"]["PLAC"] = value
    def setFamilyHusband(self, famID, fatherID):
        ret, famObj = self.getFamily(famID)
        if not ret: 
            print("Familie " + str(famID) + " existiert nicht")
            return
        
        ret, fatherObj = self.getPerson(fatherID)
        if not ret: 
            print("Vater " + str(fatherID) + " existiert nicht")
            return
                
        husb = famObj.get("HUSB","")
        if husb != fatherID:
            famObj["HUSB"] = fatherID
            self._addToFamLog(famID, "HUSB", fatherID, "+")       

        if not "FAMS" in fatherObj:
            fatherObj["FAMS"] = []
            
        if famID not in fatherObj["FAMS"]:
            fatherObj["FAMS"].append(famID)
            self._addToLog(fatherID, "FAMS", famID, "+")        
    def setFamilyWife(self, famID, motherID):
        ret, famObj = self.getFamily(famID)
        if not ret: 
            print("Familie " + str(famID) + " existiert nicht")
            return
        
        ret, motherObj = self.getPerson(motherID)
        if not ret: 
            print("Mutter " + str(motherID) + " existiert nicht")
            return
                
        wife = famObj.get("WIFE","")
        if wife != motherID:
            famObj["WIFE"] = motherID
            self._addToFamLog(famID, "WIFE", motherID, "+")       

        if not "FAMS" in motherObj:
            motherObj["FAMS"] = []
            
        if famID not in motherObj["FAMS"]:
            motherObj["FAMS"].append(famID)
            self._addToLog(motherID, "FAMS", famID, "+")        
    def setFamilyChild(self, famID, childID):
        # Adds entries: INDI > FAMC and FAMS > CHILD #
        ret, famObj = self.getFamily(famID)
        if not ret: 
            print("Familie " + str(famID) + " existiert nicht")
            return
        
        ret, childObj = self.getPerson(childID)
        if not ret: 
            print("Kind " + str(childID) + " existiert nicht")
            return

        if not "CHIL" in famObj:
            famObj["CHIL"] = []
            
        if childID not in famObj["CHIL"]:
            famObj["CHIL"].append(childID)
            self._addToFamLog(famID, "CHIL", childID, "+")       

        childObj["FAMC"] = famID
        self._addToLog(childID, "FAMC", famID, "+")        
    def setFirstname(self, id, value):
        idx = self.helperPersList.get(id,"")
        if idx == "": return
        
        # Logging #
        self._addToLog(id, "NAME>GIVN", value, "+")
        
        # json Data #
        if not "NAME" in self.jData["INDI"][idx]:
            self.jData["INDI"][idx]["NAME"] = {}
        self.jData["INDI"][idx]["NAME"]["GIVN"] = value
    def setMarriageDate(self, id, idx, text):
        ret, pers = self.getPerson(id)
        if ret:
            fams = pers.get("FAMS",[])
            if len(fams) > idx or idx == 0:
                if len(fams) == 0 and idx == 0:
                    famID = self.addFamily()
                    if pers.get("SEX") == None:
                        self.setFamilyHusband(famID,id) # Default is male
                    elif pers.get("SEX") == 'f':
                        self.setFamilyWife(famID,id)
                    else:
                        self.setFamilyHusband(famID,id)
                else:
                    famID = fams[idx]
    
                ret, fam = self.getFamily(famID)
                if ret:
                    if fam.get("MARR") == None:
                        fam["MARR"] = {}
                    fam["MARR"]["DATE"] = text
                    self._addToFamLog(famID,"MARR>DATE",text,"+")
    def setMarriagePlace(self, id, idx, text):
        ret, pers = self.getPerson(id)
        if ret:
            fams = pers.get("FAMS",[])
            if len(fams) > idx or idx == 0:
                if len(fams) == 0 and idx == 0:
                    famID = self.addFamily()
                    if pers.get("SEX") == None:
                        self.setFamilyHusband(famID,id) # Default is male
                    elif pers.get("SEX") == 'f':
                        self.setFamilyWife(famID,id)
                    else:
                        self.setFamilyHusband(famID,id)
                else:
                    famID = fams[idx]
                ret, fam = self.getFamily(famID)
                if ret:
                    if fam.get("MARR") == None:
                        fam["MARR"] = {}
                    fam["MARR"]["PLAC"] = text
                    self._addToFamLog(famID,"MARR>PLAC",text,"+")
    def setMedia(self, id, value):
        idx = self.helperPersList.get(id,"")
        if idx == "": return
        
        # Logging #
        self._addToLog(id, "media", value, "+")
        
        # json Data #
        self.jData["INDI"][idx]["media"] = value               
    def setNote(self, persId, noteType, value):
        ret, obj = self.getPerson(persId)
        if not ret: return

        if "NOTE" not in self.jData:
            self.jData["NOTE"] = []
        
        # get NoteId #
        noteId = obj.get(noteType,"")
        if noteId == "":
            noteId = self._getNextNoteId()
            obj[noteType] = noteId
            
        # Set Value #        
        ret, noteObj = self._getNoteObj(noteId)
        if ret:
            noteObj[noteType] = value
        else: 
            self.jData["NOTE"].append({"id":noteId, noteType:value})
            self.helperNoteList[noteId] = len(self.helperNoteList)
        
        # Logging #
        self._addToLog(persId, noteType, noteId, "+") 
        self._addToNoteLog(noteId, noteType, value, "+")
    def setSex(self, id, value):
        idx = self.helperPersList.get(id,"")
        if idx == "": return;
        
        # Logging #
        self._addToLog(id, "SEX", value, "+")
        
        # json Data #
        self.jData["INDI"][idx]["SEX"] = value
    def setSurname(self, id, value):
        idx = self.helperPersList.get(id,"")
        if idx == "": return
        
        # Logging #
        self._addToLog(id, "NAME>SURN", value, "+")
        
        # json Data #
        if not "NAME" in self.jData["INDI"][idx]:
            self.jData["INDI"][idx]["NAME"] = {}
        self.jData["INDI"][idx]["NAME"]["SURN"] = value
    def setUrl(self, id, value):
        idx = self.helperPersList.get(id,"")
        if idx == "": return
        
        # Logging #
        self._addToLog(id, "url", value, "+")
        
        # json Data #
        self.jData["INDI"][idx]["url"] = value               
    def setRelationComment(self, id, idx, text):
        ret, pers = self.getPerson(id)
        if ret:
            fams = pers.get("FAMS",[])
            if len(fams) > idx:
                famID = fams[idx]
                ret, fam = self.getFamily(famID)
                if ret:
                    fam["comment"] = text
                    self._addToFamLog(famID,"comment",text,"+")
    def setSource(self, id, value):
        idx = self.helperPersList.get(id,"")
        if idx == "": return
        
        # Logging #
        self._addToLog(id, "source", value, "+")
        
        # json Data #
        self.jData["INDI"][idx]["source"] = value               
                
    # ----- Others ----- #
    def addFamily(self):
        famID = self.getNextFamId()

        # Logging #
        self._addToFamLog(famID, "id", famID, "+")
        
        if self.jData.get("FAM") == None:
            self.jData["FAM"] = []
            
        # fill data and helper #
        self.jData["FAM"].append({"id": famID})
        self.helperFamList[famID] = len(self.jData["FAM"]) - 1 
        
        return famID
    def addPerson(self):
        # Called from MainWidget.py #

        id = self.getNextPersonId()  

        # Logging #
        self._addToLog(id,"id",id,"+")
        
        if len(self.jData.get("INDI",[])) == 0:
            self.jData["INDI"] = []
            
        # fill data and helper #
        self.jData["INDI"].append({"id":id})
        self.helperPersList[id] = len(self.jData["INDI"]) - 1 

        return id
    def assignParent(self, childID, parentID, who):
        # Called from PersonWidget.py #
        # who = "WIFE" for mother and "HUSB" for father
            
        # CHECKS: does child exist? #
        ret, childObj = self.getPerson(childID)
        if not ret: return 
        
        # Remove Parent #
        if parentID == "":
            self.unassignParent(self, childID, who)
            return
            
        # CHECKS: does parent exist?  #
        ret, parentObj = self.getPerson(parentID)
        if not ret: return 

        famID = ""
        otherParent = ""
        if "FAMC" in childObj:
            # Get other Partner and remember #
            if who == "HUSB":
                ret, otherParent = self.getMotherId(childID)
            else:
                ret, otherParent = self.getFatherId(childID)
                
            self.removeChildFromFamily(childID)
            
            if otherParent != "":
                famID = self.getFamilyForPair(parentID, otherParent)
            
        if famID == "":
            # is there a family with this parent and no partner?
            found = False
            if "FAMS" in parentObj:
                for famID in parentObj["FAMS"]:
                    ret, famObj = self.getFamily(famID)
                    if ret:
                        partnerWho = "HUSB" if who == "WIFE" else "WIFE"
                        if famObj.get(partnerWho,"") == "":
                            found = True
                            break
            if not found:
                # Add new family #
                famID = self.addFamily()

        # Finally, write entries! #
        if who == "HUSB": 
            self.setFamilyWife(famID, otherParent)       
            self.setFamilyHusband(famID, parentID)
        else:             
            self.setFamilyWife(famID, parentID)       
            self.setFamilyHusband(famID, otherParent)
        self.setFamilyChild(famID, childID)
    def assignParents(self, childID, motherID, fatherID):
        # CHECKS: Do all person objects exist? #
        ret = self.getPerson(childID)
        if not ret: 
            print("Kind " + str(childID) + " existiert nicht")
            return False
        ret = self.getPerson(motherID)
        if not ret: 
            print("Mutter " + str(motherID) + " existiert nicht")
            return False
        ret = self.getPerson(fatherID)
        if not ret: 
            print("Vater " + str(fatherID) + " existiert nicht")
            return False
        
        # Need to unassign the child from another family? #
        self.removeChildFromFamily(childID)
        
        # is there a family with father and mother already? #
        famID = self.getFamilyForPair(motherID, fatherID)
        
        # Create a new family if necessary #
        if famID == "":
            famID = self.addFamily()
            
        # TODO: wenn Mutter und Vater vertauscht sind, soll das ok sein, selbst nach Geschlecht schauen!
        # Add mother (WIFE), father (HUSB), child (CHIL) to family #
        # Add family to mother, father (INDI > FAMS) and child (INDI > FAMC) #
        self.setFamilyHusband(famID, fatherID)
        self.setFamilyWife(famID, motherID)
        self.setFamilyChild(famID, childID)
        
        return True
    def _deleteFamilyIfPossible(self, famID):                                         
        ret, famObj = self.getFamily(famID)
        if not ret: return
        
        # Delete whole family, if only WIFE and/or HUSB entries
        pCnt = 0
        # Do mother and father exist? #
        fatherID = famObj.get("HUSB","")
        if fatherID != "":
            pCnt = pCnt + 1
        motherID = famObj.get("WIFE","")
        if motherID != "":
            pCnt = pCnt + 1
        pCnt = pCnt + 1 # for "id" of familiy
        
        if len(famObj) == pCnt:
            self._removeFamily(famID)
    def _fillHelperLists(self):
        self.helperPersList = {}
        self.helperNoteList = {}
        
        cnt = 0        
        if "INDI" in self.jData:
            for obj in self.jData["INDI"]:
                self.helperPersList[obj.get("id")] = cnt
                cnt = cnt + 1

        self.fillHelperFamList()

        cnt = 0        
        if "NOTE" in self.jData:
            for obj in self.jData["NOTE"]:
                self.helperNoteList[obj.get("id")] = cnt
                cnt = cnt + 1
    def fillHelperFamList(self):
        self.helperFamList  = {}

        cnt = 0        
        if "FAM" in self.jData:
            for obj in self.jData["FAM"]:
                self.helperFamList[obj.get("id")] = cnt
                cnt = cnt + 1        
    def onExit(self):
        # Called from main.py #
        return self._updateFromLog(1)
    def removeChildFromFamily(self, childID):
        ret, childObj = self.getPerson(childID)
        if not ret: return
        
        famID = childObj.get("FAMC")
        if famID == None: return
        
        ret, famObj = self.getFamily(famID)
        if not ret: return
        
        children = famObj.get("CHIL")
        if children != None:
            if childID in children:
                children.remove(childID)
                self._addToFamLog(famID, "CHIL", childID, "-")
                
            if len(children) == 0:
                famObj.pop("CHIL","")
                self._addToFamLog(famID, "CHIL", "", "-")
                
        self._deleteFamilyIfPossible(famID)
    def _removeFamily(self, fam):
        idx = self.helperFamList.get(fam,-1)
        if idx < 0: return
        
        famObj = self.jData["FAM"][idx]
        idMother = famObj.get("WIFE","")
        idFather = famObj.get("HUSB","")
        children = famObj.get("CHIL",[])
        
        # remove fam from jData["FAM"]
        del self.jData["FAM"][idx]
        self._addToFamLog(fam, "FAM", "", "-")
        self.fillHelperFamList()
        
        # remove "FAMS" from jDATA["INDI"] for both parents
        ret, pers = self.getPerson(idMother)
        if ret:
            famIDs = pers.get("FAMS")
            if famIDs != None:
                for obj in famIDs:
                    if fam in famIDs:
                        famIDs.remove(fam)
                        self._addToLog(idMother, "FAMS", fam, "-")
                        
        ret, pers = self.getPerson(idFather)
        if ret:
            famIDs = pers.get("FAMS")
            if famIDs != None:
                for obj in famIDs:
                    if fam in famIDs:
                        famIDs.remove(fam)
                        self._addToLog(idFather, "FAMS", fam, "-")
        
        # remove "FAMC" from jDATA["INDI"] 
        for idChild in children:
            ret, pers = self.getPerson(idChild)
            if ret:
                famChild = pers.get("FAMC")
                if famChild != None:
                    pers.pop("FAMC")
                    self._addToLog(idChild, "FAMC", "", "-")
    def _selectPersonList(self):
        # Source must be filled already: self.jData #
        if "INDI" not in self.jData:
            return []
        
        # Initialize
        tabData = []
        
        # List of key fields, which is used for the table #
        fields = self.configData["personListFields"].keys()
        
        for pers in self.jData["INDI"]:
            line = []
            
            for key in fields:
                
                if key in pers:
                    line.append(pers[key])
                    
                elif key.find(">") > 0:
                    pos = key.find(">")
                    pre = key[0:pos]
                    post = key[pos+1:]
                    if pre in pers:
                        if post in pers[pre]:
                            line.append(pers[pre][post])
                        else:
                            line.append("")
                    else:
                        line.append("")
                        
                else:
                    line.append("")
                    
            tabData.append(line)
            
        return tabData
    def unassignParent(self, childID, who):
        fatherID, motherID = self.getParentsIDs(childID)
        self.removeChildFromFamily(childID)
                
        # Assign person to the other part of parents
        if fatherID != "" and motherID != "":
            if who == "HUSB":
                self.assignParent(childID, motherID, "WIFE")
            elif who == "WIFE":
                self.assignParent(childID, fatherID, "HUSB")
                
        return True
    def updatePersValue(self,objectType,id,field,value):
        # Called from PersonListWidget.py #
        
        # Logging #
        self._addToLog(id, field, value, "+")
        
        # Update in internal json Structure #
        if objectType in self.jData:
            ret, idx = self.getPersonIdx(id)
            if ret:
                pos = field.find(">")
                if pos == -1:
                    self.jData["INDI"][idx][field] == value
                else:
                    field1 = field[0:pos]
                    field2 = field[pos+1:]
                    if field1 not in self.jData["INDI"][idx]:
                        self.jData["INDI"][idx][field1] = {}
                    self.jData["INDI"][idx][field1][field2] = value
    def removeFamilyPartner(self, fid, id): # id is the remaining partner
        ret, famObj = self.getFamily(fid)
        if not ret: return

        pers = famObj.get("HUSB","")
        if pers != id:
            famObj.pop("HUSB")
            self._addToFamLog(fid, "HUSB", pers, "-") 
            
        pers = famObj.get("WIFE","")
        if pers != id:
            famObj.pop("WIFE")
            self._addToFamLog(fid, "WIFE", pers, "-") 
        
        self._deleteFamilyIfPossible(fid)
    def createTreeAncestors(self, id): # Vorfahren
        idList = {id: {"idFather": 0, "idMother": 0, "x": 0, "y": 0}}
        lineList = []
        cnt = 0
        minYear = 9999
        maxYear = -9999

        # Get all involved people
        while True:
            obj = idList[cnt]
            pid = obj["id"]
            idFather, idMother = self.getParentsIDs(pid)
            if idFather != "":
                obj["idFather"] = idFather
                idList[idFather] = {"idFather": 0, "idMother": 0, "idChild": pid, "x": 0, "y": 0}
                lineList.append([pid,idFather])
            if idMother != "":
                obj["idMother"] = idMother
                idList[idMother] = {"idFather": 0, "idMother": 0, "idChild": pid, "x": 0, "y": 0}
                lineList.append([pid,idMother])

            cnt = cnt + 1
            if cnt >= len(idList):
                break

        # Add birth year
        for pid in idList:
            year = ""
            ret, birth = self.getBirthData(pid)
            if ret:
                year = birth.get("date","")

            if year != "":
                try:
                    birth = parse(year, fuzzy=False)
                    year = birth.year
                except ValueError:
                    year = ""

            # Find "Line" with pid as second value => assume, mother/father is 20 years older than child
            if year == "":
                found = False
                for line in lineList:
                    if line[1] == pid:
                        childId = line[0]
                        for pers in idList:
                            if pers["id"] == childId:
                                year = pers["year"] - 20
                                found = True
                                break
                    if found: break
                        
            obj["year"] = year
            if minYear > year: minYear = year
            if maxYear < year: maxYear = year
            print(pid + " " + str(year) + " - " + self.getPersStr(pid))

        print("Jahre: " + str(minYear) + " - " + str(maxYear))
        maxYear += 40 # Damit die jüngste Person aufs "Papier" passt
        return idList, lineList, minYear, maxYear