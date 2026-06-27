"""Underlay reachability check, recorded once on CML2 and replayed in CI.

spine1 should have an OSPF route to every other loopback in the fabric. The
assertion is a dictionary lookup against parsed structured data, not a regex
against screen-scraped text.

The same suite runs two ways with zero code changes:

    # against the live CML2 lab
    pyats run job job.py --testbed-file testbeds/testbed.yaml

    # against the committed recording, no lab needed (this is what CI runs)
    pyats run job job.py --testbed-file testbeds/testbed.yaml --replay records/
"""

from pyats import aetest

# spine1's three fabric peers, learned over OSPF.
REMOTE_LOOPBACKS = ["2.2.2.2/32", "11.11.11.11/32", "22.22.22.22/32"]


class CommonSetup(aetest.CommonSetup):
    @aetest.subsection
    def connect(self, testbed):
        testbed.devices["spine1"].connect(log_stdout=False)


class UnderlayReachability(aetest.Testcase):
    @aetest.test
    def remote_loopbacks_present(self, testbed):
        spine1 = testbed.devices["spine1"]

        # Run the command, then parse the captured text. Feeding execute() output
        # into parse(output=...) is what keeps this working in --replay, where the
        # connection is a recording rather than a live socket.
        output = spine1.execute("show ip route")
        routes = spine1.parse("show ip route", output=output)

        seen = routes["vrf"]["default"]["address_family"]["ipv4"]["routes"].keys()
        for loopback in REMOTE_LOOPBACKS:
            assert loopback in seen, f"spine1 has no route to {loopback}"


class CommonCleanup(aetest.CommonCleanup):
    @aetest.subsection
    def disconnect(self, testbed):
        testbed.devices["spine1"].disconnect()
