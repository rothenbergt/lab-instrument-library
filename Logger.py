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


from datetime import datetime

class Logger:

    def __init__(self, directory):
        self.directory = directory

    def print(self, message):
        """
        Method which will log a message and print it to the screen
        """
        # Try to open the file
        try:
            f = open(self.directory + "log.txt", "a")
        # If the file doesnt exist, create one
        except FileNotFoundError as ex:
            print("No log.txt file found... Creating one")
            f = open('log.txt', 'w')
    
        
        if (type(message) != str):
            print(message)
        else: 
            print(datetime.now().strftime("%H:%M:%S") + ", " + message)
            f.write(datetime.now().strftime("%H:%M:%S") + ", " + message + "\n")
        f.close()


    def clear(self):
        """
        Method which will clear the current log.txt file
        """
        try:
            f = open('log.txt', 'w')
            f.close()
        except FileNotFoundError as ex:
            print("There is no log to clear")

