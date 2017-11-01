"""
OpenLava executor for Apache Mesos. Fires up a LIM, PIM, SBATCHD, RES.
"""

import json
import threading
import time

from mesos import interface
from mesos.interface import mesos_pb2

__author__ = 'tmetsch'

TIMEOUT = 10
COUNT = 12


class OpenLavaExecutor(interface.Executor):
    """
    OpenLava Mesos executor.
    """
    # TODO: could make use of docker itself - aka run jobs in docker.

    def __init__(self, lava_controller):
        super(OpenLavaExecutor, self).__init__()

        self.lava_ctrl = lava_controller
        self.task = None
        self.task_data = None
        self.driver = None

    def _start_lava(self):
        """
        Start OpenLava on agent.
        """
        # start openlava services
        master_hostname = self.task_data['master_hostname']
        master_ip = self.task_data['master_ip']

        # configure the master.
        self.lava_ctrl.add_host(master_hostname, master_ip, False)
        self.lava_ctrl.start_lava(False)

    def _stop_lava(self):
        """
        Stop OpenLava on agent.
        """
        self.lava_ctrl.stop_lava()

    def _create_update(self):
        """
        Create a task update.
        """
        agent_hostname = self.task_data['agent_hostname']
        agent_ip = self.task_data['agent_ip']

        update = mesos_pb2.TaskStatus()
        update.task_id.value = self.task.task_id.value
        update.data = json.dumps({'agent_hostname': agent_hostname,
                                  'agent_ip': agent_ip})
        return update

    def run_task(self):
        """
        Run a Apache Mesos Task.
        """
        busy = True
        count = 0
        while busy:
            time.sleep(TIMEOUT)
            try:
                if self.lava_ctrl.host_njobs(
                        self.task_data['agent_hostname']) == 0:
                    count += 1
            except:
                # lim not ready...
                pass

            if count >= COUNT:
                # in case I'm idle for a while finish...
                busy = False
                update = self._create_update()
                update.state = mesos_pb2.TASK_FINISHED
                self.driver.sendStatusUpdate(update)
                self._stop_lava()

    def launchTask(self, driver, task):
        """
        Fires up OpenLava services and once obsolete kill them again.
        """
        # TODO: containerize Openlava service itself...
        self.task = task
        self.task_data = json.loads(self.task.data)
        self.driver = driver

        # start lava
        self._start_lava()

        # tell master we are ready to fire up.
        update = self._create_update()
        update.state = mesos_pb2.TASK_RUNNING
        driver.sendStatusUpdate(update)

        # start a thread.
        thread = threading.Thread(target=self.run_task)
        thread.start()
