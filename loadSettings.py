from pathlib import *  # For reading files
from sys import platform
import json


def getLegacySettings(setting):
    if setting == "clientID":
        if Path("clientID.txt").is_file():
            # Client ID found in legacy file
            contents = Path("clientID.txt").read_text()
            Path("clientID.txt").unlink()
            return contents
        else:
            return ""
    if setting == "hypervisors":
        if Path("hypervisors.txt").is_file():
            contents = Path("hypervisors.txt").read_text().casefold().split("\n")
            Path("hypervisors.txt").unlink()
            return contents
        else:
            return ""
    if setting == "largeImage":
        if Path("largeImage.txt").is_file():
            contents = Path("largeImage.txt").read_text()
            Path("largeImage.txt").unlink()
            return contents
        else:
            return ""
    if setting == "vmwarePath":
        if Path("vmwarePath.txt").is_file():
            contents = Path("vmwarePath.txt").read_text()
            Path("vmwarePath.txt").unlink()
            return contents
        else:
            return ""

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
    elif getLegacySettings("clientID"):
        # Client ID found in legacy file
        settings["clientID"] = getLegacySettings("clientID")
    else:
        # Prompt for ID
        settings["clientID"] = input("Enter client ID: ")

    hypervisors = []
    # Here, we look for VMware/Hyper-V in the settings. If it is found, we then check if the
    # enabled value exists and is set to false. If so, we skip it. If the enabled value is missing
    # or true, we enable it, and set it to true (this will set the value if it is not there). 
    # If VMware/Hyper-V is not in the settings, we do not enable it.
    if settings.get("vmware", {}).get("enabled", True):
        hypervisors.append("vmware")
        settings["vmware"]["enabled"] = True
    if settings.get("hyper-v", {}).get("enabled", True):
        hypervisors.append("hyper-v")
        settings["hyper-v"]["enabled"] = True
    # No hypervisors were found in the settings
    if hypervisors == []:
        if getLegacySettings("hypervisors"):
            # Hypervisors found in legacy file
            hypervisors = getLegacySettings("hypervisors")
            for hypervisor in hypervisors:
                if settings.get(hypervisor):
                    settings[hypervisor]["enabled"] = True
                else:
                    settings.update({hypervisor: {'enabled': True}})
        else:
            print("No hypervisors enabled! Exiting.")
            exit()
    
    if "vmware" in hypervisors:
        # Get path to VMware
        if platform.lower() == "win32":
            if settings.get("vmware", {}).get("path"):
                # VMware path found in settings.json and it's not blank (NoneType/blank strings == False)
                vmwarepath = settings.get("vmware").get("path")
            elif getLegacySettings("vmwarePath"):
                # VMware path found in legacy file
                vmwarepath = settings["vmware"]["path"] = getLegacySettings("vmwarePath");
            # Check default paths
            else:
                for path in ["C:/Program Files (x86)/VMware/VMware Workstation/vmrun.exe", "C:/Program Files/VMware/VMware Workstation/vmrun.exe"]:
                    if Path(path).is_file():
                        print("Using " + path + " as path.")
                        vmwarepath = settings["vmware"]["path"] = Path(path).as_posix()
                        break
                if path == "":
                    # Prompt for path
                    vmwarepath = settings["vmware"]["path"] = input("Enter path to VMware Workstation folder: ")
        else:
            # For non Windows OSes we assume vmrun is in the path
            vmwarepath = Path("vmrun")

    # Get large image key
    if settings.get("largeImage"):
        None
    elif getLegacySettings("largeImage"):
        # Large image key found in legacy file
        settings["largeImage"] = getLegacySettings("largeImage")
    else:
        # None found, ignore
        largeimage = None
    
    settingsPath = Path("settings.json")
    json.dump(settings, Path("settings.json").open(mode="w",), indent="\t")
    return settings, hypervisors, vmwarepath