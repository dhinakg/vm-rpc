hypervisors = ["vmware", ""] # supported values are "hyper-v" and "vmware"

from pypresence import Presence, DiscordError, exceptions, InvalidPipe # For rich presence
import subprocess # For running VMs
from datetime import datetime # For epoch time
from pathlib import Path, PurePath, PureWindowsPath # For reading files
from vmware import vmware
from hyperv import hyperv
from time import sleep
# get Client ID
if Path("clientID.txt").is_file():
    # Client ID found in file
    client_ID = Path("clientID.txt").read_text()
else:
    # Prompt for ID
    client_ID = input("Enter client ID: ")

# get hypervisors
if Path("hypervisors.txt").is_file():
    # Client ID found in file
    hypervisors = Path("hypervisors.txt").read_text()
    hypervisors = hypervisors.casefold().split("\n")
else:
    hypervisors = ["vmware", "hyper-v"]

if "vmware" in hypervisors:
    # Get path to VMware
    if Path("vmwarePath.txt").is_file():
        # VMware path found in file
        vmwarepath = Path("vmwarePath.txt").read_text()
    else:
        # Prompt for path
        vmwarepath = input("Enter path to VMware Workstation folder: ")

# Get large image key
if Path("largeImage.txt").is_file():
    # Large image key found
    largeimage = Path("largeImage.txt").read_text()
else:
    # None found, ignore
    largeimage = None

if "vmware" in hypervisors:
    # Initialize VMware
    vmware = vmware(vmwarepath)

if "hyper-v" in hypervisors:
    # Initialize Hyper-V
    hyperv = hyperv()

# Set up RPC
RPC = Presence(client_ID)
try:
    RPC.connect()
except InvalidPipe:
    print("Waiting for Discord...")
    while True:
        try:
            RPC.connect()
            print("Connected to RPC.")
            break
        except:
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
            epoch_time = 0
            RPC.clear()
            STATUS = None
            LASTSTATUS = None
        elif vmware.runCount() > 1:
            # Too many VMs to fit in field
            STATUS = "Running VMs"
            # Get VM count so we can show how many are running
            vmcount = [vmware.runCount(), vmware.runCount()]
            HYPERVISOR = "Running VMware"
        else:
            # Init variable
            displayName = vmware.getRunningGuestName(0)
            STATUS = "Virtualizing " + displayName # Set status
            vmcount = None # Only 1 VM, so set vmcount to None
            HYPERVISOR = "Running VMware"
    if "hyper-v" in hypervisors:
        hyperv.updateRunningVMs()
        if hyperv.isRunning() == False:
            # No VMs running, clear rich presence and set time to update on next change
            epoch_time = 0
            RPC.clear()
            STATUS = None
            LASTSTATUS = None
        elif hyperv.runCount() > 1:
            # Too many VMs to fit in field
            STATUS = "Running VMs"
            # Get VM count so we can show how many are running
            vmcount = [hyperv.runCount(), hyperv.runCount()]
            HYPERVISOR = "Running Hyper-V"
        else:
            # Init variable
            displayName = hyperv.getRunningGuestName(0)
            STATUS = "Virtualizing " + displayName # Set status
            vmcount = None # Only 1 VM, so set vmcount to none
            HYPERVISOR = "Hyper-V"
    if STATUS != LASTSTATUS and STATUS != None: # To prevent spamming Discord, only update when something changes
        print("Rich presence updated locally; new rich presence is: " + STATUS + " (using " + HYPERVISOR) # Report of status change, before ratelimit
        if epoch_time == 0: # Only change the time if we stopped running VMs before
            # Get epoch time
            now = datetime.utcnow()
            epoch_time = int((now - datetime(1970, 1, 1)).total_seconds())
        if largeimage == None:
            largetext = None
        else:
            largetext = "Check out vm-rpc by DhinakG on GitHub!"
        # The big RPC update
        RPC.update(state=STATUS,details=HYPERVISOR,large_image=largeimage,large_text=largetext,start=epoch_time,party_size=vmcount)
        LASTSTATUS = STATUS # Update last status to last status sent