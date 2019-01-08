import subprocess
from pathlib import *
import staticConstant
from sys import platform

class vmware(object):
    vmrunpath = None
    output = None
    def __init__(self, vmwarepath):
        if platform.lower() == "win32":
            vmwarepath = vmwarepath.replace('\"', "")
            vmwarepath = vmwarepath.replace("\'", "")
            self.vmrunpath = Path(vmwarepath).joinpath("vmrun.exe")
        else:
            self.vmrunpath = vmwarepath
    def updateOutput(self):
        output = subprocess.run([str(self.vmrunpath), "list"], stdout=subprocess.PIPE)
        output = output.stdout.decode("utf-8")
        if platform.lower() == "win32":
            output = output.split("\r\n")
        else:
            output = output.split("\n")
        self.output = [x for x in output if len(x)] # Don't rely on always having a blank element at the end, thanks CorpNewt
    def runCount(self):
        return len(self.output) - 1
    def isRunning(self):
        if self.runCount() > 0:
            return True
        else:
            return False
    def getRunningVMPath(self, index = None):
        if self.isRunning() == False:
            return None
        # Thanks to CorpNewt for the fix
        elif index != None:
            return self.output[index + 1]
        else:
            return self.output[1:]
    def getVMProperty(self, path, property):
        vmx = Path(path)
        value = None
        for line in vmx.read_text().split("\n"):
            if property in line:
                value = line[len(property) + 4:][:-1]
                break
        return value
    def getRunningVMProperty(self, index, property):
        return self.getVMProperty(self.getRunningVMPath(index), property)
    def getGuestName(self, path):
        return self.getVMProperty(path, "displayName")
    def getRunningGuestName(self, index):
        return self.getRunningVMProperty(index, "displayName")
    def getGuestOS(self, path, raw=None):
        if raw == None or raw == False:
            property = self.getVMProperty(path, "guestOS")
            return staticConstant.guestOS.get(property, "Unknown")
        else:
            return self.getVMProperty(path, "guestOS")
    def getRunningGuestOS(self, index, raw=None):
        if raw == None or raw == False:
            property = self.getRunningVMProperty(index, "guestOS")
            return staticConstant.guestOS.get(property, "Unknown")
        else:
            return self.getRunningVMProperty(index, "guestOS")