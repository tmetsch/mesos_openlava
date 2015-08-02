__author__ = 'tmetsch'

import sys
import threading
import time

import util

from mesos import interface
from mesos import native
from mesos.interface import mesos_pb2

OPENLAVA_PATH = '/opt/openlava-2.2'


class OpenLavaExecutor(interface.Executor):

    def launchTask(self, driver, task):
        # TODO: containerize openlava service itself...
        # and make sure openlava uses docker to execute (#TurtlesAllTheWay).

        def run_task():
            # start openlava services
            tmp = task.data.split(':')
            host = tmp[0]
            ip = tmp[1]
            util.add_hosts(host, ip)
            util.add_host_to_cluster(host)

            slave_host, slave_ip = util.get_ip()

            update = mesos_pb2.TaskStatus()
            update.task_id.value = task.task_id.value
            update.state = mesos_pb2.TASK_RUNNING
            update.data = slave_host + ':' + slave_ip
            driver.sendStatusUpdate(update)

            util.start_lava(OPENLAVA_PATH)

            # in case I'm idle for a while done.
            busy = True
            count = 0
            while busy:
                time.sleep(10)

                try:
                    if util.njobs_per_host(OPENLAVA_PATH, slave_host.strip()) \
                            == 0:
                        count += 1
                except:
                    # lim not ready...
                    pass

                if count >= 10 and slave_host.strip() != 'testnode':
                    busy = False
                    util.stop_lava()
                    update = mesos_pb2.TaskStatus()
                    update.task_id.value = task.task_id.value
                    update.state = mesos_pb2.TASK_FINISHED
                    update.data = slave_host + ':' + slave_ip
                    driver.sendStatusUpdate(update)

        thread = threading.Thread(target=run_task)
        thread.start()


if __name__ == "__main__":
    driver = native.MesosExecutorDriver(OpenLavaExecutor())
    sys.exit(0 if driver.run() == mesos_pb2.DRIVER_STOPPED else 1)
