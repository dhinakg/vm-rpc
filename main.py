from pypresence.presence import Presence
from pypresence import InvalidPipe
from time import sleep 
from pathlib import Path
from vmware import vmware
from hyperv import hyperv
from virtualbox import virtualbox
from datetime import datetime, UTC
from sys import platform
import json

def clear() -> None:
    global epoch_time, STATUS, LASTSTATUS, running
    epoch_time = 0
    RPC.clear()
    STATUS = None
    LASTSTATUS = None
    if running:
        print("Stopped running VMs.")
        running = False
    return running

running = False

# Load JSON settings file
if Path("settings.json").is_file() and Path("settings.json").stat().st_size != 0:
    # Settings file found
    with open("settings.json", encoding="utf-8") as f:
        settings = json.load(f)
else:
    Path("settings.json").touch()
    settings = {}

# Get client ID
if settings.get("clientID"):
    # client ID found in settings.json and it's not blank (NoneType/blank strings == False)
    client_id = settings.get("clientID")
elif Path("clientID.txt").is_file():
    # Client ID found in legacy file
    client_id = Path("clientID.txt").read_text(encoding="utf-8")
else:
    # Prompt for ID
    client_id = input("Enter client ID: ")
    settings["clientID"] = client_id

# get hypervisors
hypervisors = []
if "vmware" in settings and settings["vmware"].get("enabled", True):
    hypervisors.append("vmware")
    settings["vmware"]["enabled"] = True
if "hyper-v" in settings and settings["hyper-v"].get("enabled", True):
    hypervisors.append("hyper-v")
    settings["hyper-v"]["enabled"] = True
if "virtualbox" in settings and settings["virtualbox"].get("enabled", True):
    hypervisors.append("virtualbox")
    settings["virtualbox"]["enabled"] = True
if not hypervisors:
    if Path("hypervisors.txt").is_file():
        # Client ID found in legacy file
        hypervisors = Path("hypervisors.txt").read_text(encoding="utf-8")
        hypervisors = hypervisors.casefold().split("\n")
    else:
        hypervisors = ["vmware", "hyper-v", "virtualbox"]
        settings.update({'vmware': {'enabled': True}, 'hyper-v': {'enabled': True}, 'virtualbox': {'enabled': True}})

if "vmware" in hypervisors:
    # Get path to VMware
    if platform.lower() == "win32":
        if "vmware" in settings and settings["vmware"].get("path"):
            # VMware path found in settings.json and it's not blank (NoneType/blank strings == False)
            vmwarepath = settings["vmware"].get("path")
        elif Path("vmwarePath.txt").is_file():
            # VMware path found in legacy file
            vmwarepath = Path("vmwarePath.txt").read_text(encoding="utf-8")
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
    # Get path to VirtualBox
    if platform.lower() == "win32":
        if "virtualbox" in settings and settings["virtualbox"].get("path"):
            # VirtualBox path found in settings.json and it's not blank (NoneType/blank strings == False)
            virtualboxpath = settings["virtualbox"].get("path")
        elif Path("C:/Program Files/Oracle/VirtualBox/VBoxManage.exe").is_file():
            print("Using C:/Program Files/Oracle/VirtualBox/ as path.")
            virtualboxpath = Path("C:/Program Files/Oracle/VirtualBox/")
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
    largeimage = Path("largeImage.txt").read_text(encoding="utf-8")
    settings["largeImage"] = largeimage
else:
    # None found, ignore
    largeimage = None
# Get small image key
smallimage = settings.get("smallImage")

with open("settings.json", "w", encoding="utf-8") as f:
    json.dump(settings, f, indent="\t")

if "vmware" in hypervisors:
    # Initialize VMware
    vmware = vmware(str(vmwarepath))

if "hyper-v" in hypervisors:
    # Initialize Hyper-V
    hyperv = hyperv()
if "virtualbox" in hypervisors:
    # Initialize VirtualBox
    virtualbox = virtualbox(str(virtualboxpath))

# Set up RPC
RPC = Presence(client_id)
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
    vmcount = None

    for hv_name in hypervisors:
        if hv_name == "vmware":
            hv = vmware
            hv.updateOutput()
        elif hv_name == "hyper-v":
            hv = hyperv
            if not hv.isFound():
                print("Hyper-V either not supported, enabled, or found on this machine. Disabling Hyper-V for this session.")
                while "hyper-v" in hypervisors:
                    hypervisors.remove("hyper-v")
                continue
            hv.updateRunningVMs()
        elif hv_name == "virtualbox":
            hv = virtualbox
            hv.updateOutput()
        else:
            continue
        
        HYPERVISOR = "VMware" if hv_name == "vmware" else "VirtualBox" if hv_name == "virtualbox" else "Hyper-V"
        if hv.runCount() <= 0:
            continue
        if hv.runCount() > 1:
            running = True
            # Too many VMs to fit in field
            STATUS = "Running VMs"
            # Get VM count so we can show how many are running
            vmcount = [hv.runCount(), hv.runCount()]
        else:
            running = True
            # Init variable
            displayName = hv.getRunningGuestName(0)
            STATUS = "Virtualizing " + displayName # Set status
            vmcount = None # Only 1 VM, so set vmcount to none
        break  # Stop checking since a HV has VMs running
    if STATUS is None:
        clear()
    if STATUS != LASTSTATUS and STATUS is not None: # To prevent spamming Discord, only update when something changes
        print(f"Rich presence updated locally; new rich presence is: {STATUS} (using {HYPERVISOR})") # Report of status change, before ratelimit
        if "virtualbox" in hypervisors and virtualbox.isRunning() and virtualbox.runCount() == 1: # Check if VirtualBox is in use
            epoch_time = virtualbox.getVMuptime(0)
        elif epoch_time == 0: # Only change the time if we stopped running VMs before
            # Get epoch time
            now = datetime.now(UTC)
            epoch_time = int((now - datetime(1970, 1, 1, tzinfo=UTC)).total_seconds())
        if largeimage is None:
            largetext = None
        else:
            largetext = "Check out vm-rpc by DhinakG on GitHub!"
        # The big RPC update
        RPC.update(
            state=STATUS,
            details=f"Running {HYPERVISOR}",
            small_image=smallimage,
            large_image=largeimage,
            small_text=HYPERVISOR,
            large_text=largetext,
            start=epoch_time,
            party_size=vmcount
        )
        LASTSTATUS = STATUS # Update last status to last status sent
    sleep(1)
