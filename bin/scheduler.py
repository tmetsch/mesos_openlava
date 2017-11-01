#!/usr/bin/env python2.7
"""
Kick-off OpenLava DCOS service.
"""

import logging
import os
import sys

sys.path.append('/tmp/mesoslava')

from mesos import native
from mesos.interface import mesos_pb2

from mesoslava import framework
from mesoslava import lava_control
from mesoslava import ui

LOG = logging.getLogger(__name__)


def main():
    """
    Main routine.
    """
    LOG.setLevel(level='DEBUG')

    executor = mesos_pb2.ExecutorInfo()
    executor.executor_id.value = "default"
    executor.command.value = os.path.abspath("/tmp/executor.py")
    executor.name = "OpenLava executor"
    executor.source = "openlava_test"

    dcos_service = mesos_pb2.FrameworkInfo()
    dcos_service.user = ''
    dcos_service.name = 'OpenLava'
    dcos_service.roles.append('hpc')
    role1 = dcos_service.capabilities.add()
    role1.type = dcos_service.Capability.MULTI_ROLE
    role2 = dcos_service.capabilities.add()
    role2.type = dcos_service.Capability.GPU_RESOURCES
    dcos_service.webui_url = 'http://%s:9876' % ui.web.get_hostname()

    # Setup the loggers
    log = (__name__, 'mesos')
    for log in log:
        logging.getLogger(log).setLevel(logging.DEBUG)

    # TODO: authentication
    # TODO: revocable
    # TODO: pick up mesos master URI from env var.
    dcos_service.principal = 'openlava-service'
    lava_ctrl = lava_control.LavaControl()
    scheduler = framework.OpenLavaScheduler(executor, lava_ctrl)
    driver = native.MesosSchedulerDriver(scheduler,
                                         dcos_service,
                                         'master:5050')
    return driver


if __name__ == '__main__':
    DRIVER = main()
    STATUS = 0 if DRIVER.run() == mesos_pb2.DRIVER_STOPPED else 1
    DRIVER.stop()

    sys.exit(STATUS)
