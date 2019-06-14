# vm-rpc

Discord RPC for VMs. 

**Works with VMware Workstation 14/15, VMware Fusion 14/15 and Hyper-V. VMware Workstation Player 14/15 users, see [here](https://github.com/dhinakg/vm-rpc/blob/master/vix.md).**

How to use:

1. Create a Discord app. (https://discordapp.com/developers/)
2. Install Python 3.
3. Install `pypresence` from `pip`.
4. Rename `sample-settings.json` to `settings.json` and configure your settings as neccessary.
5. Run `main.py`. Hyper-V support requires adminstrator privileges.

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
- [ ] Switch large image based on current OS for VMware, and a image of Hyper-V for Hyper-V
- [ ] Small image of VMware if VMware is current hypervisor
- [X] Unified settings file using JSON