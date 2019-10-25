from pypresence import Presence, DiscordError, exceptions, InvalidPipe # For rich presence
import subprocess # For running VMs
from datetime import datetime # For epoch time
from pathlib import * # For reading files
from vmware import vmware
from hyperv import hyperv
from time import sleep
from sys import platform
from loadSettings import *
import json

STATUS = LASTSTATUS = None
running = False
epoch_time = 0

def clear():
    epoch_time = 0
    RPC.clear()
    STATUS = None
    LASTSTATUS = None
    if running == True:
        print("Stopped running VMs.")
        running = False

settings, hypervisors, vmwarepath = loadSettings()

if "vmware" in hypervisors:
    # Initialize VMware
    vmware = vmware(vmwarepath)

if "hyper-v" in hypervisors:
    # Initialize Hyper-V
    hyperv = hyperv()

# Set up RPC
RPC = Presence(settings["clientID"])
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
    if STATUS != LASTSTATUS and STATUS != None: # To prevent spamming Discord, only update when something changes
        print("Rich presence updated locally; new rich presence is: " + STATUS + " (using " + HYPERVISOR + ")") # Report of status change, before ratelimit
        if epoch_time == 0: # Only change the time if we stopped running VMs before
            # Get epoch time
            now = datetime.utcnow()
            epoch_time = int((now - datetime(1970, 1, 1)).total_seconds())
        if settings["largeImage"] == None:
            largetext = None
        else:
            largetext = "Check out vm-rpc by DhinakG on GitHub!"
        # The big RPC update
        RPC.update(state=STATUS,details="Running " + HYPERVISOR,large_image=settings["largeImage"],large_text=largetext,start=epoch_time,party_size=vmcount)
        LASTSTATUS = STATUS # Update last status to last status sent