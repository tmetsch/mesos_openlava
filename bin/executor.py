#!/usr/bin/env python2.7

import sys

sys.path.append('/tmp/mesoslava')
sys.path.append('/usr/local/lib/python2.7/site-packages')

from mesos import native
from mesos.interface import mesos_pb2

from mesoslava import executor
from mesoslava import lava_control

if __name__ == "__main__":
    LAVA_CTRL = lava_control.LavaControl()
    DRIVER = native.MesosExecutorDriver(executor.OpenLavaExecutor(LAVA_CTRL))
    sys.exit(0 if DRIVER.run() == mesos_pb2.DRIVER_STOPPED else 1)
