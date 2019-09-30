from pathlib import *  # For reading files


def loadSettings():
    # load JSON settings file
    if Path("settings.json").is_file() and Path("settings.json").stat().st_size != 0:
        # Settings file found
        settings = json.load(open("settings.json"))
    else:
        Path("settings.json").touch()
        settings = {}
    
    # Get client ID
    if settings.get("clientID"):
        # client ID found in settings.json and it's not blank (NoneType/blank strings == False)
        clientID = settings.get("clientID")
    elif Path("clientID.txt").is_file():
        # Client ID found in legacy file
        client_ID = Path("clientID.txt").read_text()
    else:
        # Prompt for ID
        clientID = input("Enter client ID: ")
        settings["clientID"] = clientID
