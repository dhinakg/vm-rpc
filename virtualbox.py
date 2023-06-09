import subprocess
from pathlib import Path
from sys import platform
import datetime
from pytz import UTC

utc = UTC

class virtualbox(object):
    vmrunpath = None
    output = None

    def __init__(self, virtualboxpath, tz) -> None:
        if platform.lower() == "win32":
            virtualboxpath = virtualboxpath.replace('\"', "")
            virtualboxpath = virtualboxpath.replace("\'", "")
            self.vmrunpath = Path(virtualboxpath).joinpath("VBoxManage.exe")
        else:
            self.vmrunpath = virtualboxpath
        self.tz = tz
        self.vminfo = None

    def updateOutput(self) -> None:
        # output = subprocess.run([str(self.vmrunpath), "list", "runningvms"], stdout=subprocess.PIPE)
        # output = output.stdout.decode("utf-8")
        with subprocess.Popen([str(self.vmrunpath), "list", "runningvms"], stdout=subprocess.PIPE) as proc:
            output = proc.stdout.read().decode()
        if platform.lower() == "win32":
            output = output.split("\r\n")
        else:
            output = output.split("\n")
        self.output = [{"Name": x[:x.find(' {')].strip().replace('"', ''), "Hash": x[x.find(' {'):].strip()} for x in output if len(x)]
        self.vminfo = [[] for _ in range(self.runCount())]
        for i in range(self.runCount()):
            # vminfo = subprocess.run([str(self.vmrunpath), "showvminfo", self.getGuestName(i)], stdout=subprocess.PIPE)
            # vminfo = vminfo.stdout.decode("utf-8")
            with subprocess.Popen([str(self.vmrunpath), "showvminfo", self.getGuestName(i)], stdout=subprocess.PIPE) as proc:
                vminfo = proc.stdout.read().decode()
            vminfo = vminfo.replace("Name", "displayName", 1)
            if platform.lower() == "win32":
                vminfo = vminfo.split("\r\n")
            else:
                vminfo = vminfo.split("\n")
            self.vminfo[i] = {line.split(':', 1)[0].strip(): line.split(':', 1)[1].strip() if len(line.split(':', 1)) > 1 else "Undefined" for line in vminfo if line.find(':') != -1 and line[0].strip() != '#'}

    def runCount(self) -> int:
        return len(self.output)

    def isRunning(self) -> bool:
        if self.runCount() > 0:
            return True
        else:
            return False

    def getVMProperty(self, index, property) -> str:
        return self.vminfo[index][property]

    def getRunningVMPath(self, index=None) -> str:
        if self.isRunning() == False:
            return None
        elif index != None:
            return self.getVMProperty(index, "Location")
        else:
            return self.getVMProperty(0, "Location")

    def getGuestName(self, index: int = 0) -> str:
        return self.output[index]["Name"]

    def getRunningGuestName(self, index) -> str:
        return self.getVMProperty(index, "displayName")

    def getVMuptime(self, index) -> int:
        state = self.getVMProperty(index, "State")
        # Date is in the format of `running (since 2023-05-10T10:32:30.185000000)`
        dt = datetime.datetime.fromisoformat(
            state[state.find('since')+6:state.find('.')])
        dt = utc.localize(dt)
        dt = dt.astimezone(self.tz)
        return int(dt.timestamp())
