# Sources:
#   https://

# import os
from os.path import exists
import json

class Config():

    def __init__(self, main):
        super().__init__()
        self.main     = main
        
        self.jData = {}        
        self.filename = "config/config.json"
        
        if exists(self.filename):
            with open(self.filename, encoding="utf-8") as f:
                self.jData = json.load(f)
            f.close()

        # Check for needful Config-Data #
        if "currProject" not in self.jData:       # currProject
            self.jData["currProject"] = ""
        if "currProjectFile" not in self.jData:   # currProjectFile
            self.jData["currProjectFile"] = ""
        if "encoding" not in self.jData:          # encoding
            self.jData["encoding"] = "utf-8"
        if "personListFields" not in self.jData:  # personListFields
            self.jData["personListFields"] = {
                "id": "ID", 
                "NAME>SURN": "Nachname", 
                "NAME>GIVN": "Vorname", 
                "BIRT>DATE": "Geb. Datum", 
                "BIRT>PLAC": "Geb. Ort", 
                "DEAT>DATE": "Tod Datum", 
                "DEAT>PLAC": "Tod Ort" 
            }
        if "projectDir" not in self.jData:        # projectDir
            self.jData["projectDir"] = "data"
        if "persLog" not in self.jData:
            self.jData["persLog"] = "logs/pers.log"

    def onExit(self):
        # Called from main.py #
        f = open(self.filename, 'w', encoding='utf8')
        json.dump(self.jData, f, indent=4, ensure_ascii=False)
        f.close()
        
        exit()