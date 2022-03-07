# Sources:
#   https://


class Config():

    def __init__(self, main):
        super().__init__()
        self.main     = main
        self.filename = "config/config.txt"
        self.DB       = ""  # Values at Start, no update later

        # ToDo: If file is not available or points to a too old database, then
        # the report would not start => in this case empty the database preselection
        # and/or renew the file

        f = open(self.filename, 'r')

        while True: # file could be opened
            # Get next line from file
            line = f.readline()

            if not line: # end of file
                break
            
            parts = line.split(" = ", 2)

            if len(parts) > 1:
                if parts[0] == "lastDB":
                    self.DB = parts[1]

        f.close()

    def onExit(self):
        f = open(self.filename, 'w')
        f.write("lastDB = " + self.main.data.projName)
        f.close()
        exit(self)
