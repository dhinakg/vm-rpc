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
        None
    elif Path("clientID.txt").is_file():
        # Client ID found in legacy file
        settings["clientID"] =  Path("clientID.txt").read_text()
    else:
        # Prompt for ID
        settings["clientID"] = input("Enter client ID: ")

    hypervisors = []
    if "vmware" in settings and settings.get("vmware").get("enabled", True):
        hypervisors.append("vmware")
    if "hyper-v" in settings and settings.get("hyper-v").get("enabled", True):
        hypervisors.append("hyper-v")
    if hypervisors == []:
        if Path("hypervisors.txt").is_file():
            # Client ID found in legacy file
            hypervisors = Path("hypervisors.txt").read_text()
            hypervisors = hypervisors.casefold().split("\n")
        else:
            settings.update({'vmware': {'enabled': True}, 'hyper-v': {'enabled': True}})