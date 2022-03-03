"""  ____
    / __ \___  ____  ___  _________ ______
   / /_/ / _ \/ __ \/ _ \/ ___/ __ `/ ___/
  / _, _/  __/ / / /  __(__  ) /_/ (__  )
 /_/ |_|\___/_/ /_/\___/____/\__,_/____/
 ----------------------------------------
A one line summary of the module or program, terminated by a period.

Leave one blank line.  The rest of this docstring should contain an
overall description of the module or program.  Optionally, it may also
contain a brief description of exported classes and functions and/or usage
examples.

  Typical usage example:

  foo = ClassFoo()
  bar = foo.FunctionBar()
"""

from LibraryTemplate import LibraryTemplate
import numpy as np
import time
import sys

class Thermocouple(LibraryTemplate):
    """Summary of class here.

    Longer class information....
    Longer class information....

    Attributes:
        likes_spam: A boolean indicating if we like SPAM or not.
        eggs: An integer count of the eggs we have laid.
    """    
    def get_temperature(self, channel = 1):
        retval = sys.maxsize
        try:
            retval = float(self.connection.query(f"MEAS?{channel}"))
        except Exception as ex:
            print(f"Could not read temperature")
            try:
                retval = float(self.connection.query(f"MEAS?{channel}"))
            except Exception as ex:
                print(f"Could not read temperature")
        return retval
    
    # def get_temperature(self):
    #     return self.get_temperature()
    
    def get_temperature_2(self):
        return self.get_temperature(channel = 2)

    
    def setType(self, ch, mnem = "T"):
        self.connection.write(f"TTYP {ch},{mnem}")
        
    