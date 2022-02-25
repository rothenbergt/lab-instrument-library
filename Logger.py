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

