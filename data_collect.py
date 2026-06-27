"""Record real device output once, so CI can replay it forever.

Run this against the live CML2 fabric with unicon's --record flag:

    export PYATS_UNAME=cisco PYATS_PWORD=cisco
    python data_collect.py --record ./records

unicon writes one recording per device into ./records/<hostname>. That file is
what the test suite replays in CI, with no lab in reach.
"""

from genie.testbed import load

# Every command the suite will ask for later must be recorded here, because
# replay can only answer what was captured.
LIST_OF_CMDS = [
    "show ip route",
    "show ip interface brief",
    "show ip ospf neighbor",
]

testbed = load("testbeds/testbed.yaml")
device = testbed.devices["spine1"]

device.connect(log_stdout=False)
for command in LIST_OF_CMDS:
    device.execute(command)
device.disconnect()
