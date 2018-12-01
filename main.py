from pypresence import Presence
import time
import subprocess
import os.path


if os.path.isfile("clientID.txt"):
    idfile = open("clientID.txt")
    for line in idfile:
        client_ID = line.rstrip()
else:
    client_ID = input("Enter client ID: ")

if os.path.isfile("vmwarePath.txt"):
    vmwarefile = open("vmwarePath.txt")
    for line in vmwarefile:
        vmwarepath = line.rstrip()
else:
    vmwarepath = input("Enter path to VMware Workstation folder, with backslashes or escaped frontslashes: ")

vmwarepath = vmwarepath.replace("\"", "")
vmwarepath = os.path.join(vmwarepath, '')
VMRUNPATH = vmwarepath + "vmrun.exe"
COMMAND = "list"

RPC = Presence(client_ID, pipe=0)
RPC.connect()
print("Connected to RPC.")
LASTSTATUS = ""



print("Please note that Discord has a 15 second ratelimit in sending Rich Presence updates.")
while True:
    file = subprocess.run([VMRUNPATH, COMMAND], stdout=subprocess.PIPE)
    file = file.stdout.decode('utf-8')
    filearray = file.split("\n")
    del filearray[-1]
    if file == "Total running VMs: 0\r\n":
        RPC.clear()
        continue
    elif len(filearray) >= 3:
        STATUS = "Running multiple VMs"
    else:
        displayName = ""
        handle = open(filearray[1].rstrip())
        for line in handle:
            if "displayName" in line:
                displayName = line[15:][:-2]
                STATUS = "Virtualizing " + displayName
    if STATUS != LASTSTATUS:
        print("Rich presence updated locally; new rich presence is: " + STATUS)
        RPC.update(state=STATUS,details="Running VMware")
        LASTSTATUS = STATUS