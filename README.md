# vm-rpc
Discord RPC for VMs. 

**Works with VMware Workstation 14/15, VMware Fusion 14/15 and Hyper-V. VMware Workstation Player 14/15 users, see [here](https://github.com/dhinakg/vm-rpc/blob/master/vix.md).**

How to use:
1. Create a Discord app. (https://discordapp.com/developers/)
2. Install Python 3.
3. Install `pypresence` from `pip`.
4. (Optional, if not found will enable Hyper-V and VMware) Create `hypervisors.txt`, containing `vmware`, `hyper-v`, or both (case insensitive).
5. (Optional, but will ask on runtime if not found and VMware enabled and Windows) Create `vmwarePath.txt` with the path to VMware Workstation (the directory), or if using VMware Workstation Player, the path to VMware VIX. It must have no extra lines.
5. (Optional, but will ask on runtime if not found) Create `clientID.txt` with the client ID of your Discord app. It must have no extra lines.
6. Run `legacy.py`, or `main.py` for the refactor that uses the VMware library. Hyper-V support is only in `main.py`, and requires adminstrator privileges.

**Note: If you get `Access is denied`, restart Discord.**

Note: Discord has a 15 second ratelimit in sending Rich Presence updates.

TO-DO
- [x] Hyper-V library
- [x] Add Hyper-V to code
- [X] Wait for Discord to open instead of erroring out
- [X] Stopped running VMs message
- [X] Multi-platform support
- [ ] VirtualBox library
- [ ] Add VirtualBox to code
- [X] Allow user to enable/disable hypervisor support
- [ ] Add custom hypervisor priority
- [ ] Switch client IDs based on current hypervisor
- [ ] Switch large image based on current hypervisor
