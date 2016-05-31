"""
OpenLava executor for Apache Mesos. Fires up a LIM, PIM, SBATCHD, RES.
"""

__author__ = 'tmetsch'

import sys
import json
import threading
import time

from mesos import interface
from mesos import native
from mesos.interface import mesos_pb2

import util


class OpenLavaExecutor(interface.Executor):
    """
    OpenLava Mesos executor.
    """
    # TODO: could make use of docker itself - aka run jobs in docker.

    def launchTask(self, driver, task):
        """
        Fires up OpenLava services and once obsolete kill them again.
        """
        # TODO: containerize openlava service itself...

        def run_task():
            """
            Run a Apache Mesos Task.
            """
            slave_host, slave_ip = util.get_ip()

            # start openlava services
            tmp = json.loads(task.data)
            host = tmp['master_host']
            ip_addr = tmp['master_ip']
            util.add_to_hosts(host, ip_addr)
            util.add_to_cluster_conf(host)

            update = mesos_pb2.TaskStatus()
            update.task_id.value = task.task_id.value
            update.state = mesos_pb2.TASK_RUNNING
            update.data = slave_host + ':' + slave_ip
            driver.sendStatusUpdate(update)

            util.start_lava()

            # in case I'm idle for a while done.
            busy = True
            count = 0
            while busy:
                time.sleep(10)

                try:
                    if util.njobs_per_host(slave_host.strip()) == 0:
                        count += 1
                except:
                    # lim not ready...
                    pass

                if count >= 12:
                    busy = False
                    update = mesos_pb2.TaskStatus()
                    update.task_id.value = task.task_id.value
                    update.state = mesos_pb2.TASK_FINISHED
                    update.data = slave_host + ':' + slave_ip
                    driver.sendStatusUpdate(update)
                    util.stop_lava()

        thread = threading.Thread(target=run_task)
        thread.start()


if __name__ == "__main__":
    DRIVER = native.MesosExecutorDriver(OpenLavaExecutor())
    sys.exit(0 if DRIVER.run() == mesos_pb2.DRIVER_STOPPED else 1)
