# note: this file needs to be run as admin for commands to work

import subprocess
from pathlib import Path
from sys import platform

class hyperv(object):
    runningVMs = None
    VMs = None
    def updateVMs(self):
        VMs = subprocess.run(["powershell", "Get-VM | Select Name"], stdout=subprocess.PIPE)
        VMs = VMs.stdout.decode("utf-8")
        VMs = VMs.split("\r\n")
        self.VMs = [x for x in VMs if len(x)]
    def updateRunningVMs(self):
        runningVMs = subprocess.run(["powershell", "Get-VM | Where { $_.State -eq 'Running' } | Select Name"], stdout=subprocess.PIPE)
        runningVMs = runningVMs.stdout.decode("utf-8")
        runningVMs = runningVMs.split("\r\n")
        self.runningVMs = [x for x in runningVMs if len(x)]
    def updateOutput(self):
        self.updateRunningVMs()
        self.updateVMs()
    def isFound(self):
        if platform.lower() != "win32":
            return False
        elif self.runningVMs != [] and self.runningVMs != None:
            if "not recognized" in self.runningVMs[0]:
                return False
            else:
                return True
        else:
            return True
    def runCount(self):
        if self.runningVMs == []:
            return 0
        else:
            return len(self.runningVMs[2:])
    def isRunning(self):
        if self.runCount() > 0:
            return True
        else:
            return False
    def getGuestName(self, index = None):
        if self.VMs == []:
            return None
        elif index != None:
            return self.VMs[index + 2]
        else:
            return self.VMs[2:]
    def getRunningGuestName(self, index = None):
        if self.isRunning() == False:
            return None
        elif index != None:
            return self.runningVMs[index + 2]
        else:
            return self.runningVMs[2:]