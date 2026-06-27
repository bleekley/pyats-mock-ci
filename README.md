# pyats-mock-ci

Record a real network device once, then run pyATS tests against the recording in
CI forever. No lab to license, boot, or reach from the pipeline.

This is the companion repo for the blog post
[Record Once, Test Forever](https://brent.leekley.me/blog/record-once-test-forever/),
part of a series pairing [Cisco pyATS](https://developer.cisco.com/docs/pyats/)
with [Cisco Modeling Labs 2](https://developer.cisco.com/modeling-labs/).

## The idea

Engineers develop against a live CML2 spine-leaf fabric. But a GitHub Actions
runner cannot see that lab, and you would not want every push to depend on a
booted lab anyway. So we record the device output once with unicon playback,
commit the recording, and let CI replay the exact same pyATS suite against it.

```
record on the live lab  ->  commit the recording  ->  replay in CI, no lab
```

## What is in here

| Path | What it is |
| --- | --- |
| `testbeds/testbed.yaml` | The same testbed used against the live lab. Credentials come from `%ENV{...}`. |
| `data_collect.py` | Connects to the lab and runs the show commands so unicon can record them. |
| `records/spine1` | The committed recording of spine1. This is what CI replays. |
| `test_underlay.py` | The aetest: spine1 must have an OSPF route to every other loopback. |
| `job.py` | The easypy job that runs the testscript. |
| `mock_output/spine1_ios.yaml` | Optional, human-readable mock for `mock_device_cli`. Not used by CI. |
| `.github/workflows/replay.yml` | The pipeline: pip install pyATS, replay the suite, no network. |

The recordings are sanitized lab output: RFC 5737 / RFC 2544 addresses and
throwaway `cisco` / `cisco` lab credentials. Nothing here is production data.

## Run it yourself

Replay against the committed recording (no lab required):

```bash
pip install -r requirements.txt
export PYATS_UNAME=cisco PYATS_PWORD=cisco
pyats run job job.py --testbed-file testbeds/testbed.yaml --replay records/
```

Re-record against your own lab (edit `testbeds/testbed.yaml` first):

```bash
export PYATS_UNAME=cisco PYATS_PWORD=cisco
python data_collect.py --record ./records
python -m unicon.playback.mock \
  --recorded-data ./records/spine1 \
  --output ./mock_output/spine1_ios.yaml
```

Kick the tires on the mock from a shell:

```bash
echo 'show ip route' | mock_device_cli --os ios --hostname spine1 \
  --mock_data_dir mock_output --state execute
```
