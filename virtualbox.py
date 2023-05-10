import subprocess
from pathlib import *
from sys import platform
import datetime
from pytz import UTC

utc = UTC

class virtualbox(object):
    vmrunpath = None
    output = None
    def __init__(self, virtualboxpath, tz):
        if platform.lower() == "win32":
            virtualboxpath = virtualboxpath.replace('\"', "")
            virtualboxpath = virtualboxpath.replace("\'", "")
            self.vmrunpath = Path(virtualboxpath).joinpath("VBoxManage.exe")
        else:
            self.vmrunpath = virtualboxpath
        self.tz = tz
    def updateOutput(self):
        output = subprocess.run([str(self.vmrunpath), "list", "runningvms"], stdout=subprocess.PIPE)
        output = output.stdout.decode("utf-8")
        if platform.lower() == "win32":
            output = output.split("\r\n")
        else:
            output = output.split("\n")
        self.output = [x[:x.find(' ')].replace('"','') for x in output if len(x)]
        if self.runCount() == 1:
            vminfo = subprocess.run([str(self.vmrunpath), "showvminfo", self.getGuestName(0)], stdout=subprocess.PIPE)
            vminfo = vminfo.stdout.decode("utf-8")
            vminfo = vminfo.replace('Name','displayName',1)
            if platform.lower() == "win32":
                vminfo = vminfo.split("\r\n")
            else:
                vminfo = vminfo.split("\n")
            self.vminfo = {line.split(':',1)[0].strip():line.split(':',1)[1].strip() if len(line.split(':',1)) > 1 else "Undefined" for line in vminfo if line.find(':') != -1 and line[0].strip() != '#'}

    def runCount(self):
        return len(self.output)
    def isRunning(self):
        if self.runCount() > 0:
            return True
        else:
            return False
    def getVMProperty(self, property):
        return self.vminfo[property]
    def getRunningVMPath(self):
        if self.isRunning() == False:
            return None
        return self.getVMProperty('Location')
    def getGuestName(self, index : int = 0):
        return self.output[index]
    def getRunningGuestName(self):
        return self.getVMProperty("displayName")
    def getVMuptime(self):
        state = self.getVMProperty('State')
        dt = datetime.datetime.fromisoformat(state[state.find('since')+6:state.find('.')]) # Date is in the format of `running (since 2023-05-10T10:32:30.185000000)`
        dt = utc.localize(dt)
        dt = dt.astimezone(self.tz)
        return int(dt.timestamp())

if __name__ == '__main__':
    vbox = virtualbox("F:/Program Files (x86)/Oracle/VirtualBox")
    vbox.updateOutput()
    vbox.getVMuptime()