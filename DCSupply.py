#     ____
#    / __ \___  ____  ___  _________ ______
#   / /_/ / _ \/ __ \/ _ \/ ___/ __ `/ ___/
#  / _, _/  __/ / / /  __(__  ) /_/ (__  )
# /_/ |_|\___/_/ /_/\___/____/\__,_/____/
# ----------------------------------------


from LibraryTemplate import LibraryTemplate
from typing import List
import inspect

class E3649A(LibraryTemplate):
    

    def getVoltage(self):
        retval = self.connection.query(f"MEASure:VOLTage:DC?")
        return float(retval)

    def getCurrent(self):
        retval = self.connection.query(f"MEASure:CURRent:DC?")
        return float(retval)

    def setVoltage(self, voltage):
        self.connection.write(f"VOLT {voltage}")

# s = E3649A("GPIB::05::INSTR")
# print(s.getCurrent())

# s.setVoltage(5)