__author__ = 'tmetsch'

import logging
import os
import subprocess
import sys
import uuid

import util

from mesos import native
from mesos import interface
from mesos.interface import mesos_pb2

OPENLAVA_PATH = '/opt/openlava-2.2'
LOG = logging.getLogger(__name__)


class OpenLavaScheduler(interface.Scheduler):

    def __init__(self, executor):
        self.executor = executor
        self.slaves = {}

        self.master_host = util.start_lava(OPENLAVA_PATH)
        _, self.master_ip = util.get_ip()

    def resourceOffers(self, driver, offers):
        # TODO: let's become smarter and grab only what we need in
        # future. - match pending jobs in queues to offers from mesos.

        LOG.info("Received %d offers" % len(offers))
        sys.stdout.flush()

        for offer in offers:
            if util.get_queue_length(OPENLAVA_PATH) > 10 or len(self.slaves)\
                    <= 1:
                # one compute node is running.
                sys.stdout.flush()
                operation = self._grab_offer(offer)
                driver.acceptOffers([offer.id], [operation])
            else:
                sys.stdout.flush()
                driver.declineOffer(offer.id)

    def _grab_offer(self, offer):
        """
        Grabs the offer from mesos and fires tasks.
        """
        offer_cpus = 0
        offer_mem = 0
        for resource in offer.resources:
            if resource.name == "cpus":
                offer_cpus += resource.scalar.value
            elif resource.name == "mem":
                offer_mem += resource.scalar.value

        # XXX: we take the complete offer here for now :-P
        # TODO: no need to run multiple openlava on one hosts I suspect...
        tid = uuid.uuid4()
        task = mesos_pb2.TaskInfo()
        task.task_id.value = str(tid)
        task.slave_id.value = offer.slave_id.value
        task.name = "task %d" % tid
        task.executor.MergeFrom(self.executor)
        # this is the master host
        task.data = self.master_host + ':' + self.master_ip

        cpus = task.resources.add()
        cpus.name = "cpus"
        cpus.type = mesos_pb2.Value.SCALAR
        cpus.scalar.value = offer_cpus

        mem = task.resources.add()
        mem.name = "mem"
        mem.type = mesos_pb2.Value.SCALAR
        mem.scalar.value = offer_mem

        operation = mesos_pb2.Offer.Operation()
        operation.type = mesos_pb2.Offer.Operation.LAUNCH
        operation.launch.task_infos.extend([task])

        return operation

    def statusUpdate(self, driver, update):
        tmp = update.data.split(':')
        if len(tmp) < 2:
            return
        host = tmp[0]
        ip = tmp[1]

        if host not in self.slaves:
            self.slaves[host] = ip
            util.add_host_to_cluster(host)
            util.add_hosts(host, ip)
            subprocess.check_output(['/opt/openlava-2.2/bin/lsaddhost',
                                     host.strip()])
        elif update.state == mesos_pb2.TASK_FINISHED:
            self.slaves.pop(host)
            subprocess.check_output(['/opt/openlava-2.2/bin/lsrmhost',
                                     host.strip()])
            util.rm_host_from_cluster(host)
            util.rm_hosts(host)
        elif update.state == mesos_pb2.TASK_LOST or \
             update.state == mesos_pb2.TASK_KILLED or \
             update.state == mesos_pb2.TASK_FAILED:
            driver.abort()

        print('Current queue length: '
              + str(util.get_queue_length(OPENLAVA_PATH)))
        print subprocess.check_output('/opt/openlava-2.2/bin/lsid')
        print subprocess.check_output('/opt/openlava-2.2/bin/bhosts')
        sys.stdout.flush()

if __name__ == '__main__':
    LOG.setLevel(level='DEBUG')

    executor = mesos_pb2.ExecutorInfo()
    executor.executor_id.value = "default"
    executor.command.value = os.path.abspath("/tmp/openlava_node.sh")
    executor.name = "OpenLava executor"
    executor.source = "openlava_test"

    framework = mesos_pb2.FrameworkInfo()
    framework.user = ''
    framework.name = 'OpenLava'

    # Setup the loggers
    loggers = (__name__, 'mesos')
    for log in loggers:
        logging.getLogger(log).setLevel(logging.DEBUG)

    # TODO: authentication
    framework.principal = 'openlava-framework'
    driver = native.MesosSchedulerDriver(OpenLavaScheduler(executor),
                                         framework,
                                         'master:5050')
    status = 0 if driver.run() == mesos_pb2.DRIVER_STOPPED else 1

    driver.stop()

    sys.exit(status)
