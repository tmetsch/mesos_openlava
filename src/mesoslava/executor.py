__author__ = 'tmetsch'

import sys
import threading
import subprocess
import time

import util

from mesos import interface
from mesos import native
from mesos.interface import mesos_pb2

OPENLAVA_PATH = '/opt/openlava-2.2'


class OpenLavaExecutor(interface.Executor):

    def launchTask(self, driver, task):
        # TODO: containerize openlava service itself...
        # XXX: this is a hack:
        # run a job on the master to add host to /etc/hosts & lsf.cluster.openlava
        # add hostname to lsf.cluster.openlava
        # start services...
        # and make sure openlava uses docker to execute (#TurtlesAllTheWay).

        def run_task():
            # start openlava services
            tmp = task.data.split(':')
            host = tmp[0]
            ip = tmp[1]
            util.add_hosts(host, ip)
            util.add_host_to_cluster(host)

            slv_host, slv_ip = util.get_ip()

            update = mesos_pb2.TaskStatus()
            update.task_id.value = task.task_id.value
            update.state = mesos_pb2.TASK_RUNNING
            update.data = slv_host + ':' + slv_ip
            driver.sendStatusUpdate(update)

            util.start_lava(OPENLAVA_PATH)

        thread = threading.Thread(target=run_task)
        thread.start()


if __name__ == "__main__":
    driver = native.MesosExecutorDriver(OpenLavaExecutor())
    sys.exit(0 if driver.run() == mesos_pb2.DRIVER_STOPPED else 1)
