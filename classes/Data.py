import os, chardet
from PyQt5.QtWidgets import QInputDialog, QFileDialog, QMessageBox
import json
import sqlite3

class Data():

    def __init__(self, main):
        super(Data, self).__init__()
        self.main          = main
        self.conn          = None
        self.cursor        = None
        self.conn_config   = None
        self.cursor_config = None
        self.config_name   = None
        self.base_dir      = os.path.dirname(__file__) + os.sep + ".." + os.sep
        self.project_dir   = self.base_dir + "data" + os.sep
        self.config_dir    = self.base_dir + "config" + os.sep
        self.language_dir  = self.base_dir + "i18n" + os.sep
        self.indi_columns  = [   ["id",          "INTEGER PRIMARY key"],
                                ["GIVN",        "TEXT"],
                                ["SURN",        "TEXT"],
                                ["SEX",         "TEXT"],
                                ["BIRT_DATE",   "TEXT"],
                                ["BIRT_PLAC",   "TEXT"],
                                ["DEAT_DATE",   "TEXT"],
                                ["DEAT_PLAC",   "TEXT"],
                                ["url",         "TEXT"],
                                ["comment",     "TEXT"],
                                ["media",       "TEXT"],
                                ["source",      "TEXT"],
                                ["finished",    "TEXT"],
                                ["father",      "INTEGER"],
                                ["mother",      "INTEGER"],
                                ["birthname",   "TEXT"],
                                ["no_child",    "TEXT"],
                                ["guess_birth", "TEXT"],
                                ["guess_death", "TEXT"]
                            ]
        self.fam_columns   = [   ["id",          "INTEGER PRIMARY key"],
                                ["HUSB",        "INTEGER"],
                                ["WIFE",        "INTEGER"],
                                ["MARR_DATE",   "TEXT"],
                                ["MARR_PLAC",   "TEXT"],
                                ["comment",     "TEXT"]
                            ]
        self.check_conf_db()
        self.config_name   = self.get_config_name()
        self.language      = self.get_conf_attribute("language")
        self.fill_language_table()
        self.project       = self.get_conf_attribute("project")

    def check_conf_db(self):
        # Check existence of config subdirectory
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        
        # Connect to or create config-database
        self.conn_config = sqlite3.connect(self.config_dir + "config.db") 
        self.cursor_config = self.conn_config.cursor()
        self.cursor_config.execute("SELECT name FROM sqlite_master WHERE type='table';") 

        found_conf = False
        found_text = False
        for table in self.cursor_config.fetchall():
            if "CONF" == table[0]:
                found_conf = True
            elif "TEXT" == table[0]:
                found_text = True

        # Check existence or create table CONF in config-database
        if not found_conf:
            self.cursor_config.execute("CREATE TABLE IF NOT EXISTS CONF (" \
                                       + "config_name TEXT, " \
                                       + "property    TEXT, " \
                                       + "value       TEXT, " \
                                       + "PRIMARY KEY(config_name, property) )")
            self.conn_config.commit()

        # Check existence or create table TEXT in config-database
        if not found_text:
            self.cursor_config.execute("CREATE TABLE IF NOT EXISTS TEXT (" \
                                       + "name     TEXT, " \
                                       + "language TEXT, " \
                                       + "text     TEXT, " \
                                       + "PRIMARY KEY(name, language) )")
            self.conn_config.commit()
            
        # Check existence or create property table_columns as default
        if not found_conf or not found_text:
            self.set_conf_defaults()
        # self.language = self.get_conf_attribute("language")

        # # Fill language-dependent texts from file to DB
        # found = False
        # self.cursor_config.execute("SELECT name FROM TEXT WHERE language = '" + self.language + "' LIMIT 1")
        # for row in self.cursor_config.fetchall():
        #     found = True

        # if not found:
        #     filename = self.language_dir + "i18n_" + self.language + ".properties"
        #     if os.path.exists(filename):
        #         with open(filename, "r", encoding="utf-8") as f:
        #             for line in f:
        #                 line = line.strip()
        #                 if line != "" and line[0] != "#":
        #                     name, text = line.split("=",2)
        #                     self.cursor_config.execute("""INSERT INTO TEXT (name, language, text) """ \
        #                           + """VALUES ('""" + name + """', '""" + self.language + """', '""" + text + """') """ \
        #                           + """ON CONFLICT (name, language) DO UPDATE SET text = excluded.text""")
        #     self.conn_config.commit()
    def check_db_structure(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';") 
        tabellen = self.cursor.fetchall()
        found_indi = False
        found_fam  = False

        for tabelle in tabellen:
            if "INDI" == tabelle[0]:
                found_indi = True
            elif "FAM" == tabelle[0]:
                found_fam = True

        # Table INDI #
        if not found_indi:
            self.create_db_tab_indi()
        else:
            self.cursor.execute("PRAGMA table_info(INDI)")
            fields = [row[1] for row in self.cursor.fetchall()]  # column name in index 1
            for col in self.indi_columns:
                if col[0] not in fields:
                    self.cursor.execute("ALTER TABLE INDI ADD COLUMN " + col[0] + " " + col[1] + ";")
                    self.conn.commit()

        # Table FAM #
        if not found_fam:
            self.create_db_tab_fam()
        else:
            self.cursor.execute("PRAGMA table_info(FAM)")
            fields = [row[1] for row in self.cursor.fetchall()]  # column name in index 1
            for col in self.fam_columns:
                if col[0] not in fields:
                    self.cursor.execute("ALTER TABLE FAM ADD COLUMN " + col[0] + " " + col[1] + ";")
                    self.conn.commit()
    def convert_data_format_json_to_db(self, file):
        # ----- Figure out codepage of file ----- #
        bytes = min(32, os.path.getsize(file))
        raw = open(file, 'rb').read(bytes)
        result = chardet.detect(raw)
        encoding = result['encoding']
        
        if encoding == "ascii": encoding = "utf-8"

        # ----- Read Data ----- #
        with open(file, encoding=encoding) as f:
            jData = json.load(f)
        f.close()

        # Conversion #
        for table in jData:
            if table == "INDI":
                for person in jData[table]:
                    if "id" in person:
                        persID = int(person["id"][2:-1])
                        self.create_person(persID)
                        for key in person:
                            if key == "id": continue
                            if key == "NAME":
                                for sub_key in person[key]:
                                    self.set_indi_attribute(persID, sub_key, person[key][sub_key])
                            elif key == "BIRT":
                                for sub_key in person[key]:
                                    self.set_indi_attribute(persID, "BIRT_" + sub_key, person[key][sub_key])
                            elif key == "DEAT":
                                for sub_key in person[key]:
                                    self.set_indi_attribute(persID, "DEAT_" + sub_key, person[key][sub_key])
                            elif key in ("SEX", "comment", "finished", "media", "source", "url"):
                                self.set_indi_attribute(persID, key, person[key])
                            elif key in ("FAMC", "FAMS"):
                                pass  # no message
                            else:
                                self.main.add_status_message(self.get_text("UNKNOWN_KEY") + " INDI: " + key)
                    else:
                        self.main.add_status_message(self.get_text("UNKNOWN_KEY") + " INDI")
                        
            elif table == "FAM":
                for family in jData[table]:
                    if "id" in family:
                        children = []
                        father = mother = ""
                        famID = int(family["id"][2:-1])
                        self.create_family(famID)
                        for key in family:
                            if key == "id": continue
                            if key in ("WIFE", "HUSB"):
                                value = int(family[key][2:-1])
                                self.set_fam_attribute(famID, key, value)
                                if key == "WIFE":
                                    mother = value
                                elif key == "HUSB":
                                    father = value
                            elif key in ("comment"):
                                self.set_fam_attribute(famID, key, family[key])
                            elif key == "MARR":
                                for sub_key in family[key]:
                                    self.set_fam_attribute(persID, "MARR_" + sub_key, family[key][sub_key])
                            elif key == "CHIL":
                                children = family[key]
                            else:
                                self.main.add_status_message(self.get_text("UNKNOWN_KEY") + " FAM: " + key)
                        for child in children:
                            if father != "":
                                self.set_indi_attribute(int(child[2:-1]), "father", father)
                            if mother != "":
                                self.set_indi_attribute(int(child[2:-1]), "mother", mother)
            else:
                self.main.add_status_message(self.get_text("UNKNOWN_TABLE") + ": " + table)
    def convert_data_format_csv_to_db(self, file): # field separator in csv is "#§" and no " around fields; no header line
        # ----- Figure out codepage of file ----- #
        bytes = min(32, os.path.getsize(file))
        raw = open(file, 'rb').read(bytes)
        result = chardet.detect(raw)
        encoding = result['encoding']
        
        if encoding == "ascii": encoding = "utf-8"

        # ----- Read Data ----- #
        line_old = ""
        tab_fields = "id,GIVN,SURN,SEX,BIRT_DATE,BIRT_PLAC,DEAT_DATE,DEAT_PLAC,url,comment,source," + \
                     "father,mother,birthname,no_child,guess_birth,guess_death"
        with open(file, encoding=encoding) as f:            
            for line in f:
                line = line.strip()
                if line_old != "":
                    line = line_old + "\n" + line
                    line_old = ""
                fields = line.split("#§")
                if len(fields) < 25:
                    line_old = line
                    continue

                if len(fields) > 25:
                    self.main.add_status_message(self.get_text("CONVERSION_ERROR") + " " + fields[0])
                    continue

                # Process data #
                # 13 #§ehePartner  <= redundant, ignore
                # 14 #§kinder      <= redundant, ignore
                self.main.add_status_message(self.get_text("PROCESS_PERSON") + ": " + fields[0])

                urls = fields[19] + "\n" + fields[20] + "\n" + fields[21] + "\n" + fields[22]
                urls = urls.replace("\n\n","\n").replace("\n\n","\n").replace("\n\n","\n")

                source = fields[17]
                if fields[8] != "" and fields[8] != "0":
                    source = source + "\n" + self.get_text("BIRTH_REG") + " " + fields[8]
                if fields[12] != "" and fields[12] != "0":
                    source = source + "\n" + self.get_text("DEATH_REG") + " " + fields[12]
                source = source.replace("\n\n","\n")

                val_fields = fields[0]  + ",'"  + fields[1]  + "','" + fields[3]  + "','" + fields[4]  + "','" + fields[5] + "','"  \
                           + fields[7]  + "','" + fields[9]  + "','" + fields[11] + "','" + urls       + "','" \
                           + fields[18] + "','" + source     + "',"  + fields[15] + ","   + fields[16] + ",'" \
                           + fields[2]  + "','" + fields[23] + "','" + fields[6]  + "','" + fields[10] + "'"

                self.cursor.execute("INSERT INTO INDI ("+ tab_fields + ") VALUES (" + val_fields + ")")
            self.conn.commit()  

        # --------------------------- #
        # ----- IMPORT MARRIAGE ----- #
        # --------------------------- #
        # ----- Get Filename, which is to be imported ----- #
        fileDlg = QFileDialog()
        fileStruc = fileDlg.getOpenFileName( self.main, \
                self.get_text("CHOICE_IMPORT_MARRIAGE_FILE"), \
                "MyImport/", \
                "Gedcom CSV (*.csv);;"
            )
        fileName = fileStruc[0]

        # Stop if nothing chosen
        if fileName == "":
            return
        
        line_old = ""
        tab_fields = "id,HUSB,WIFE,MARR_DATE,MARR_PLAC,comment"
        with open(fileName, encoding=encoding) as f:            
            for line in f:
                line = line.strip()
                if line_old != "":
                    line = line_old + "\n" + line
                    line_old = ""
                fields = line.split("#§")
                if len(fields) < 6:
                    line_old = line
                    continue

                if len(fields) > 6:
                    self.main.add_status_message(self.get_text("CONVERSION_ERROR") + fields[0])
                    continue

                self.main.add_status_message(self.get_text("PROCESS_MARRIAGE") + ": " + fields[0])
                val_fields = fields[0]  + ","  + fields[1]  + "," + fields[2]  + ",'" + fields[3]  + "','" + fields[4] + "','" + fields[5] + "'"

                self.cursor.execute("INSERT INTO FAM ("+ tab_fields + ") VALUES (" + val_fields + ")")
                # 0  lfdnr      
                # 1  #§idmann
                # 2  #§idfrau
                # 3  #§datum
                # 4  #§ort
                # 5  #§kommentar
            self.conn.commit()  
    def create_db(self, project_name):
        self.conn = sqlite3.connect(self.project_dir + project_name + ".db") 
        self.cursor = self.conn.cursor()
        self.create_db_tab_indi()
        self.create_db_tab_fam()
    def create_db_tab_fam(self):
        field_str = ""
        first = True
        for col in self.fam_columns:
            if first:
                field_str = col[0] + " " + col[1]
                first = False
            else:
                field_str = field_str + ",\n" + col[0] + " " + col[1]

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS FAM (""" + field_str + """)""")
    def create_db_tab_indi(self):
        field_str = ""
        first = True
        for col in self.indi_columns:
            if first:
                field_str = col[0] + " " + col[1]
                first = False
            else:
                field_str = field_str + ",\n" + col[0] + " " + col[1]

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS INDI (""" + field_str + """)""")
    def create_family(self, famID = -1):
        if famID == -1:
            self.cursor.execute("INSERT INTO FAM DEFAULT VALUES")
        else:
            self.cursor.execute("INSERT INTO FAM (id) VALUES (" + str(famID) + ")")
        self.conn.commit() 
        return self.cursor.lastrowid
    def create_person(self, persID = -1):
        if persID == -1:
            self.cursor.execute("SELECT id FROM INDI ORDER BY id")  # search for next ID-hole
            cnt = 0
            found = False
            for row in self.cursor.fetchall():
                cnt = cnt + 1
                if row[0] != cnt:
                    self.cursor.execute("INSERT INTO INDI (id) VALUES (" + str(cnt) + ")")
                    found = True
                    break
            if not found:
                self.cursor.execute("INSERT INTO INDI DEFAULT VALUES")
        else:
            self.cursor.execute("INSERT INTO INDI (id) VALUES (" + str(persID) + ")")
        self.conn.commit() 
        return self.cursor.lastrowid
    def create_project(self):
        if not os.path.exists(self.project_dir):
            os.makedirs(self.project_dir)

        proj_txt = self.get_text("PROJECTNAME")
        projectName, ok = QInputDialog.getText(self.main, \
                                            proj_txt, \
                                            self.get_text("GIVE_PROJECTNAME") \
                                            )

        while True:
            if not ok: return None

            fileName = self.project_dir + os.sep + projectName + ".db"

            if os.path.isfile(fileName): 
                txt = proj_txt + " " + projectName + \
                      " " + self.get_text("NAME_EXISTS")
                projectName, ok = QInputDialog.getText(self.main, proj_txt, txt )
            elif projectName == "":
                projectName, ok = QInputDialog.getText(self.main, \
                                                proj_txt, \
                                                self.get_text("GIVE_PROJECTNAME") \
                                            )
            else:
                break

        self.main.clear_widgets()
        self.project = projectName
        self.main.setWindowTitle("Alva - " + projectName)  

        # Create database file and create tables #
        self.create_db(projectName)
        return projectName
    def copy_person(self, persID):  # only INDI values to be copied, no FAM
        newID = self.create_person()
        pers  = self.get_person(persID)
        for key, value in pers.items():
            if key == "id": 
                continue
            if key in ("father", "mother") and value == "":
                continue
            self.set_indi_attribute(newID, key, value)
        return newID
    def delete_person(self, persID):
        self.cursor.execute("DELETE FROM INDI WHERE id = " + str(persID))
        self.cursor.execute("DELETE FROM FAM WHERE WIFE = " + str(persID))
        self.cursor.execute("DELETE FROM FAM WHERE HUSB = " + str(persID))
        self.conn.commit()
    def exists_person(self, persID):
        self.cursor.execute("SELECT EXISTS(SELECT 1 FROM INDI WHERE id = " + str(persID) + ")") 
        for row in self.cursor.fetchall():
            if row[0] == 1:
                return True
        return False
    def exportData(self):
        self.main.add_status_message("exportData - " + self.get_text("NOT_IMPLEMENTED"))
        # Conversion of json fle to ged file
        # fileDlg = QFileDialog()
        # fname = fileDlg.getOpenFileName( self.main, \
        #         'Wählen Sie die umzuwandelnde json Datei aus', \
        #         "MyImport/", \
        #         "Json (*.json)"
        #     )
        # file_from = fname[0]
        # file_to = fname[0][0:-5] + ".ged"
        
        # # Stop if nothing chosen
        # if file_from == "":
        #     return
        
        # note_cnt = 1
        # note_obj = []

        # # ----- Header ----- #
        # fw = open(file_to, 'w', encoding='utf8')
        # fw.write("0 HEAD\n")
        # fw.write("1 SOUR Alva\n")
        # fw.write("2 CORP (private)\n")
        # fw.write("3 ADDR https://alva.ur-ahn.de\n")
        # fw.write("1 SUBM @SUB@\n")
        # fw.write("1 GEDC\n")
        # fw.write("2 VERS 5.5\n")
        # fw.write("2 FORM LINEAGE-LINKED\n")
        # fw.write("1 CHAR UTF-8\n")
        # fw.write("1 LANG German\n")
        # fw.write("0 @SUB@ SUBM\n")
        # fw.write("1 NAME Manuela Kugel\n")
        # fw.write("1 ADDR \n")
        # fw.write("2 CONT mawi@online.de\n")
        # fw.close()
        
        # # ----- Read json File ----- #
        # with open(file_from, encoding="utf-8") as json_file:
        #     data = json.load( json_file )
        
        # # ----- Each Person ----- #
        # i = 0
        # for obj in data["INDI"]:
        #     f = open(file_to, 'a', encoding='utf8')
            
        #     i = i + 1
        #     if i % 250 == 0:
        #         self.main.add_status_message("Konvertiere " + str(i) + ". Person ")    
            
        #     if "id" in obj:
        #         f.write("0 @" + str(obj["id"]) + "@ INDI\n")
                
        #     if "NAME" in obj:
        #         if "id" in obj["NAME"]:
        #             f.write("1 NAME " + obj["NAME"]["id"] + "\n")
        #         if "GIVN" in obj["NAME"]:
        #             f.write("2 GIVN " + obj["NAME"]["GIVN"] + "\n")
        #         if "SURN" in obj["NAME"]:
        #             f.write("2 SURN " + obj["NAME"]["SURN"] + "\n")
            
        #     if "SEX" in obj:
        #         if obj["SEX"] == "m":
        #             f.write("1 SEX M\n")
        #         elif obj["SEX"] == "w":
        #             f.write("1 SEX F\n")
                
        #     if "BIRT" in obj:
        #         f.write("1 BIRT\n")
        #         if "DATE" in obj["BIRT"]:
        #             found, date = self._convertDateToGedFormat(obj["BIRT"]["DATE"])
        #             if found:
        #                 f.write("2 DATE " + date + "\n")
        #         if "PLAC" in obj["BIRT"]:
        #             f.write("2 PLAC " + obj["BIRT"]["PLAC"] + "\n")
            
        #     if "DEAT" in obj:
        #         f.write("1 DEAT\n")
        #         if "DATE" in obj["DEAT"]:
        #             found, date = self._convertDateToGedFormat(obj["DEAT"]["DATE"])
        #             if found:
        #                 f.write("2 DATE " + date + "\n")
        #         if "PLAC" in obj["DEAT"]:
        #             f.write("2 PLAC " + obj["DEAT"]["PLAC"] + "\n")
            
        #     if "CHR" in obj:  # Taufe
        #         f.write("1 CHR\n")  
        #         if "DATE" in obj["CHR"]:
        #             found, date = self._convertDateToGedFormat(obj["CHR"]["DATE"])
        #             if found:
        #                 f.write("2 DATE " +date + "\n")
        
        #     if "FAMC" in obj: # my parents - can only happen once
        #         f.write("1 FAMC @" + str(obj["FAMC"]) + "@\n")
                
        #     if "FAMS" in obj:
        #         for fams in obj["FAMS"]:
        #             f.write("1 FAMS @" + str(fams) + "@\n")
            
        #     # Comments
        #     if "comment" in obj:
        #         f.write("1 NOTE @N" + str(note_cnt) + "@\n")
        #         note_obj.append({note_cnt: "Tauf-Eintrag/Kommentar: " + obj["comment"]})
        #         note_cnt = note_cnt + 1
        #     if "comment_father" in obj:
        #         f.write("1 NOTE @N" + str(note_cnt) + "@\n")
        #         note_obj.append({note_cnt: "Tauf-Eintrag >> Vater: " + obj["comment_father"]})
        #         note_cnt = note_cnt + 1
        #     if "comment_mother" in obj:
        #         f.write("1 NOTE @N" + str(note_cnt) + "@\n")
        #         note_obj.append({note_cnt: "Tauf-Eintrag >> Mutter: " + obj["comment_mother"]})
        #         note_cnt = note_cnt + 1            
            
        #     f.close()
            
        # self.main.add_status_message("Export Personen abgeschlossen")
            
        # # ----- Each Family ----- #
        # i = 0
        # for obj in data["FAM"]:
        #     f = open(file_to, 'a', encoding='utf8')
            
        #     i = i + 1
        #     if i % 100 == 0:
        #         self.main.add_status_message("Konvertiere " + str(i) + ". Familie ")    

        #     if "id" in obj:
        #         if str(obj["id"])[0] != 'F':
        #             f.write("0 @F" + str(obj["id"]) + "@ FAM\n")
        #         else:
        #             f.write("0 @" + str(obj["id"]) + "@ FAM\n")
            
        #     if "HUSB" in obj:
        #         if str(obj["HUSB"])[0] != 'I':
        #             f.write("1 HUSB @I" + str(obj["HUSB"]) + "@\n")
        #         else:
        #             f.write("1 HUSB @" + str(obj["HUSB"]) + "@\n")
                
        #     if "WIFE" in obj:
        #         if str(obj["WIFE"])[0] != 'I':
        #             f.write("1 WIFE @I" + str(obj["WIFE"]) + "@\n")
        #         else:
        #             f.write("1 WIFE @" + str(obj["WIFE"]) + "@\n")
            
        #     if "CHIL" in obj:
        #         for chil in obj["CHIL"]:
        #             if chil[0] != 'I':
        #                 f.write("1 CHIL @I" + chil + "@\n")
        #             else:
        #                 f.write("1 CHIL @" + chil + "@\n")
        
        #     if "MARR" in obj:        
        #         f.write("1 MARR\n")
        #         if "DATE" in obj["MARR"]:
        #             found, date = self._convertDateToGedFormat(obj["MARR"]["DATE"])
        #             if found:
        #                 f.write("2 DATE " +date + "\n")
        #         if "PLAC" in obj["MARR"]:
        #             f.write("2 PLAC " + obj["MARR"]["PLAC"] + "\n")
        
        #     # Kommentare (Vater, Mutter, Ehe)
        #     if "comment" in obj:
        #         f.write("1 NOTE @N" + str(note_cnt) + "@\n")
        #         note_obj.append({note_cnt: "Ehe-Eintrag der Eltern: " + obj["comment"]})
        #         note_cnt = note_cnt + 1
        #     if "comment_father" in obj:
        #         f.write("1 NOTE @N" + str(note_cnt) + "@\n")
        #         note_obj.append({note_cnt: "Ehe-Eintrag der Eltern >> Bräutigam: " + obj["comment_father"]})
        #         note_cnt = note_cnt + 1
        #     if "comment_mother" in obj:
        #         f.write("1 NOTE @N" + str(note_cnt) + "@\n")
        #         note_obj.append({note_cnt: "Ehe-Eintrag der Eltern >> Braut: " + obj["comment_mother"]})
        #         note_cnt = note_cnt + 1            
            
        #     f.close()
            
        # self.main.add_status_message("Export Familien abgeschlossen")
            
        # i = 0
        # for obj in note_obj:
        #     i = i + 1
        #     if i % 500 == 0:
        #         self.main.add_status_message("Konvertiere " + str(i) + ". Kommentar")    

        #     f = open(file_to, 'a', encoding='utf8')
        #     for key in obj:
        #         obj[key] = obj[key].replace("\n", " ")
                
        #         if len(obj[key]) >= 70:
        #             f.write("0 @N" + str(key) + "@ NOTE " + obj[key][0:70] + "\n")
        #             obj[key] = obj[key][70:]
        #         else:
        #             f.write("0 @N" + str(key) + "@ NOTE " + obj[key] + "\n")
        #             obj[key] = ""
                    
        #         while len(obj[key]) > 0:
        #             if len(obj[key]) >= 70:
        #                 f.write("1 CONC " + obj[key][0:70] + "\n")
        #                 obj[key] = obj[key][70:]
        #             else:
        #                 f.write("1 CONC " + obj[key] + "\n")
        #                 obj[key] = ""

        #     f.close()
            
        # self.main.add_status_message("Export Kommentare abgeschlossen")
            
        # # ----- Footer ----- #
        # fw = open(file_to, 'a', encoding='utf8')
        # fw.write("0 TRLR\n")
        # f.close()
        
        # self.main.add_status_message("----- Export abgeschlossen -----")
    def fill_language_table(self):
        if self.language == None:
            self.language = "de"

        # Change content of table TEXT (switch to texts from according i18n file content)
        self.cursor_config.execute("DELETE FROM TEXT")
        self.conn_config.commit()
        filename = self.language_dir + "i18n_" + self.language + ".properties"
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line != "" and line[0] != "#":
                    name, text = line.split("=",2)
                    self.cursor_config.execute("""INSERT INTO TEXT (name, language, text) """ \
                        + """VALUES ('""" + name + """', '""" + self.language + """', '""" + text + """') """ \
                        + """ON CONFLICT (name, language) DO UPDATE SET text = excluded.text""")
        self.conn_config.commit()
    def get_ancestors(self, persID):
        ids = {persID:{"child":-1}}    # each record includes: persID: { <table INDI>, partners (list), birth, death, year, child }
        lines = []                     # each record includes: boxLeft, boxRight
        min_year = -1
        max_year = -1
        if persID == -1:
            return (ids, lines, min_year, max_year)

        # sequence is important, therefore, add a helper array 
        helper = [{"id":persID,"child":-1}]
        while len(helper) > 0:
            key = helper[0]["id"]
            person = self.get_person(key)
            ids[key] = person
            ids[key]["child"]     = helper[0]["child"]
            ids[key]["partners"]  = self.get_partners_blood(key)
            ids[key]["birth"]     = self.main.get_date_line(ids[key]["BIRT_DATE"], ids[key]["BIRT_PLAC"], "*")
            ids[key]["death"]     = self.main.get_date_line(ids[key]["DEAT_DATE"], ids[key]["DEAT_PLAC"], "†")
            helper.pop(0)

            # father
            if ids[key]["father"] != -1:
                helper.insert(0, {"id":ids[key]["father"], "child":key})
                lines.append({"boxLeft":key, "boxRight":ids[key]["father"]})

            # mother
            if ids[key]["mother"] != -1:
                helper.insert(0, {"id":ids[key]["mother"], "child":key})
                lines.append({"boxLeft":key, "boxRight":ids[key]["mother"]})

            # year of birth, min_year, max_year
            if len(ids[key]["BIRT_DATE"]) > 4:
                try:
                    ids[key]["year"] = int(ids[key]["BIRT_DATE"][:4])
                    if min_year == -1 or min_year > ids[key]["year"]:
                        min_year = ids[key]["year"]
                    if max_year == -1 or max_year < ids[key]["year"]:
                        max_year = ids[key]["year"]
                except:
                    ids[key]["year"] = -1
            else:
                ids[key]["year"] = -1
        return (ids, lines, min_year, max_year)
    def get_children(self, persID):
        if persID == -1:
            return []
        self.cursor.execute("SELECT id FROM INDI WHERE father = " + str(persID) + " or mother = " + str(persID) + " ORDER BY BIRT_DATE DESC")
        list = []
        for row in self.cursor.fetchall():
            list.append(row[0])
        return list
    def get_conf_attribute(self, property):
        if self.config_name == None:
            config_name = "default"
        else:
            config_name = self.config_name

        query = "SELECT value FROM CONF WHERE config_name = '" + config_name + "' AND property = '" + property + "'"
        self.cursor_config.execute(query)
        for row in self.cursor_config.fetchall():
            return row[0]
        return None
    def get_config_name(self):
        if self.config_name != None:
            return self.config_name

        self.cursor_config.execute("SELECT DISTINCT config_name FROM CONF")
        rows = self.cursor_config.fetchall()
        if len(rows) == 0:    # table CONF is empty
            self.set_conf_defaults()
            return "my"
        elif len(rows) == 1:  # there is only one configuration, probably "default"
            self.set_conf_defaults()       # Result can be 2 or 3 configurations, because table will not be deleted
            return self.get_config_name()  # Take care, this is a RECURSION!
        elif len(rows) == 2:
            if rows[0][0] == "default":
                return rows[1][0]
            elif rows[1][0] == "default":
                return rows[0][0]
        
        # there are more than one "own" configurations, choose the correct one
        items = []
        for row in rows:
            if row[0] != "default":
                items.append(row[0])

        ok = False
        config_name, ok = QInputDialog.getItem(self.main, self.get_text("CHOICE_CONFIGURATION"), \
            self.get_text("CONFIGURATIONS"), items, 0, False)

        if ok and config_name:
            self.config_name = config_name
        else:
            self.config_name = items[0]

        self.main.refresh_configuration()
        return self.config_name
    def get_descendants(self, persID):
        ids = {}                       # each record includes: persID: { <table INDI>, partners (list), birth, death, year, child }
        lines = []                     # each record includes: boxLeft, boxRight
        min_year = -1
        max_year = -1
        if persID == -1:
            return (ids, lines, min_year, max_year)

        # sequence is important, therefore, add a helper array 
        helper = [{"id":persID}]
        while len(helper) > 0:
            key = helper[0]["id"]
            person = self.get_person(key)
            ids[key] = person
            ids[key]["children"]  = self.get_children(key)  # is list [] of children IDs
            ids[key]["partners"]  = self.get_partners_blood(key)
            ids[key]["birth"]     = self.main.get_date_line(ids[key]["BIRT_DATE"], ids[key]["BIRT_PLAC"], "*")
            ids[key]["death"]     = self.main.get_date_line(ids[key]["DEAT_DATE"], ids[key]["DEAT_PLAC"], "†")
            helper.pop(0)

            for child in ids[key]["children"]:
                helper.insert(0, {"id":child})
                lines.append({"boxLeft":child, "boxRight":key})  # sequence of boxes is important for line drawing

            # year of birth, min_year, max_year
            try:
                els = ids[key]["BIRT_DATE"].split(".")
                if len(els) >= 3:
                    y_int = int(els[2])
                else:
                    els = ids[key]["BIRT_DATE"].split("-")
                    if len(els) >= 3:
                        y_int = int(els[0])
                    else:
                        y_int = int(ids[key]["BIRT_DATE"])

                ids[key]["year"] = int(y_int)
                if min_year == -1 or min_year > ids[key]["year"]:
                    min_year = ids[key]["year"]
                if max_year == -1 or max_year < ids[key]["year"]:
                    max_year = ids[key]["year"]
            except:
                ids[key]["year"] = -1             

        cnt_old = -1
        cnt = 0
        while cnt_old != cnt:
            cnt_old = cnt
            cnt = 0
            for key in ids:
                if ids[key]["year"] == -1:
                    cnt = cnt + 1
                    if ids[key]["mother"] != -1 and ids[key]["mother"] in ids and ids[ids[key]["mother"]]["year"] != -1:
                        ids[key]["year"] = ids[ids[key]["mother"]]["year"] + 20  # assuming that the year of birth of child is 20 years after mother
                        cnt = cnt + 1
                    elif ids[key]["father"] != -1 and ids[key]["father"] in ids and ids[ids[key]["father"]]["year"] != -1:
                        ids[key]["year"] = ids[ids[key]["father"]]["year"] + 20
                        cnt = cnt + 1

        return (ids, lines, min_year, max_year)
    def get_fam_attribute(self, famID, attribute):
        if not self.cursor:
            return []
        
        self.cursor.execute("SELECT " + attribute + " FROM FAM WHERE id = " + str(famID))
        value = ""
        for row in self.cursor.fetchall():
            value = row[0]; 
            if not value: 
                value = ""
            # consider integer-type
            if attribute in ("WIFE", "HUSB"):
                if value in (None, "", 0) :
                    return -1
            break
        return value
    def get_family_ids_as_adult(self, persID):
        if not self.cursor:
            return []
        
        self.cursor.execute("SELECT id FROM FAM WHERE HUSB = " + str(persID) + " OR WIFE = " + str(persID) + " ORDER BY id ASC")
        famIDs = []
        for row in self.cursor.fetchall():
            famIDs.append(row[0])
        return famIDs
    def get_family_as_adult(self, persID):
        if not self.cursor:
            return []
        
        self.cursor.execute("SELECT * FROM FAM WHERE HUSB = " + str(persID) + " OR WIFE = " + str(persID))
        fam_rows = []
        for row in self.cursor.fetchall():
            fam_rows.append(row)

        objects = []
        for row in fam_rows:
            obj = {}
            obj["id"]         = row[0]
            obj["partnerID"]  = row[2] if row[1] == persID else row[1]
            if obj["partnerID"] in (None, "", 0):
                obj["partnerID"] = -1
                partner_str = "''"
            else:
                partner_str = str(obj["partnerID"])
            obj["date"]       = row[3]  # Marriage date
            obj["place"]      = row[4]  # Marriage place 
            obj["comment"]    = row[5]
            obj["childrenID"] = []

            sel_str = "SELECT id FROM INDI WHERE (father = " + str(persID) + " AND mother = " + partner_str + ") OR " \
                                                "(mother = " + str(persID) + " AND father = " + partner_str + ")"
            self.cursor.execute(sel_str)
            for id in self.cursor.fetchall():
                obj["childrenID"].append(id[0])

            objects.append(obj)
                              
        return objects
    def get_indi_attribute(self, persID, attribute):
        if persID == -1:
            if attribute in ("finished"):  # boolean
                return False
            elif attribute in ("father", "mother"):  # IDs
                return -1
            else:
                return ""

        self.cursor.execute("SELECT " + attribute + " FROM INDI WHERE id = " + str(persID))
        value = ""
        for row in self.cursor.fetchall():
            value = row[0]; 
            if not value: 
                value = ""
            # consider bool-type
            if attribute == "finished": 
                if value == "":
                    return False
                else:
                    return True
            # consider integer-type
            if attribute in ("father", "mother"):
                if value in (None, "", 0):
                    return -1
            break
        return value
    def get_marriage(self, persID, idx): 
        if persID in (None, "", 0, -1):
            return {}

        self.cursor.execute("SELECT * FROM FAM WHERE HUSB = " + str(persID) + " OR WIFE = " + str(persID) + " ORDER BY MARR_DATE")
        cnt = -1
        for row in self.cursor.fetchall():
            cnt = cnt + 1
            if cnt != idx:
                continue
            line = {}
            for i in range(len(self.fam_columns)):
                line[self.fam_columns[i][0]] = row[i]
            return line
        return {}
    def get_partners_blood(self, persID):                # Partner with same child
        self.cursor.execute("SELECT DISTINCT father, mother FROM INDI WHERE father = " + str(persID) + " or mother = " + str(persID) + " ORDER BY GIVN, SURN")
        list = []
        for row in self.cursor.fetchall():
            id = row[1] if row[0] == persID else row[0]
            list.append(id)
        return list
    def get_person(self, persID):
        self.cursor.execute("SELECT * FROM INDI WHERE id = " + str(persID))
        pers_dict = {}
        for row in self.cursor.fetchall():
            for i in range(len(self.indi_columns)):
                if row[i]:
                    pers_dict[self.indi_columns[i][0]] = row[i]
                else:
                    pers_dict[self.indi_columns[i][0]] = ""

                if self.indi_columns[i][0] in ("father", "mother"):
                    if pers_dict[self.indi_columns[i][0]] in (None, "", 0):
                        pers_dict[self.indi_columns[i][0]] = -1

                    if pers_dict[self.indi_columns[i][0]] != -1: # check, if person in DB
                        if not self.exists_person(pers_dict[self.indi_columns[i][0]]):
                            self.set_indi_attribute(persID, self.indi_columns[i][0], -1)
                            pers_dict[self.indi_columns[i][0]] = -1
        return pers_dict
    def get_person_for_table(self, persID):
        # List of key fields, which is used for the table #
        fields_str, fields, field_list = self.get_table_col_fields()
        self.cursor.execute("SELECT " + fields_str + " FROM INDI WHERE id = " + str(persID))
        line = []
        for row in self.cursor.fetchall():
            line = []
            i = -1
            for field_json in field_list:
                i = i + 1
                field = field_json.split(":")[0]
                if field in ("father", "mother"):
                    if row[i] in (None, 0, -1):
                        line.append("")
                    else:
                        line.append(row[i])
                else:
                    line.append(row[i])
        return line
    def get_persons_for_table(self):
        fields_str, _, field_list = self.get_table_col_fields()
        self.cursor.execute("SELECT " + fields_str + " FROM INDI ORDER BY id")
        lines = []        
        for row in self.cursor.fetchall():
            line = []
            i = -1
            for element in field_list:
                field = element.split(":")[0]
                i = i + 1
                if field in ("father", "mother"):
                    if row[i] in (None, 0, -1):
                        line.append("")
                    else:
                        line.append(row[i])
                elif field in ("BIRT_DATE", "DEAT_DATE"):
                    if not row[i]:
                        line.append("")
                    else:
                        els = row[i].split("-")
                        if len(els) >= 3:
                            if els[1] == '00' and els[2] == '00':
                                line.append(els[0])
                            else:
                                line.append(els[2] + "." + els[1] + "." + els[0])
                        elif len(els) == 1:  # no "-" in date
                            els = row[i].split(".")
                            if len(els) >= 3:
                                if els[0] == '00' and els[1] == '00':
                                    line.append(els[2])
                                else:
                                    line.append(els[0] + "." + els[1] + "." + els[2])
                            else:
                                line.append(row[i])
                        else:
                            line.append(row[i])
                else:
                    line.append(row[i])
            lines.append(line)
        return lines
    def get_person_strings_for_value_help(self, exclID, sexNot):
        self.cursor.execute("SELECT id FROM INDI WHERE SEX != '" + sexNot + "' AND id != " + str(exclID) + " ORDER BY GIVN, SURN")
        list = []
        for row in self.cursor.fetchall():
            persID = row[0]
            line = "ID "+ str(persID) + ": " + self.main.get_person_string(persID) 
            list.append(line)
        return list
    def get_project(self):
        if self.project in (None, ""):
            self.cursor_config.execute("SELECT value FROM CONF WHERE config_name = 'default' AND property = 'project'")
            for row in self.cursor_config.fetchall():
                self.project = row[0]
        return self.project
    def get_table_col_fields(self):
        fields = self.get_conf_attribute("table_columns")
        fields_str = ""
        field_list = fields.split(",")
        first = True
        for field_json in field_list:
            field = field_json.split(":")
            if first:
                fields_str = field[0]
                first = False
            else:
                fields_str = fields_str + "," + field[0]
        return (fields_str, fields, field_list)
    def get_table_col_number(self, fieldname):
        table_columns = self.get_conf_attribute("table_columns")
        field_list = table_columns.split(",")
        num = -1
        for field_json in field_list:
            num = num + 1
            field = field_json.split(":")[0]
            if field == fieldname:
                return num
        return -1
    def get_table_col_texts(self):
        table_columns = self.get_conf_attribute("table_columns")
        field_list = table_columns.split(",")
        txt_list = []
        for field_json in field_list:
            field = field_json.split(":")[1]
            field_txt = self.main.get_text(field)
            txt_list.append(field_txt)
        return txt_list
    def get_text(self, ID):
        query = "SELECT text FROM TEXT WHERE name = '" + ID + "' AND language = '" + self.language + "'"
        self.cursor_config.execute(query)
        for row in self.cursor_config.fetchall():
            return row[0]
    def import_data(self):
        # ----- Get Filename, which is to be imported ----- #
        fileDlg = QFileDialog()
        fileStruc = fileDlg.getOpenFileName( self.main, \
                self.get_text("CHOICE_IMPORT_FILE"), \
                "MyImport/", \
                "Gedcom CSV (*.csv);;(*.json)" #(*.ged);;Excel (*.xlsx);;Json (*.json)"
            )
        fileName = fileStruc[0]

        # Stop if nothing chosen
        if fileName == "":
            return

        # ----- Create new project ----- #
        if self.project not in (None, ""):
            self.main.clear_widgets()
        self.create_project()
        
        # ----- Process Data: convert Files to json ----- #
        if fileName:
            if fileName[-4:] == ".ged":
                self._convertDataFormatGedToJson(fileName)
            elif fileName[-4:] == ".csv":
                self.convert_data_format_csv_to_db(fileName)
            elif fileName[-5:] == ".json":
                self.convert_data_format_json_to_db(fileName)
            elif fileName[-5:] == ".xlsx":
                self._convertDataFormatXlsxToJson(fileName)
            else:
                QMessageBox.information(self.main, \
                    self.get_text("FILE_READ_ERROR"), \
                    self.get_text("FORMAT_NOT_IMPLEMENTED"), \
                    buttons=QMessageBox.Ok
                  )
                return
            
        # ----- Show Data in Table ----- #
        data = self.get_persons_for_table()
        if len(data) > 0:
            self.main.tableWidget.fill_table(data)
        else:
            self.widget.clear_widgets()

        QMessageBox.information(self.main, \
            self.get_text("CONVERSION_FINISHED"), \
            self.get_text("CONVERSION_SUCCESS"), \
            buttons=QMessageBox.Ok
        )
    def init_project(self):
        if self.project in (None, ""):
            self.set_empty_project()
        else:
            self.set_project(self.project)
    def on_exit(self):
        self.conn.close()
    def select_project(self):                            # asks for project from list of existing projects
        # Search for files in data subdirectory
        items = []
        if not os.path.exists(self.project_dir):
            os.makedirs(self.project_dir)

        files = os.listdir(self.project_dir)
        for file in files:
            if file.endswith(".db"):
                items.append(file.removesuffix(".db"))

        ok = False
        if len(items) == 0:
            project = self.create_project()
            ok = True
        else:
            project, ok = QInputDialog.getItem(self.main, self.get_text("CHOICE_PROJECT"), \
                self.get_text("PROJECTS"), items, 0, False)

        if ok and project:
            self.set_project(project)
    def set_conf_attribute(self, property, value):
        query = "UPDATE CONF SET value = '" + value + "' WHERE config_name = '" \
              + self.config_name + "' AND property = '" + property + "'"
        self.cursor_config.execute(query)
        self.conn_config.commit()

        if self.cursor_config.rowcount == 0:
            query = "INSERT INTO CONF (config_name, property, value) VALUES ('" \
                  + self.config_name + "', '" + property + "', '" + value + "')"
            self.cursor_config.execute(query)
            self.conn_config.commit()
    def set_conf_defaults(self):
        dict = {}
        dict["table_columns"] = 'id:ID,finished:DONE,' \
                    + 'SURN:LASTNAME,birthname:BORN,GIVN:FIRSTNAME,BIRT_DATE:BIRTH_DATE,' \
                    + 'BIRT_PLAC:BIRTH_PLACE,DEAT_DATE:DEATH_DATE,DEAT_PLAC:DEATH_PLACE,' \
                    + 'father:FATHER_ID,mother:MOTHER_ID,SEX:SEX,no_child:NO_CHILD,' \
                    + 'guess_birth:BIRTH_YEAR_ESTIMATED,guess_death:DEATH_YEAR_ESTIMATED'
        dict["language"] = "de"

        for property in dict:
            value = dict[property]
            query = """INSERT INTO CONF (config_name, property, value) """ \
                  + """VALUES ('default', '""" + property + """', '""" + str(value) + """') """\
                  + """ON CONFLICT (config_name, property) DO UPDATE SET value = excluded.value"""
            self.cursor_config.execute(query)

            query = """INSERT INTO CONF (config_name, property, value) """ \
                  + """VALUES ('my', '""" + property + """', '""" + str(value) + """') """\
                  + """ON CONFLICT (config_name, property) DO UPDATE SET value = excluded.value"""
            self.cursor_config.execute(query)

        self.conn_config.commit()
    def set_empty_project(self):
        self.set_conf_attribute("project", "")
        self.project = None
        self.conn    = None
        self.cursor  = None    
        self.main.setWindowTitle("Alva (" + self.get_text("NO_OPEN_PROJECT") + ")")  
        self.main.close_graphs()   # In case, graphs are open, windows are closed
        self.main.clear_widgets()  # Empty other Widgets
    def set_fam_attribute(self, famID, attribute, value):
        if famID == -1:
            return
        if attribute in ("HUSB", "WIFE"):
            self.cursor.execute("UPDATE FAM SET " + attribute + " = " + str(value) + " WHERE id = " + str(famID))
        else:
            self.cursor.execute("UPDATE FAM SET " + attribute + " = '" + value + "' WHERE id = " + str(famID))
        self.conn.commit()
    def set_indi_attribute(self, persID, attribute, value):
        if persID == -1:
            return
        # integer type #
        if attribute in ("father", "mother"):
            self.cursor.execute("UPDATE INDI SET " + attribute + " = "+ str(value) + " WHERE id = " + str(persID))
        # boolean type #
        elif attribute in ("finished", "guess_birth", "guess_death"):
            if value:
                self.cursor.execute("UPDATE INDI SET " + attribute + " = 'X' WHERE id = " + str(persID))
            else:
                self.cursor.execute("UPDATE INDI SET " + attribute + " = '' WHERE id = " + str(persID))
        # date conversion necessary
        elif attribute in ("BIRT_DATE", "DEAT_DATE"):
            elems = value.split(".")
            if len(elems) >= 3:
                dat = elems[2] + "-" + elems[1] + "-" + elems[0]
                self.cursor.execute("UPDATE INDI SET " + attribute + " = '" + dat +"' WHERE id = " + str(persID))
            else:
                self.cursor.execute("UPDATE INDI SET " + attribute + " = '" + value +"' WHERE id = " + str(persID))
        # text type #
        else:
            self.cursor.execute("UPDATE INDI SET " + attribute + " = '" + value +"' WHERE id = " + str(persID))
        self.conn.commit()
    def set_language(self):
        files = os.listdir(self.language_dir)
        list = []
        for file in files:
            list.append(file)
        list.sort()

        items = []
        for file in list:
            if file.startswith("i18n_") and file.endswith(".properties"):
                items.append(file[5:-11])
        
        language, ok = QInputDialog.getItem(self.main, self.get_text("CHOICE_LANGUAGE"), \
            self.get_text("LANGUAGES"), items, 0, False)    
        if ok:
            self.language = language
            self.fill_language_table()

            # Change text in shown controls and table header
            self.main.refresh_texts()

            # Store new language in config table
            self.set_conf_attribute("language", self.language)
    def set_project(self, project_name):
        self.project = project_name
        self.set_conf_attribute("project", self.project)

        # Create / enhance project database and tables, if necessary
        db_filename = self.project_dir + project_name + ".db"
        if not os.path.exists(db_filename):
            self.create_db(project_name)

        self.conn = sqlite3.connect(db_filename) 
        self.cursor = self.conn.cursor()
        self.check_db_structure()
    
        self.main.setWindowTitle("Alva -> " + self.get_text("PROJECT") + ' "' + project_name + '"')  

        # In case, graphs are open, windows are closed
        self.main.close_graphs()

        # Fill PersonListWidget (Table) from columns, which are actually shown
        data = self.get_persons_for_table()
        if len(data) > 0:
            self.main.fill_table(data)
            self.main.resize_table_columns()
            self.main.set_person(data[0][0])    # first person, always first value is "id"
        else:
            self.main.clear_widgets()
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
        return
    
        df = pandas.read_excel(fname, sheet_name="Taufen Alle", dtype=str)
        first = True
        
        self.main.add_status_message("Start Lesen der Daten aus der Excel-Datei")
        
        # Initialize File
        f = open(self.project, 'w', encoding='utf8')
        f.write("{\n\"INDI\":\n[\n")
        f.close()

        self.main.add_status_message("Ende Lesen der Daten aus der Excel-Datei, Beginn Verarbeitung")

        # Each Row in Excel File
        for i in range(df.Vorname._values.size):
            if str(df.ID._values[i]) == "nan":
                continue        
            if i % 100 == 0 and i > 0:
                self.main.add_status_message("Konvertiere " + str(i) + ". Person ")    
            
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
            f = open(self.config_dir, 'a', encoding='utf8')
            if first:
                first = False
            else:
                f.write(",\n")
            json.dump(obj, f, indent=4, ensure_ascii=False)
            f.close()
            
        self.main.add_status_message("Ende Verarbeitung Personen, Beginn Speicherung als json-Datei")

        # Close INDI Brackets, open FAM Brackets
        f = open(self.config_dir, 'a', encoding='utf8')
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
                self.main.add_status_message("Konvertiere " + str(i) + ". Ehe ")    
            
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
                        
            f = open(self.project, 'a', encoding='utf8')
            if first:
                first = False
            else:
                f.write(",\n")
            json.dump(obj, f, indent=4, ensure_ascii=False)
            f.close()
            
        # Close FAM Brackets
        f = open(self.config_dir, 'a', encoding='utf8')
        f.write("\n]\n}")
        f.close()

        self.main.add_status_message("Konvertierung abgeschlossen")

        return
    def _convertDataFormatGedToJson(self, fname):
        return

        # ----- Read Source File ----- #
        bytes = min(2048, os.path.getsize(fname))
        raw = open(fname, 'rb').read(bytes)
        result = chardet.detect(raw)
        encoding = result['encoding']
       
        f = open(fname, 'r', encoding=encoding)
        lines = f.readlines()
        f.close()
        
        # Start with empty file #
        f = open(..., 'w', encoding='utf8')
        f.close()

        cnt = 0
        tab = []
        first = True
        firstPrint = True
        obj = {}
        lastkey0 = ""
        newkey = ""

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
                for newkey in obj.keys():
                    break
    
                # braces, colons, new lines and indentation - magic ;o)
                f = open(..., 'a', encoding='utf8')
                if not firstPrint:
                    if lastkey0 != newkey:
                        f.write("\n    ],\n    \"" + newkey + "\":\n    [\n")
                    else:
                        f.write(",\n")
                else:
                    f.write("{\n    \"" + newkey + "\":\n    [\n")
                    firstPrint = False
                lastkey0 = newkey

                # write data from obj structure into file
                json.dump(obj[newkey], f, indent=4, ensure_ascii=False)
                f.close()
            elif level == 0:
                first = False

            tab.append({"level": level, "key": key, "value": value})

        # Once again after finishing the loop
        obj = self._runRecursion(tab)
        f = open(..., 'a', encoding='utf8')
        
        # braces, colons, new lines and indentation - magic ;o)
        for newkey in obj.keys(): break
        if lastkey0 != newkey:
            f.write("\n    ],\n    \"" + newkey + "\":\n    [\n")
        else:
            f.write(",\n")        

        # Write last Entity #
        json.dump(obj[newkey], f, indent=4, ensure_ascii=False)
        
        # Closing Brackets
        f.write("\n]\n}")
        f.close()
    def _convertDataFormatCsvToJson(self,file):
        return

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
            self.main.add_status_message("ID: " + person.get("id",""))
            if person.get("id","") == "": self.main.add_status_message( "FEHLER, keine ID")

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
            
        f = open(..., 'w', encoding='utf8')
        json.dump(jData, f, indent=4, ensure_ascii=False)
        f.close()
