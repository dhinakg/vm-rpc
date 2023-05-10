from pypresence import Presence, DiscordError, exceptions, InvalidPipe # For rich presence
import subprocess # For running VMs
from datetime import datetime # For epoch time
from pathlib import * # For reading files
from vmware import vmware
from hyperv import hyperv
from virtualbox import virtualbox
from time import sleep
from sys import platform
import json

def clear():
    global epoch_time
    global STATUS
    global LASTSTATUS
    global running
    epoch_time = 0
    RPC.clear()
    STATUS = None
    LASTSTATUS = None
    if running == True:
        print("Stopped running VMs.")
        running = False
    return running

running = False

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

# get hypervisors
hypervisors = []
if "vmware" in settings and settings.get("vmware").get("enabled", True):
    hypervisors.append("vmware")
    settings["vmware"]["enabled"] = True
if "hyper-v" in settings and settings.get("hyper-v").get("enabled", True):
    hypervisors.append("hyper-v")
    settings["hyper-v"]["enabled"] = True
if "virtualbox" in settings and settings.get("virtualbox").get("enabled", True):
    hypervisors.append("virtualbox")
    settings["virtualbox"]["enabled"] = True
if hypervisors == []:
    if Path("hypervisors.txt").is_file():
        # Client ID found in legacy file
        hypervisors = Path("hypervisors.txt").read_text()
        hypervisors = hypervisors.casefold().split("\n")
    else:
        hypervisors = ["vmware", "hyper-v", "virtualbox"]
        settings.update({'vmware': {'enabled': True}, 'hyper-v': {'enabled': True}, 'virtualbox': {'enabled': True}})

if "vmware" in hypervisors:
    # Get path to VMware
    if platform.lower() == "win32":
        if "vmware" in settings and settings.get("vmware").get("path"):
            # VMware path found in settings.json and it's not blank (NoneType/blank strings == False)
            vmwarepath = settings.get("vmware").get("path")
        elif Path("vmwarePath.txt").is_file():
            # VMware path found in legacy file
            vmwarepath = Path("vmwarePath.txt").read_text()
            settings["vmware"]["path"] = vmwarepath
        elif Path("C:/Program Files (x86)/VMware/VMware Workstation/vmrun.exe").is_file():
            print("Using C:/Program Files (x86)/VMware/VMware Workstation as path.")
            vmwarepath = Path("C:/Program Files (x86)/VMware/VMware Workstation")
            settings["vmware"]["path"] = vmwarepath.as_posix()
        elif Path("C:/Program Files/VMware/VMware Workstation/vmrun.exe").is_file():
            print("Using C:/Program Files/VMware/VMware Workstation as path.")
            vmwarepath = Path("C:/Program Files/VMware/VMware Workstation")
            settings["vmware"]["path"] = vmwarepath.as_posix()
        else:
            # Prompt for path
            vmwarepath = input("Enter path to VMware Workstation folder: ")
            settings["vmware"]["path"] = vmwarepath
    else:
        vmwarepath = Path("vmrun")
if "virtualbox" in hypervisors:
    # Get path to VMware
    if platform.lower() == "win32":
        if "virtualbox" in settings and settings.get("virtualbox").get("path"):
            # VirtualBox path found in settings.json and it's not blank (NoneType/blank strings == False)
            virtualboxpath = settings.get("virtualbox").get("path")
        elif Path("virtualboxPath.txt").is_file():
            # VirtualBox path found in legacy file
            virtualboxpath = Path("virtualboxPath.txt").read_text()
            settings["virtualbox"]["path"] = virtualboxpath
        elif Path("C:/Program Files (x86)/Oracle/VirtualBox/VBoxManage.exe").is_file():
            print("Using C:/Program Files (x86)/Oracle/VirtualBox/ as path.")
            virtualboxpath = Path("C:/Program Files (x86)/Oracle/VirtualBox/")
            settings["virtualbox"]["path"] = virtualboxpath.as_posix()
        elif Path("C:/Program Files/Oracle/VirtualBox/VBoxManage.exe").is_file():
            print("Using C:/Program Files/Oracle/VirtualBox/ as path.")
            virtualboxpath = Path("C:/Program Files/Oracle/VirtualBox")
            settings["virtualbox"]["path"] = virtualboxpath.as_posix()
        else:
            # Prompt for path
            virtualboxpath = input("Enter path to VirtualBox folder: ")
            settings["virtualbox"]["path"] = virtualboxpath
    else:
        virtualboxpath = Path("vboxmanage")

# Get large image key
if settings.get("largeImage"):
    largeimage = settings.get("largeImage")
elif Path("largeImage.txt").is_file():
    # Large image key found in legacy file
    largeimage = Path("largeImage.txt").read_text()
    settings["largeImage"] = largeimage
else:
    # None found, ignore
    largeimage = None
# Get small image key
if settings.get("smallImage"):
    smallimage = settings.get("smallImage")
