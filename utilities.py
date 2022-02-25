import pyvisa, os, time
import PySimpleGUI as sg


def create_run_folder(path_to_file):
    try:
        # Get the number of the last run, then create the next one
        files = os.listdir(path_to_file)
        maxNum = 0

        for f in files:
            # If the word run isn't in the name, move on
            if "run" not in f:
                continue

            lastNumber = [letter for letter in f if letter.isnumeric()]
            number = ''.join(lastNumber)
            number = int(number)
            if (number > maxNum):
                maxNum = number

        print("Creating folder " + str(maxNum + 1))
        os.mkdir(path_to_file + "/run" + str(maxNum + 1))
        os.mkdir(path_to_file + "/run" + str(maxNum + 1) + "/data")
        os.mkdir(path_to_file + "/run" + str(maxNum + 1) + "/pictures")
        return path_to_file + "/run" + str(maxNum + 1) + "/"

    except FileNotFoundError as ex:
        print("No folders found, creating the first run (run1)...")
        # If there is no folder, create the first one
        os.mkdir(path_to_file + "/run1")
        os.mkdir(path_to_file + "/run1/data")
        os.mkdir(path_to_file + "/run1/pictures")
        directory = path_to_file + "/run" + str(maxNum + 1) + "/"


def get_directory():
    currentDirectory = os.getcwd()
    # print(currentDirectory)

    try:
        f = open(currentDirectory + "/recentDirectories.txt", 'r+')

        # Create an empty list
        recentDirectories = []
        # Read all the lines into a temp list
        tempList = f.readlines()
        # Add all unique strings to list
        [recentDirectories.append(x) for x in tempList if x not in recentDirectories]

        # Create the GUI layout
        layout = [[sg.Listbox(values=recentDirectories, size=(70, 5), key="-LIST-", enable_events=True)],
                  [sg.Text("Choose a folder to save your data: ")],
                  [sg.FolderBrowse(key="-IN-")],
                  [sg.Button("OK")]]

        window = sg.Window('My File Browser', layout, size=(700, 500))

        while True:
            event, values = window.read()
            if event == "OK":
                if (values["-IN-"] == ""):
                    if (values['-LIST-']):
                        window.close()
                        return values['-LIST-'][0][:-1]
                    print("Please select a folder!")
                else:
                    window.close()
                    return values["-IN-"]
            if event == sg.WIN_CLOSED or event == "Exit":
                break

        f.close()
    except:
        layout = [
            [sg.Text("Choose a folder to save your data: ")],
            [sg.FolderBrowse(key="-IN-")],
            [sg.Button("OK")]]

        window = sg.Window('My File Browser', layout, size=(700, 500))

        while True:
            event, values = window.read()
            if event == "OK":
                if (values["-IN-"] == ""):
                    print("Please select a folder!")
                else:
                    window.close()
                    return values["-IN-"]
            if event == sg.WIN_CLOSED or event == "Exit":
                break

# Method which displays a countdown to the CLI
def countdown(t):

    while t:
        mins, secs = divmod(t, 60)
        timeformat = '{:02d}:{:02d}'.format(mins, secs)
        t -= 1
        if (t == 0):
            print(timeformat + " (Ctrl + C to end early)", end='\n')
        else:
            print(timeformat + " (Ctrl + C to end early)", end='\r')
        time.sleep(1)

def getAllLiveUnits():
    rm = pyvisa.ResourceManager()
    allResources = rm.list_resources() 

    for i in range(0, 33):
        print(str(i) + ": " , end = ' ')
        try:
            inst = rm.open_resource('GPIB0::' + str(i) + '::INSTR')
            print("Connected..", end = ' ')
            # inst.write("25C")
            print(inst.query("*IDN?")[:-1])

        except:
            print("NONE")

# getAllLiveUnits()

def stringToInt(string):
    lastNumber = [letter for letter in string if letter.isnumeric() or letter == "."]
    number = ''.join(lastNumber)
    return int(number)


def stringToFloat(string):
    lastNumber = [letter for letter in string if letter.isnumeric() or letter == "."]
    number = ''.join(lastNumber)
    return float(number)
