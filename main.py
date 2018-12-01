from pypresence import Presence # The simple rich presence client in pypresence
import time

client_ID = "518230088228274178"
RPC = Presence(client_ID, pipe=0)
RPC.connect()
RPC.update(state="Currently in development",details="Apparently you need detail"
"s instead of \n test",start=1543626576,party_id="453dd",party_size=[1,20],instance=True,spectate="ggg",join="ccc",match="ddd")
while True:
    time.sleep(15)