elif Path("smallImage.txt").is_file():
    # Small image key found in legacy file
    smallimage = Path("smallImage.txt").read_text()
    settings["smallImage"] = smallimage
else:
    # None found, ignore
    smallimage = None

settingsPath = Path("settings.json")
json.dump(settings, Path("settings.json").open(mode="w",), indent="\t")

if "vmware" in hypervisors:
    # Initialize VMware
    vmware = vmware(vmwarepath)

if "hyper-v" in hypervisors:
    # Initialize Hyper-V
    hyperv = hyperv()

if "virtualbox" in hypervisors:
    # Initialize VirtualBox
    virtualbox = virtualbox(virtualboxpath)

# Set up RPC
RPC = Presence(clientID)
try:
    RPC.connect()
except InvalidPipe:
    print("Waiting for Discord...")
    while True:
        try:
            RPC.connect()
            print("Connected to RPC.")
            break
        except InvalidPipe:
            pass
        sleep(5)
else:
    print("Connected to RPC.")
# RPC.connect()
# print("Connected to RPC.")
# Create last sent status so we don't spam Discord
LASTSTATUS = None
STATUS = None
# Set time to 0 to update on next change
epoch_time = 0

# Warning
print("Please note that Discord has a 15 second ratelimit in sending Rich Presence updates.")

# Run on a loop
while True:
    # Run vmrun list, capture output, and split it up
    STATUS = None
    if "vmware" in hypervisors:
        vmware.updateOutput()
        if vmware.isRunning() == False:
            # No VMs running, clear rich presence and set time to update on next change
            clear()
        elif vmware.runCount() > 1:
            running = True
            # Too many VMs to fit in field
            STATUS = "Running VMs"
            # Get VM count so we can show how many are running
            vmcount = [vmware.runCount(), vmware.runCount()]
            HYPERVISOR = "VMware"
        else:
            running = True
            # Init variable
            displayName = vmware.getRunningGuestName(0)
            STATUS = "Virtualizing " + displayName # Set status
            vmcount = None # Only 1 VM, so set vmcount to None
            HYPERVISOR = "VMware"
    if "hyper-v" in hypervisors:
        if hyperv.isFound() == False:
            print("Hyper-V either not supported, enabled, or found on this machine. Disabling Hyper-V for this session.")
            while "hyper-v" in hypervisors:
                hypervisors.remove("hyper-v")
            continue
        hyperv.updateRunningVMs()
        if hyperv.isRunning() == False:
            # No VMs running, clear rich presence and set time to update on next change
            clear()
        elif hyperv.runCount() > 1:
            running = True
            # Too many VMs to fit in field
            STATUS = "Running VMs"
            # Get VM count so we can show how many are running
            vmcount = [hyperv.runCount(), hyperv.runCount()]
            HYPERVISOR = "Hyper-V"
        else:
            running = True
            # Init variable
            displayName = hyperv.getRunningGuestName(0)
            STATUS = "Virtualizing " + displayName # Set status
            vmcount = None # Only 1 VM, so set vmcount to none
            HYPERVISOR = "Hyper-V"
    if "virtualbox" in hypervisors:
        virtualbox.updateOutput()
        if virtualbox.isRunning() == False:
            # No VMs running, clear rich presence and set time to update on next change
            clear()
        elif virtualbox.runCount() > 1:
            running = True
            # Too many VMs to fit in field
            STATUS = "Running VMs"
            # Get VM count so we can show how many are running
            vmcount = [virtualbox.runCount(), virtualbox.runCount()]
            HYPERVISOR = "VirtualBox"
        else:
            running = True
            # Init variable
            displayName = virtualbox.getRunningGuestName()
            STATUS = "Virtualizing " + displayName # Set status
            vmcount = None # Only 1 VM, so set vmcount to None
            HYPERVISOR = "VirtualBox"
    if STATUS != LASTSTATUS and STATUS != None: # To prevent spamming Discord, only update when something changes
        print("Rich presence updated locally; new rich presence is: " + STATUS + " (using " + HYPERVISOR + ")") # Report of status change, before ratelimit
        if epoch_time == 0: # Only change the time if we stopped running VMs before
            # Get epoch time
            if virtualbox.isRunning() and virtualbox.runCount() == 1:
                epoch_time = virtualbox.getVMuptime()
            else:
                now = datetime.utcnow()
                epoch_time = int((now - datetime(1970, 1, 1)).total_seconds())
        if largeimage == None:
            largetext = None
        else:
            largetext = "Check out vm-rpc by DhinakG on GitHub!"
        # The big RPC update
        RPC.update(state=STATUS,details="Running " + HYPERVISOR,small_image=smallimage,large_image=largeimage,small_text=HYPERVISOR,large_text=largetext,start=epoch_time,party_size=vmcount)
        LASTSTATUS = STATUS # Update last status to last status sent