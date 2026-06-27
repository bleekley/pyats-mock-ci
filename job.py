import os

from pyats.easypy import run


def main(runtime):
    here = os.path.dirname(__file__)
    run(testscript=os.path.join(here, "test_underlay.py"))
