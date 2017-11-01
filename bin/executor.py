#!/usr/bin/env python2.7
"""
Kick-off OpenLava agent/executor.
"""

import sys

sys.path.append('/tmp/mesoslava')
sys.path.append('/usr/local/lib/python2.7/site-packages')

from mesos import native
from mesos.interface import mesos_pb2

from mesoslava import executor
from mesoslava import lava_control


def main():
    """
    Main routine.
    """
    lava_ctrl = lava_control.LavaControl()
    driver = native.MesosExecutorDriver(executor.OpenLavaExecutor(lava_ctrl))

    return driver


if __name__ == "__main__":
    DRIVER = main()
    STATUS = 0 if DRIVER.run() == mesos_pb2.DRIVER_STOPPED else 1
    sys.exit(STATUS)
