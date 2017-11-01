#!/usr/bin/env python2.7

import logging
import os

from mesos import native
from mesos.interface import mesos_pb2

from mesoslava import framework
from mesoslava import lava_control
from mesoslava import ui

LOG = logging.getLogger(__name__)


if __name__ == '__main__':
    import sys
    sys.path.append('/tmp/mesoslava')

    LOG.setLevel(level='DEBUG')

    EXECUTOR = mesos_pb2.ExecutorInfo()
    EXECUTOR.executor_id.value = "default"
    EXECUTOR.command.value = os.path.abspath("/tmp/executor.py")
    EXECUTOR.name = "OpenLava executor"
    EXECUTOR.source = "openlava_test"

    FRAMEWORK = mesos_pb2.FrameworkInfo()
    FRAMEWORK.user = ''
    FRAMEWORK.name = 'OpenLava'
    FRAMEWORK.roles.append('hpc')
    role1 = FRAMEWORK.capabilities.add()
    role1.type = FRAMEWORK.Capability.MULTI_ROLE
    role2 = FRAMEWORK.capabilities.add()
    role2.type = FRAMEWORK.Capability.GPU_RESOURCES
    FRAMEWORK.webui_url = 'http://%s:9876' % ui.web.get_hostname()

    # Setup the loggers
    LOGGERS = (__name__, 'mesos')
    for log in LOGGERS:
        logging.getLogger(log).setLevel(logging.DEBUG)

    # TODO: authentication
    # TODO: revocable
    # TODO: pick up mesos master URI from env var.
    FRAMEWORK.principal = 'openlava-framework'
    LAVA_CTRL = lava_control.LavaControl()
    DRIVER = native.MesosSchedulerDriver(framework.OpenLavaScheduler(EXECUTOR,
                                                                     LAVA_CTRL),
                                         FRAMEWORK,
                                         'master:5050')
    STATUS = 0 if DRIVER.run() == mesos_pb2.DRIVER_STOPPED else 1

    DRIVER.stop()

    sys.exit(STATUS)