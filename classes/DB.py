# Sources:
#   GEDCOM-Format (de): http://www.daubnet.com/ftp/gedcom-551-deutsch.pdf
#   https://realpython.com/python-pyqt-database/

from types import MethodWrapperType
from PyQt5 import QtWidgets
from PyQt5.QtSql import QSqlDatabase, QSqlQuery

class DB():

    def __init__(self, *args):
        super(DB, self).__init__(*args)
        print("  Versuche, DB-Verbindung herzustellen")
        self.db = QSqlDatabase()

    def createConnection(self,fullname):
        if self.db.open():
            if self.db.databaseName() == fullname:
                return

        self.db.close()
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(fullname)

        if not self.db.open():
            print("  Fehler beim Aufbau der Datenbankverbindung")
            return False
        else:
            print("  Datenbankverbindung erfolgreich aufgebaut")

    def createDatabaseAndTables(self):
        query = QSqlQuery()

        # TODO: tables for all other main entities

        # ----- Personen-Tabelle ---------------------------------------------------------------- #
        qStr = """CREATE TABLE pers (
                id VARCHAR(22) PRIMARY KEY,
                surname VARCHAR(100),
                firstname VARCHAR(100),
                family VARCHAR(22),
                linkagetype VARCHAR(1),
                sex VARCHAR(1),
                birth_date VARCHAR(35),
                birth_place VARCHAR(90),
                death_date VARCHAR(35),
                death_place VARCHAR(90),
                comment_father TEXT,
                comment_Mother TEXT,
                comment TEXT
            )"""
        ret = query.exec_(qStr)

        if ret:
            print("  Ergebnis CREATE TABLE pers: ok")
        else:
            print("  Fehler bei CREATE TABLE pers: Fehler")
            print(query.lastError().databaseText())

        self.db.commit()

        # ----- Familie-Tabelle ----------------------------------------------------------------- #
        ret = query.exec_("""CREATE TABLE fam (
                id VARCHAR(22) PRIMARY KEY,
                marr_date VARCHAR(35),
                marr_place VARCHAR(90), 
                man VARCHAR(22),
                woman VARCHAR(22),
                children TEXT,
                comment_father TEXT,
                comment_mother TEXT,
                comment TEXT
            );""")

        if ret:
            print("  Ergebnis CREATE TABLE fam: ok")
        else:
            print("  Fehler bei CREATE TABLE: fam")

        self.db.commit()

        # ----- Events-Tabelle ------------------------------------------------------------------ #
        ret = query.exec_("""CREATE TABLE evt (
                id VARCHAR(22),
                evt_type VARCHAR(90),
                evt_date VARCHAR(35),
                place VARCHAR(90),
                place_id VARCHAR(10),
                reli VARCHAR(90)
            );""")

        if ret:
            print("  Ergebnis CREATE TABLE evt: ok")
        else:
            print("  Fehler bei CREATE TABLE: evt")

        self.db.commit()

        # ----- Places-Tabelle ------------------------------------------------------------------ #
        ret = query.exec_("""CREATE TABLE places (
                pl_id VARCHAR(10) PRIMARY KEY,
                hierarchy VARCHAR(120),
                longitude VARCHAR(12),
                latitude VARCHAR(12)
            );""")

        if ret:
            print("  Ergebnis CREATE TABLE places: ok")
        else:
            print("  Fehler bei CREATE TABLE: places")

        self.db.commit()

        # ----- Tags-Tabelle -------------------------------------------------------------------- #
        # Note: id is implicitely autincremented when it is primary key
        ret = query.exec_("""CREATE TABLE details (
                obj  VARCHAR(4),
                oType VARCHAR(22),
                oJson VARCHAR(1000)
            );""")

        if ret:
            print("  Ergebnis CREATE TABLE details: ok")
        else:
            print("  Fehler bei CREATE TABLE: details")

        self.db.commit()

    def insertPerson( self, id, surname, firstname, family, linkagetype, sex, birthDate, 
                      birthPlace, deathDate, deathPlace, comment, commentFather, commentMother):
        query = QSqlQuery()
        
        comment       = comment.replace("'", "''")
        commentFather = commentFather.replace("'", "''")
        commentMother = commentMother.replace("'", "''")
        
        qStr = "INSERT INTO pers values('" \
                    + id + "', '" \
                    + surname + "', '" \
                    + firstname + "', '" \
                    + family + "', '" \
                    + linkagetype + "', '" \
                    + sex + "', '" \
                    + birthDate + "', '" \
                    + birthPlace + "', '" \
                    + deathDate + "', '"\
                    + deathPlace + "', '" \
                    + comment + "', '" \
                    + commentFather + "', '" \
                    + commentMother + "')"
        ret = query.exec_(qStr)
        if not ret: 
            print("  Fehler Insert Person: " + qStr)
            print("  " + query.lastError().text())
        self.db.commit()

    def insertFamily(self, id, marrDate, marrPlace, man, woman, children, commentFather, commentMother, comment):
        query = QSqlQuery()
        qStr = "INSERT INTO fam values('" + id + "', '" + marrDate + "', '" + marrPlace + "', '" \
                       + man + "', '" + woman + "', '" + children + "', '" + commentFather + "', '" \
                       + commentMother + "', '" + comment + "')"
        ret = query.exec_(qStr)
        if not ret: 
            print("Fehler Insert Familie: " + qStr)
        self.db.commit()

    def insertEvent(self, event):
        # print("DB.insertEvent() - empty")

        evt_date = ""
        place = ""
        religion = ""

        if "evt_date" in event.keys(): evt_date = event["evt_date"]        
        if "place"    in event.keys(): place    = event["place"]
        if "religion" in event.keys(): religion = event["religion"]

        if "id" not in event.keys(): 
            print(event); 
            return

        query = QSqlQuery()
        qStr = "INSERT INTO evt values('" + event["id"] + "', '" + event["evt_type"] \
                                        + "', '" + evt_date + "', '" + place + "', '', '" \
                                        + religion + "')"

        ret = query.exec_(qStr)
        if not ret: 
            print("Fehler Insert Event: " + qStr)
        self.db.commit()

        if event["evt_type"] == "BIRT":
            if evt_date != "":
                self.updateTable("pers", event["id"], "birth_date", evt_date)
            if place != "":
                self.updateTable("pers", event["id"], "birth_place", place)

        if event["evt_type"] == "DEAT":
            if evt_date != "":
                self.updateTable("pers", event["id"], "death_date", evt_date)
            if place != "":
                self.updateTable("pers", event["id"], "death_place", place)

    def insertDetail(self, key, oType, oJson):
        query = QSqlQuery()
        qStr = "INSERT INTO details VALUES (" + "'" + key + "', '" + oType + "', '" + oJson + "')"
        ret = query.exec_(qStr)
        if not ret: 
            print("  Fehler Insert Detail: " + qStr)
            print("  " + query.lastError().text())
        self.db.commit()        

    def updateTable(self, tabName, id, field, value):
        query = QSqlQuery()
        qStr = "UPDATE " + tabName + " SET " + field + " = '" + value + "' WHERE id = '" + id + "'"
        ret = query.exec_(qStr)
        if not ret: 
            print("  Fehler Update: " + qStr)
        self.db.commit()

    def selectPersonList(self,fieldArr):
        query = QSqlQuery()

        # Build Select String from FieldArr
        qStr = "SELECT " + ", ".join(fieldArr) + " FROM pers"
        ret = query.exec_(qStr)

        if not ret: 
            print("  Fehler Select Person List: " + qStr)
            return

        # query.first()
        data = []
        while query.next():
            line = []
            for i in range(len(fieldArr)):
                line.append(query.value(i))
            data.append(line)
        
        return data

    def selectPersonWithFields(self, id, fieldArr):
        query = QSqlQuery()

        # Build Select String from FieldArr
        qStr = "SELECT " + ", ".join(fieldArr) + " FROM pers WHERE id = '" + id + "'"
        ret = query.exec_(qStr)

        if not ret: 
            print("  Fehler Select Person with Fields: " + qStr)
            return

        while query.next():
            line = []
            for i in range(len(fieldArr)):
                line.append(query.value(i))
        
        return line

    def selectPerson(self,id):
        # print("DB.selectPerson(" + str(id) + ")")
        # if no id is given (id == ""), then an empty pers structure is expected

        query = QSqlQuery()
        pers = {}
        pers["id"]          = id
        pers["surname"]     = ""
        pers["firstname"]   = ""
        pers["family"]      = ""
        pers["linkagetype"] = ""
        pers["father"]      = ""
        pers["fatherId"]    = ""
        pers["mother"]      = ""
        pers["motherId"]    = ""
        pers["raw"]         = ""

        # Build Select String for table pers
        qStr = "SELECT * FROM pers WHERE id = '" + str(id) + "'"
        ret = query.exec_(qStr)

        if not ret: 
            print("  Fehler Select Person: " + qStr)
            return

        while query.next():
            pers["id"]          = query.value(0)
            pers["surname"]     = query.value(1)
            pers["firstname"]   = query.value(2)
            pers["family"]      = query.value(3)
            pers["linkagetype"] = query.value(4)

        # Build Select String for table fam
        if pers["family"] != "":
            qStr = "SELECT man, woman, p1.surname, p1.firstname, p2.surname, p2.firstname FROM fam " \
                 + "LEFT OUTER JOIN pers AS p1 ON p1.id = fam.man " \
                 + "LEFT OUTER JOIN pers AS p2 ON p2.id = fam.woman " \
                 + "WHERE fam.id = '" + str(pers["family"]) + "'"
            ret = query.exec_(qStr)

            if not ret: 
                print("  Fehler Select Familie: " + qStr)

            while query.next():
                pers["father"] = query.value(3) + " " + query.value(2)
                pers["fatherId"] = query.value(0)
                pers["mother"] = query.value(5) + " " + query.value(4)
                pers["motherId"] = query.value(1)

        # Build Select String for ged-details
        qStr = "SELECT * FROM details WHERE oType ='INDI' AND obj = '" + str(id) + "'"
        ret = query.exec_(qStr)

        if not ret: 
            print("  Fehler Select Details: " + qStr)
    
        while query.next():
            cnt = 2
            pers["raw"] = query.value(cnt)

        return pers

    def getParentsOfPerson(sef, id):
        #print("DB.selectParents(" + str(id) + ")")

        query   = QSqlQuery()
        family  = ""
        parents = []

        # Build Select String for table pers
        qStr = "SELECT family FROM pers WHERE id = '" + str(id) + "'"
        ret = query.exec_(qStr)

        if not ret: 
            print("  Fehler Select Familie: " + qStr)
            return

        while query.next():
            family = query.value(0)

        # Build Select String for table fam
        if family == "":
            return []

        qStr = "SELECT man, woman FROM fam WHERE id = '" + str(family) + "'"
        ret = query.exec_(qStr)

        if not ret: 
            print("  Fehler Select Eltern: " + qStr)
            return []

        while query.next():
            if query.value(0) != "":
                parents.append(query.value(0))
            if query.value(1) != "":
                parents.append(query.value(1))

        return parents

    def getSex(self,id):
        #print("DB.getSex(" + str(id) + ")")

        query = QSqlQuery()
        sex = ""

        # Build Select String for table pers
        qStr = "SELECT sex FROM pers WHERE id = '" + str(id) + "'"
        ret = query.exec_(qStr)

        if not ret: 
            print("  Fehler Select Geschlecht: " + qStr)
            return

        while query.next():
            sex = query.value(0)

        if sex == "M" or sex == "m":
            sex = "m" # man
        else:
            sex = "w" # woman

        return sex

    def getPersonName(self,id):
        query = QSqlQuery()
        names = {"firstname": "", "surname": ""}

        # Build Select String for table pers
        qStr = "SELECT firstname, surname FROM pers WHERE id = '" + str(id) + "'"
        ret = query.exec_(qStr)

        if not ret: 
            print("  Fehler Select Name: " + qStr)
            return

        while query.next():
            if query.value(0) != "":
                names["firstname"] = query.value(0)
            if query.value(1) != "":
                names["surname"] = query.value(1)

        return names

    def getBirthData(self,id):
        query = QSqlQuery()
        birth = {"birth_date": "", "birth_place": ""}

        # Build Select String for table pers
        qStr = "SELECT birth_date, birth_place FROM pers WHERE id = '" + str(id) + "'"
        ret = query.exec_(qStr)

        if not ret: 
            print("  Fehler Select Birth: " + qStr)
            return

        while query.next():
            # print(" QUERY:" + str(query.value(0)) + " - " + str(query.value(1)))
            if query.value(0) != "":
                birth["birth_date"] = query.value(0)
            if query.value(1) != "":
                birth["birth_place"]=query.value(1)

        return birth
    
    def getDeathData(self,id):
        query = QSqlQuery()
        death = {"death_date": "", "death_place": ""}

        # Build Select String for table pers
        qStr = "SELECT death_date, death_place FROM pers WHERE id = '" + str(id) + "'"
        ret = query.exec_(qStr)

        if not ret: 
            print("  Fehler Select Death: " + qStr)
            return

        while query.next():
            if query.value(0) != "":
                death["death_date"]=query.value(0)
            if query.value(1) != "":
                death["death_place"]=query.value(1)

        return death

    def getMarriage(self, fam_id):
        query = QSqlQuery()
        marr = {"id": "", "evt_date": "", "place": ""}

        # Build Select String for table pers
        qStr = "SELECT id, evt_date, place FROM evt WHERE id = '" + str(fam_id) + "' AND evt_type = 'MARR'"
        ret = query.exec_(qStr)

        if not ret: 
            print("  Fehler Select Marriage: " + qStr)
            return

        while query.next():
            marr["id"] = fam_id
            marr["evt_date"] = query.value(1)
            marr["place"] = query.value(2)

        return marr
    
    def getChildrenOfPerson(self,id):
        #print("DB.selectParents(" + str(id) + ")")
        # TODO: Das mit den Halbgeschwistern passt noch nicht ganz in der Grafik, siehe Cosima

        query = QSqlQuery()
        children = []
        fams = []

        # Build Select String for table pers
        qStr = "SELECT id FROM fam WHERE man = '" + str(id) + "' OR woman = '" + str(id) + "'"
        ret = query.exec_(qStr)

        if not ret: 
            print("  Fehler Select Familie: " + qStr)
            return

        while query.next():
            fams.append(query.value(0))

        # Build Select String for table pers
        for fam in fams:
            qStr2 = "SELECT id FROM pers WHERE family = '" + str(fam) + "'"
            ret2 = query.exec_(qStr2)

            if not ret2: 
                print("  Fehler Select Kinder: " + qStr)
                return

            while query.next():
                children.append(query.value(0))

        return children

    def getPartners(self,id):
        query    = QSqlQuery()
        query2   = QSqlQuery()
        partners = []

        # Build Select String for table pers
        qStr = "SELECT id, man, woman FROM fam WHERE man = '" + str(id) + "' OR woman = '" + str(id) + "'"
        ret = query.exec_(qStr)

        if not ret: 
            print("  Fehler Select Partner: " + qStr)
            return

        while query.next():
            famid = query.value(0)
            man   = query.value(1)
            woman = query.value(2)
            
            # Build Select String for table pers
            if man == id:
                qStr2 = "SELECT sex FROM pers WHERE id = '" + str(woman) + "'"
            else:
                qStr2 = "SELECT sex FROM pers WHERE id = '" + str(man) + "'"
            ret2 = query2.exec_(qStr2)

            if not ret2: 
                print("  Fehler Select Partner: " + qStr2)
                return

            while query2.next():
                if query2.value(0) == "M" or query2.value(0) == "m":
                    sex = "m"
                else:
                    sex = "w"
                
                if man == id:
                    partners.append({"fam_id": famid, "id": woman, "sex": sex})
                else:
                    partners.append({"fam_id": famid, "id": man, "sex": sex})

        return partners

    def getNextPersonId(self):
        query = QSqlQuery()
        num = 0
        pattern = ""
        retval = ""

        # Build Select String for table pers
        qStr = "SELECT min(id), max(id) FROM pers"
        ret = query.exec_(qStr)

        if not ret: 
            print("  Fehler Select MAX(id): " + qStr)
            return "1"

        while query.next():
            min = query.value(0) #sample: @I500002@
            max = query.value(1) #sample: @I500186@
            max_save = max
            # Check, if there is a pattern
            while True:
                if len(min) <= 0 or len(max) <= 0:
                    break

                min_l = min[:1]
                min   = min[1:]
                max_l = max[:1]
                max   = max[1:]

                if min_l == max_l:
                    if min_l.isnumeric():
                        pattern = pattern + "z"
                    else:
                        pattern = pattern + str(min_l)
                else:
                    if min_l.isnumeric() and max_l.isnumeric():
                        pattern = pattern + "z"
                    else:
                        pattern = pattern + "."
        
        # if there are only "z" and constant signs included in pattern, then count numeric
        if pattern.find(".") >= 0:
            # if there are "." included in pattern, then count alphanumeric
            print("With . Not yet implemented in DB.getNextPersonId()")
            # TODO
            retval = pattern # nonsense!
        else:
            max = max_save
            cnt = 0
            while True:
                if len(max) <= cnt:
                    break
                
                if pattern[cnt:cnt+1] == "z":
                    num = 10 * num + int(max[cnt:cnt+1])
                cnt = cnt + 1

            num = num + 1
            nums = str(num)
            cnt = 0
            while True:
                if len(max) <= cnt:
                    break

                if pattern[cnt:cnt+1] == "z":
                    retval  = retval + nums[:1]
                    nums = nums[1:]
                else:
                    retval = retval + pattern[cnt:cnt+1]
                cnt = cnt + 1

            if nums != "":
                retval  = retval + nums

        return retval
