# vm-rpc
Discord RPC for VMs. 

Currently the Python works only for VMware Workstation.
How to use:
1. Create a Discord app. (https://discordapp.com/developers/)
2. Install Python 3.
3. Install `pypresence` from `pip`.
4. (Optional, but will ask on runtime if not found) Create `vmwarePath.txt` with the path to VMware Workstation (the directory). It must be escaped or use backslashes instead of frontslashes, and have no extra lines.
5. (Optional, but will ask on runtime if not found) Create `clientID.txt` with the client ID of your Discord app. It must have no extra lines.
6. Run `main.py`.

Note: Discord has a 15 second ratelimit in sending Rich Presence updates.