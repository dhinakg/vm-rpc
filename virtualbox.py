import subprocess
from pathlib import Path
from sys import platform
import datetime
from pytz import UTC
from dateutil import parser
utc = UTC

def find_dict_in_list(dict_name : str, arr : list) -> dict: #finds the dict whose first key is equal to the specified name in a list
    return [arr[arr.index(x)] for x in arr if list(arr[arr.index(x)].keys())[0] == dict_name][0]

class virtualbox(object):

    def __init__(self, virtualboxpath) -> None:
        if platform.lower() == "win32":
            virtualboxpath = virtualboxpath.replace('\"', "")
            virtualboxpath = virtualboxpath.replace("\'", "")
            self.vmrunpath = Path(virtualboxpath).joinpath("VBoxManage.exe")
        else:
            self.vmrunpath = virtualboxpath
        self.vminfo = []
        self.output = []

    def updateOutput(self) -> None:
        output = subprocess.run([str(self.vmrunpath), "list", "runningvms"], stdout=subprocess.PIPE)
        output = output.stdout.decode("utf-8")
        if platform.lower() == "win32":
            output = output.split("\r\n")
        else:
            output = output.split("\n")
        output = [{x[:x.find(' {')].strip().replace('"', '') : {"Hash": x[x.find(' {')+2:len(x)-1].strip()}} for x in output if len(x)]

        for vm in output:
            vmname = list(vm.keys())[0]
            vminfo = subprocess.run([str(self.vmrunpath), "showvminfo", vmname], stdout=subprocess.PIPE)
            vminfo = vminfo.stdout.decode("utf-8")
            vminfo = vminfo.replace("Name", "displayName", 1)
            if platform.lower() == "win32":
                vminfo = vminfo.split("\r\n")
            else:
                vminfo = vminfo.split("\n")
            for num, line in enumerate(vminfo):
                if line.startswith("Shared folders:"):
                    del_line = num
                    break
            vminfo = vminfo[:del_line]+vminfo[del_line+4:]
            find_dict_in_list(vmname, output)[vmname].update({line.split(':', 1)[0].strip(): line.split(':', 1)[1].strip() if len(line.split(':', 1)) > 1 else "Undefined" for line in vminfo if line.find(':') != -1 and line[0].strip() != '#'})
        
        self.output = output

    def runCount(self) -> int:
        return len(self.output)

    def isRunning(self) -> bool:
        if self.runCount() > 0:
            return True
        else:
            return False

    def getRunningGuestName(self, index) -> str:
        return list(self.output[index].keys())[0]

    def getVMProperty(self, index, property) -> str:
        return self.output[index][self.getRunningGuestName(index)][property]

    def getVMuptime(self, index) -> int:
        # Date is in the format of `running (since 2023-05-10T10:32:30.185000000)`
        state = self.getVMProperty(index, "State")
        return int(parser.parse(state[state.find('since')+6:state.find('.')]).replace(tzinfo=datetime.timezone.utc).timestamp())
