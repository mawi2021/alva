# Sources:
#   https://bodo-schoenfeld.de/excel-daten-mit-python-einlesen/
#   https://www.tutorialspoint.com/pyqt5/pyqt5_qdialog_class.htm
#   https://www.pythonguis.com/tutorials/pyqt-dialogs/
#   https://realpython.com/python-modulo-operator/
#   https://www.tutorialspoint.com/pyqt/pyqt_qinputdialog_widget.htm
#   https://www.codegrepper.com/code-examples/python/get+list+of+all+files+in+a+directory+python
#   https://bodo-schoenfeld.de/excel-daten-mit-python-einlesen/

import sys, os, chardet
from PyQt5.QtWidgets import QInputDialog, QFileDialog, QDialog, QPushButton, QLabel, \
    QVBoxLayout, QDialogButtonBox, QHBoxLayout, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui
from classes.DB import DB
from PyQt5.QtSql import QSqlQuery
import json
#import xlrd
import pandas
import numpy

class Data():

    def __init__(self, main):
        super(Data, self).__init__()
        self.projName    = "" # only the pure project title
        self.projectName = "" # full file name with database content
        self.main        = main
        self.db          = DB()
        self.dirName     = "data"
        self.fields      = ["id", "surname", "firstname", "birth_date", "family", "birth_place", \
                            "death_date", "death_place", "sex", "comment_father"]
        self.fieldNames  = ["ID","Nachname","Vorname", "Geb.Datum", "Geb.Ort", \
                            "Tod Datum", "Tod Ort", "Geschlecht"]
        
        # ----- Constants ----- #
        self.famPrefix = "My" # for numbers of families in conversion


    # ------------------------------------------------------------------------------------------- #
    # ----- n e w   P r o j e c t --------------------------------------------------------------- #
    # ------------------------------------------------------------------------------------------- #
    def newProject(self):
        print("Data.newProject")

        if os.path.isdir(self.dirName) == False:
            # TODO: Verzeichnis Anlegen
            print("Daten-Verzeichnis existiert nicht >> Abbruch")
            return

        self.projName, ok = QInputDialog.getText(self.main, \
                                            'Projektname', \
                                            'Bitte geben Sie einen neuen Projektnamen an:' \
                                            )

        while True:
            if not ok:
                return

            print("  Projektname: ", self.projName)
            fileName = self.dirName + "/" + self.projName + ".db"

            if os.path.isfile(fileName): 
                txt = "Das Projekt " + self.projName + \
                      " existiert bereits. Bitte wählen Sie einen anderen Namen"
                self.projName, ok = QInputDialog.getText(self.main, \
                                                'Projektname', \
                                                txt \
                                            )
            elif self.projName == "":
                self.projName, ok = QInputDialog.getText(self.main, \
                                                'Projektname', \
                                                'Bitte geben Sie einen Projektnamen an:' \
                                            )
            else:
                break

        self.clearWidgets()
        self.projectName = fileName
        self.main.setWindowTitle("Alva - " + self.projName)  

        # ----- DB anlegen ------------------------------------------- *
        self.db.createConnection(self.projectName)
        self.db.createDatabaseAndTables()

    def openProject(self):
        print("Data.openProject")

        items = []

        # Search for files in "data" subdirectory
        files = os.listdir(self.dirName)
        for file in files:
            if file.endswith(".db"):
                items.append(file.removesuffix(".db"))

        item, ok = QInputDialog.getItem(self.main, "Auswahl des Projektes", \
            "Projekte", items, 0, False)

        if not ok:
            print("  Auswahl abgebrochen")
            return

        if not item:
            print("Keine Datenbank ausgewählt")
            return

        print("  Auswahl Projekt: " + item)
        self.setProject(item)

    def setProject(self,name):
        # print("Data.setProject")

        self.projName = name
        self.projectName = fileName = self.dirName + "/" + self.projName + ".db"
        self.main.setWindowTitle("Alfa - " + self.projName)  
        self.db.createConnection(self.projectName)

        # Fill PersonListWidget (Table) from columns, which are actually shown
        # TODO: generalize the following fixed list
        data = self.db.selectPersonList(self.fields)
        if data:
            self.main.widget.listFrame.fillTable(data)
        else:
            self.clearWidgets()

    def clearWidgets(self):
        # print("Data.clearWidgets")
        self.main.widget.listFrame.clearTable()
        self.main.widget.persFrame.clearPerson()
        self.main.graphList.clear()

    def importData(self):
        # ----- Get Filename, which is to be imported ----- #
        fileDlg = QFileDialog()
        fname = fileDlg.getOpenFileName( self.main, \
                'Wählen Sie die zu importierende Datei aus', \
                "MyImport/", \
                "Excel (*.xlsx);;CSV (*.csv);;Gedcom (*.ged);;Json (*.json)"
            )
        file = fname[0]

        # Stop if nothing chosen
        if file == "":
            return

        # ----- Create new project ----- #
        # TODO: offer to empty an existing database and adding import-data
        if self.projName != "":
            self.clearWidgets()
        self.newProject()

        # ----- Process Data ----- #
        if file:
            # TODO: which file type? Mapping necessary?
            if file[-4:] == ".ged":
                self._convertDataFormatGedToJson(file)
                file = file[0:-4] + ".json"
            elif file[-4:] == ".csv":
                self._convertDataFormatCsvToJson(file)
                file = file[0:-4] + ".json"
            elif file[-5:] == ".json":
                print("json")
            elif file[-5:] == ".xlsx":
                self._convertDataFormatXlsxToJson(file)
                file = file[0:-5] + ".json"
            else:
                QMessageBox.information(self.main, \
                    "Einlesen nicht möglich", \
                    "Das gewählte Format wurde noch nicht implementiert", \
                    buttons=QMessageBox.Ok
                  )
                return
            
            self._importJsonFile(file)

        # Show Data in Table
        data = self.db.selectPersonList(self.fields)
        self.main.widget.listFrame.fillTable(data)

    def exportData(self):
        # Conversion of json fle to ged file
        fileDlg = QFileDialog()
        fname = fileDlg.getOpenFileName( self.main, \
                'Wählen Sie die umzuwandelnde json Datei aus', \
                "MyImport/", \
                "Json (*.json)"
            )
        file = fname[0]
        
        # Stop if nothing chosen
        if file == "":
            return
        
        note_cnt = 0
        note_obj = []

        # ----- Header ----- #
        fw = open(self.projName + ".json", 'w', encoding='utf8')
        fw.write("0 HEAD\n")
        fw.write("1 SOUR Alva\n")
        fw.write("2 CORP (private)\n")
        fw.write("3 ADDR https://github.com/users/mawi2021/projects/1\n")
        fw.write("1 Gedbas\n")
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
        with open(file) as json_file:
            data = json.load( json_file )
        
        # ----- Each Person ----- #
        for i in range(data["INDI"].len()):
            f = open(self.projName + ".ged", 'a', encoding='utf8')
            
            f.write("0 @" + str(data["INDI"][i]["id"]) + "@ INDI\n")
            f.write("1 NAME " + data["INDI"][i]["NAME"]["id"] + "\n")
            f.write("2 GIVN " + data["INDI"][i]["NAME"]["GIVN"] + "\n")
            f.write("2 SURN " + data["INDI"][i]["NAME"]["SURN"] + "\n")
            
            if data["INDI"][i]["SEX"] == "m":
                f.write("1 SEX M\n")
            elif data["INDI"][i]["SEX"] == "w":
                f.write("1 SEX F\n")
                
            f.write("1 BIRT\n")
            f.write("2 DATE " + data["INDI"][i]["BIRT"]["DATE"] + "\n")
            f.write("2 PLAC " + data["INDI"][i]["BIRT"]["PLAC"] + "\n")
            
            f.write("1 DEAT\n")
            f.write("2 DATE " + data["INDI"][i]["DEAT"]["DATE"] + "\n")
            f.write("2 PLAC " + data["INDI"][i]["PLAC"]["PLAC"] + "\n")
            
            f.write("1 CHR\n")  # Taufe
            f.write("2 DATE " + data["INDI"][i]["CHR"]["DATE"] + "\n")
            
            f.write("1 FAMC @" + str(data["INDI"][i]["FAMC"]) + "@\n")
            
            # Comments
            f.write("1 NOTE @" + str(note_cnt) + "@\n")
            note_obj[note_cnt] = data["INDI"][i]["comment"]
            note_cnt = note_cnt + 1
            f.write("1 NOTE @" + str(note_cnt) + "@\n")
            note_obj[note_cnt] = data["INDI"][i]["comment_father"]
            note_cnt = note_cnt + 1
            f.write("1 NOTE @" + str(note_cnt) + "@\n")
            note_obj[note_cnt] = data["INDI"][i]["comment_mother"]
            note_cnt = note_cnt + 1            
            
            f.close()
            
        for i in range(data.FAM.len()):
            f = open(self.projName + ".ged", 'a', encoding='utf8')
            
            f.write("0 @" + str(data["FAM"][i]["id"]) + "@ FAM\n")
            
            f.write("1 HUSB @" + str(data["FAM"][i]["HUSB"]) + "@\n")
            f.write("1 WIFE @" + str(data["FAM"][i]["WIFE"]) + "@\n")
            
            for k in range(data["FAM"][i]["CHIL"].len()):
                f.write("1 CHIL @" + str(data["FAM"][i]["CHIL"][k]) + "@\n")
                
            f.write("1 MARR\n")
            f.write("2 DATE " + data["FAM"][i]["MARR"]["DATE"] + "\n")
            f.write("2 PLAC " + data["FAM"][i]["MARR"]["PLAC"] + "\n")
        
            # Kommentare (Vater, Mutter, Ehe)
            f.write("1 NOTE @" + str(note_cnt) + "@\n")
            note_obj[note_cnt] = data["INDI"][i]["comment"]
            note_cnt = note_cnt + 1
            f.write("1 NOTE @" + str(note_cnt) + "@\n")
            note_obj[note_cnt] = data["INDI"][i]["comment_father"]
            note_cnt = note_cnt + 1
            f.write("1 NOTE @" + str(note_cnt) + "@\n")
            note_obj[note_cnt] = data["INDI"][i]["MARR"]["comment"]
            note_cnt = note_cnt + 1            
            
            f.close()
            
        for i in range(note_obj.len()):
            f = open(self.projName + ".ged", 'a', encoding='utf8')
            f.write("0 @" + str(i) + "@ NOTE\n")
            f.write("1 CONC " + str(note_obj[i]) + "\n") # TODO: Umbruch nach 70 Zeichen, ggf. schon in der Zeile NOTE
            f.close()
            
        # ----- Footer ----- #
        fw = open(self.projName + ".json", 'a', encoding='utf8')
        fw.write("0 TRLR\n")
        f.close()
            

    def _convertDataFormatXlsxToJson(self,fname):
        # :TODO: Ehen aus 2. Excel einlesen und damit die Daten ergänzen
        df = pandas.read_excel(fname, sheet_name="Taufen Alle", dtype=str)
        first = True
        
        print("Start Lesen der Daten aus der Excel-Datei")
        
        # Initialize File
        f = open(fname[0:-5] + ".json", 'w', encoding='utf8')
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
            obj["id"]      = str(df.ID._values[i])
            obj["NAME"]    = {}
            obj["comment"] = ""
            
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
                obj["comment"] = "Geburt: KB Lohsa Seite "
                if str(df.Seite._values[i]) != "nan":
                    obj["comment"] = obj["comment"] + str(df.Seite._values[i])
                obj["comment"] = obj["comment"] + " #"
                if str(df.Nummer._values[i]) != "nan":
                    obj["comment"] = obj["comment"] + str(df.Nummer._values[i])
                obj["comment"] = obj["comment"] + " "
                if str(df.GebJahr._values[i]) != "nan":
                    obj["comment"] = obj["comment"] + str(int(df.GebJahr._values[i]))
                    
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
            # if str(df["Ehe am"]._values[i]) != "nan":
            #     obj["comment"] = obj["comment"] + "\nEhe am: " + str(df["Ehe am"]._values[i])
            # if str(df.Eheort._values[i]) != "nan":
            #     obj["comment"] = obj["comment"] + "\nEhe in: " + str(df.Eheort._values[i])
            # if str(df.PartnerID._values[i]) != "nan":
            #     obj["comment"] = obj["comment"] + "\nPartnerID: " + str(df.PartnerID._values[i])
            if str(df["#Ehe"]._values[i]) != "nan":
                obj["FAMC"] = obj["comment"] + "\nEigene EheID: " + str(df["#Ehe"]._values[i])
            if str(df.Ehepartner._values[i]) != "nan":
                obj["comment"] = obj["comment"] + "\nPartner: " + str(df.Ehepartner._values[i])                
            # if str(df.EheSeite._values[i]) != "nan":
            #     obj["comment"] = obj["comment"] + "\nQuelle Ehe KB: Seite " + str(df.EheSeite._values[i])
            # if str(df["Ehe#"]._values[i]) != "nan":
            #     obj["comment"] = obj["comment"] + "/" + str(df["Ehe#"]._values[i])
                            
            # Death
            if str(df.Tod._values[i]) != "nan" or str(df.SterbeOrt._values[i]) != "nan":
                obj["DEAT"] = {}
                if str(df.Tod._values[i]) != "nan":
                    obj["DEAT"]["DATE"] = df.Tod._values[i]
                if str(df.SterbeOrt._values[i]) != "nan":
                    obj["DEAT"]["PLAC"] = df.SterbeOrt._values[i]
                    
            obj["comment_father"] = ""
            if str(df.Vater._values[i]) != "nan":
                if str(df.Vater._values[i]) != "nan":
                    obj["comment_father"] = obj["comment_father"] + str(df.Vater._values[i])
                
            obj["comment_mother"] = ""
            if str(df.Mutter._values[i]) != "nan":
                if str(df.Mutter._values[i]) != "nan":
                    obj["comment_mother"] = obj["comment_mother"] + str(df.Mutter._values[i])
            
            # Comment    
            if str(df.Kommentar._values[i]) != "nan":
                obj["comment"] = obj["comment"] + "\n" + df.Kommentar._values[i]
                
            # No Children
            if str(df["Keine Nachkommen"]._values[i]) != "nan":
                obj["no_children"] = "X"
                
            # Family where I am a child
            if str(df["#Ehe Eltern"]._values[i]) != "nan":
                obj["FAMC"] = df["#Ehe Eltern"]._values[i]
                
            # Unehelich?
            if str(df["Unehelich"]._values[i]) != "nan":
                obj["unehelich"] = "X"           
                                   
            # :TODO: "Verwandt", "Baum"
            
            # Write Data to File
            f = open(fname[0:-5] + ".json", 'a', encoding='utf8')
            if first:
                first = False
            else:
                f.write(",\n")
            json.dump(obj, f, indent=4, ensure_ascii=False)
            f.close()
            
        print("Ende Verarbeitung Personen, Beginn Speicherung als json-Datei")

        # Close INDI Brackets, open FAM Brackets
        f = open(fname[0:-5] + ".json", 'a', encoding='utf8')
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
            obj["id"] = str(df["Ehe ID"]._values[i])
            
            # He
            if str(df["ID Er"]._values[i]) != "nan":
                obj["HUSB"] = str(df["ID Er"]._values[i])
            
            obj["comment_father"] = str(df["Stand Er"]._values[i]) \
                                    + " " + str(df["Vorname Er"]._values[i]) \
                                    + " " + str(df["Familienname"]._values[i]) \
                                    + "; " + str(df["Beruf Er"]._values[i]) \
                                    + "; " + str(df["Vater Er"]._values[i]) \
                                    + " (" + str(df["Ort Er"]._values[i]) \
                                    + ") " + str(df["Geb Er"]._values[i]) 
            
            # She
            if str(df["ID Sie"]._values[i]) != "nan":
                obj["WIFE"] = str(df["ID Sie"]._values[i])
            
            obj["comment_mother"] = str(df["Stand Sie"]._values[i]) \
                                    + " " + str(df["Vorname Sie"]._values[i]) \
                                    + " " + str(df["Nachname Sie"]._values[i]) \
                                    + "; " + str(df["Vater/ehem. Mann Sie"]._values[i]) \
                                    + " (" + str(df["Ort Sie"]._values[i]) \
                                    + ") " + str(df["Geb Sie"]._values[i]) 
                                    
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
                obj["CHIL"].append(str(df["Geschw1"]._values[i]))
            if str(df["Geschw2"]._values[i]) != "nan":
                obj["CHIL"].append(str(df["Geschw2"]._values[i]))
            if str(df["Geschw3"]._values[i]) != "nan":
                obj["CHIL"].append(str(df["Geschw3"]._values[i]))
            if str(df["Geschw4"]._values[i]) != "nan":
                obj["CHIL"].append(str(df["Geschw4"]._values[i]))
            if str(df["Geschw5"]._values[i]) != "nan":
                obj["CHIL"].append(str(df["Geschw5"]._values[i]))
            if str(df["Geschw6"]._values[i]) != "nan":
                obj["CHIL"].append(str(df["Geschw6"]._values[i]))
            if str(df["Geschw7"]._values[i]) != "nan":
                obj["CHIL"].append(str(df["Geschw7"]._values[i]))
            if str(df["Geschw8"]._values[i]) != "nan":
                obj["CHIL"].append(str(df["Geschw8"]._values[i]))
            if str(df["Geschw9"]._values[i]) != "nan":
                obj["CHIL"].append(str(df["Geschw9"]._values[i]))
            if str(df["Geschw10"]._values[i]) != "nan":
                obj["CHIL"].append(str(df["Geschw10"]._values[i]))
            if str(df["Geschw11"]._values[i]) != "nan":
                obj["CHIL"].append(str(df["Geschw11"]._values[i]))
            if str(df["Geschw12"]._values[i]) != "nan":
                obj["CHIL"].append(str(df["Geschw12"]._values[i]))
                        
            f = open(fname[0:-5] + ".json", 'a', encoding='utf8')
            if first:
                first = False
            else:
                f.write(",\n")
            json.dump(obj, f, indent=4, ensure_ascii=False)
            f.close()
            
        # Close FAM Brackets
        f = open(fname[0:-5] + ".json", 'a', encoding='utf8')
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
        f = open(fname[0:-4] + ".json", 'w', encoding='utf8')
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
    
                # braces, colons new lines and indentation - magic ;o)
                f = open(fname[0:-4] + ".json", 'a', encoding='utf8')
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
        
        # Closing Brackets
        f = open(fname[0:-4] + ".json", 'a', encoding='utf8')
        f.write("\n]\n}")
        f.close()
            
    def _convertDataFormatCsvToJson(self,file):
        # print("Data.readCsvFile")

        # :TODO: Ist erste Zeile mit Daten oder Spaltenüberschriften?
        # :TODO: Das ist die Reihenfolge der Felder ("Mapping"), die irgendwie anders 
        # pro Datei erzeugt werden muss, z.B. durch Abfrage
        fields = ["id","firstname","gebname","surname","sex","birth_date","birth_place","death_date",\
                  "death_place","man","woman","comment","url","kinderlos"]
        numFields = len(fields) 
        oldLine = ""
        family = 0

        bytes = min(32, os.path.getsize(file))
        raw = open(file, 'rb').read(bytes)
        result = chardet.detect(raw)
        # print(result)
        encoding = result['encoding']
        # TODO: does not work always => dirty:
        if encoding == "ascii": encoding = "utf-8"

        f = open(file, 'r', encoding=encoding)
 
        for line in f:
            line = oldLine + line.strip()

            temp = line
            while True:
                temp = temp.replace(",,", ",\"\",")
                if temp == line:
                    break
                line = temp

            elements = line.split("\",\"")
            # print("*** " + line)
            # print(elements)
            # print("==> " + str(len(elements)))
            if len(elements) < numFields:
                oldLine = line + "\n"
                continue
            else:
                oldLine = ""

            person = {  "id": "",          ##
                        "firstname": "",   ##
                        "gebname": "",
                        "surname": "",     ##
                        "sex": "",         ##
                        "birth_date": "",  ##
                        "birth_place": "", ##
                        "death_date": "",  ##
                        "death_place": "", ##
                        "man": "",         ##
                        "woman": "",       ##
                        "comment": "",     ##
                        "url": "",
                        "kinderlos": "" 
                     }

            cnt = -1
            for element in elements:
                cnt = cnt + 1 

                # Remove first '"'
                if cnt == 0:
                    element = element[1:]
                if cnt == numFields - 1:
                    element = element[0:-1]

                # print(str(cnt) + element)
                fieldname = fields[cnt]
                person[fieldname] = element
            
            # ----- Save person ----------------------------------------------------------------- #
            # :TODO: Gebname, Kommentar, URL, kinderlos #
            print("ID: " + person["id"] + " kinderlos: " + person["kinderlos"])

            self.db.insertPerson(
                                    person["id"], 
                                    person["surname"], 
                                    person["firstname"], 
                                    str(family),
                                    "", 
                                    person["sex"],
                                    person["comment"]
                                )

            family = family + 1
            self.db.insertFamily(str(family), {"man": person["man"], "woman": person["woman"]})

            self.db.insertEvent({"id":      person["id"], 
                                "evt_type": "BIRT",
                                "evt_date": person["birth_date"],
                                "place":    person["birth_place"]
                                })

            self.db.insertEvent({"id":      person["id"], 
                                "evt_type": "DEAT",
                                "evt_date": person["death_date"],
                                "place":    person["death_place"]
                                })

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

    def _importJsonFile(self,file):

        cnt = 0

        bytes = min(5000, os.path.getsize(file))
        raw = open(file, 'rb').read(bytes)
        result = chardet.detect(raw)
        
        encoding = result['encoding']
        print("Encoding : " + encoding)

        # ----- Post Processing ----- #
        with open(file, encoding=encoding) as f:
            jData = json.load(f)

        # ----- Person ----- #
        for pers in jData["INDI"]:
            cnt = cnt + 1
            if cnt % 100 == 0:
                print("Speichern auf Datenbank: Verarbeite " + str(cnt) + ". Person")

            key           = pers["id"]   if 'id'   in pers else ''
            family        = pers["FAMC"] if 'FAMC' in pers else '' # Family where I am a child
            sex           = pers["SEX"]  if 'SEX'  in pers else ''
            comment       = pers["comment"] if 'comment' in pers else ''
            comment       = comment.replace("'", "''")
            commentFather = pers["commentFather"] if 'commentFather' in pers else ''
            commentFather = commentFather.replace("'", "''")
            commentMother = pers["commentMother"] if 'commentMother' in pers else ''
            commentMother = commentMother.replace("'", "''")
            linkagetype   = 'BIRTH'

            if 'NAME' in pers:
                surname   = pers["NAME"]["SURN"] if 'SURN' in pers["NAME"] else ''
                firstname = pers["NAME"]["GIVN"] if 'GIVN' in pers["NAME"] else ''
            else: surname = ''; firstname = ''           
            
            if 'BIRT' in pers:
                birthDate   = pers["BIRT"]["DATE"] if 'DATE' in pers["BIRT"] else ''
                birthPlace  = pers["BIRT"]["PLAC"] if 'PLAC' in pers["BIRT"] else ''
            else: birthDate = ''; birthPlace = ''
            
            if 'DEAT' in pers:
                deathDate   = pers["DEAT"]["DATE"] if 'DATE' in pers["DEAT"] else ''
                deathPlace  = pers["DEAT"]["PLAC"] if 'PLAC' in pers["DEAT"] else ''
            else: deathDate = ''; deathPlace = ''
            
            self.db.insertPerson(key, surname, firstname, family, linkagetype, sex, birthDate, \
                                 birthPlace, deathDate, deathPlace, comment, commentFather, \
                                 commentMother)
            
            self.db.insertDetail(key, 'INDI', json.dumps(pers,indent=4))

        # ----- Family ----- #       
        cnt = 0     
        for fam in jData["FAM"]:
            cnt = cnt + 1
            if cnt % 100 == 0:
                print("Speichern auf Datenbank: Verarbeite " + str(cnt) + ". Familie")

            key   = fam["id"]   if 'id'   in fam else ''
            man   = fam["HUSB"] if 'HUSB' in fam else ''
            woman = fam["WIFE"] if 'WIFE' in fam else ''

            commentFather = fam["comment_father"] if 'comment_father' in fam else ''
            commentFather = commentFather.replace("'", "''")
            commentMother = fam["comment_mother"] if 'comment_mother' in fam else ''
            commentMother = commentMother.replace("'", "''")
            
            if 'MARR' in fam:
                marrDate  = fam["MARR"]["DATE"] if 'DATE' in fam["MARR"] else ''
                marrPlace = fam["MARR"]["PLAC"] if 'PLAC' in fam["MARR"] else ''
                comment   = fam["MARR"]["comment"] if 'comment' in fam["MARR"] else ''
                comment   = comment.replace("'", "''")
                
            childList = fam["CHIL"] if 'CHIL' in fam else []
            children = " " . join([str(item) for item in childList])
            
            self.db.insertFamily(key, marrDate, marrPlace, man, woman, children, commentFather, commentMother, comment)
            
            text = json.dumps(fam,indent=4)
            text = text.replace("'", "''")
            self.db.insertDetail(key, 'FAM', text)

        print("Speicherung auf Datenbank abgeschlossen")
        return
