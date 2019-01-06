from pypresence import Presence # For rich presence
import subprocess # For running VMs
from datetime import datetime # For epoch time
from pathlib import Path, PurePath, PureWindowsPath # For reading files

# get Client ID
if Path("clientID.txt").is_file():
    # Client ID found in file
    client_ID = Path("clientID.txt").read_text()
else:
    # Prompt for ID
    client_ID = input("Enter client ID: ")

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

# Remove quotes from path if necessary
vmwarepath = vmwarepath.replace("\"", "")
vmwarepath = vmwarepath.replace("\'", "")

vmrunpath = Path(vmwarepath).joinpath("vmrun.exe") # Create the path to vmrun

COMMAND = "list" # Static command to run


# Set up RPC
RPC = Presence(client_ID)
RPC.connect()
print("Connected to RPC.")
# Create last sent status so we don't spam Discord
LASTSTATUS = ""
# Set time to 0 to update on next change
epoch_time = 0

# Warning
print("Please note that Discord has a 15 second ratelimit in sending Rich Presence updates.")

# Run on a loop
while True:
    # Run vmrun list, capture output, and split it up
    file = subprocess.run([str(vmrunpath), COMMAND], stdout=subprocess.PIPE)
    file = file.stdout.decode('utf-8')
    filearray = file.split("\r\n")
    del filearray[-1] # Delete the blank line at the end
    if file == "Total running VMs: 0\r\n":
        # No VMs running, clear rich presence and set time to update on next change
        epoch_time = 0
        RPC.clear()
        continue
    elif len(filearray) >= 3:
        # Too many VMs to fit in field
        STATUS = "Running VMs"
        # Get VM count so we can show how many are running
        vmcount = [len(filearray) - 1, len(filearray) - 1]
    else:
        # Init variable
        displayName = ""
        vmx = Path(filearray[1].rstrip()) # New Path() to the VMX
        for line in vmx.read_text().split("\n"): # Get text from VMX, split on a new line
            if "displayName" in line: # Check if this is the displayName
                displayName = line[15:][:-1] # Get the display name
                STATUS = "Virtualizing " + displayName # Set status
        vmcount = None # Only 1 VM, so set vmcount to None
    if STATUS != LASTSTATUS: # To prevent spamming Discord, only update when something changes
        print("Rich presence updated locally; new rich presence is: " + STATUS) # Report of status change, before ratelimit
        if epoch_time == 0: # Only change the time if we stopped running VMs before
            # Get epoch time
            now = datetime.utcnow()
            epoch_time = int((now - datetime(1970, 1, 1)).total_seconds())
        if largeimage == None:
            largetext = None
        else:
            largetext = "Check out vm-rpc by DhinakG on GitHub!"
        # The big RPC update
        RPC.update(state=STATUS,details="Running VMware",large_image=largeimage,large_text=largetext,start=epoch_time,party_size=vmcount)
        LASTSTATUS = STATUS # Update last status to last status sent