"""
OpenLava master run as the framework.
"""

__author__ = 'tmetsch'

import logging
import os
import sys
import uuid

from mesos import native
from mesos import interface
from mesos.interface import mesos_pb2

import util

LOG = logging.getLogger(__name__)


class OpenLavaScheduler(interface.Scheduler):
    """
    OpenLava Mesos scheduler.
    """

    def __init__(self, executor):
        self.executor = executor
        self.slaves = {}

        self.master_host = util.start_lava(is_master=True)
        _, self.master_ip = util.get_ip()

    def resourceOffers(self, driver, offers):
        """
        Apache Mesos invokes this to inform us about offers. We can accept
        or decline...
        """
        # TODO: let's become smarter and grab only what we need in
        # future. - match pending jobs in queues to offers from mesos.
        # TODO: candidate: https://github.com/Netflix/Fenzo
        for offer in offers:
            if util.get_queue_length() > 10:
                operation = self._grab_offer(offer)
                driver.acceptOffers([offer.id], [operation])
            else:
                # TODO: work with filters
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
        """
        Called to tell us about the status of our task by Mesos.
        """
        tmp = update.data.split(':')
        if len(tmp) < 2:
            return
        host = tmp[0]
        ip_addr = tmp[1]

        if host not in self.slaves:
            self.slaves[host] = ip_addr
            util.add_to_hosts(host, ip_addr)
            util.add_to_cluster_conf(host)
            util.add_host_to_cluster(host.strip())
        elif update.state == mesos_pb2.TASK_FINISHED:
            util.rm_host_from_cluster(host.strip())
            util.rm_from_cluster_conf(host)
            util.rm_from_hosts(host)
            self.slaves.pop(host)
        elif update.state == mesos_pb2.TASK_LOST \
                or update.state == mesos_pb2.TASK_KILLED \
                or update.state == mesos_pb2.TASK_FAILED:
            driver.abort()

        util.show_openlava_state()

if __name__ == '__main__':
    LOG.setLevel(level='DEBUG')

    EXECUTOR = mesos_pb2.ExecutorInfo()
    EXECUTOR.executor_id.value = "default"
    EXECUTOR.command.value = os.path.abspath("/tmp/openlava_node.sh")
    EXECUTOR.name = "OpenLava executor"
    EXECUTOR.source = "openlava_test"

    FRAMEWORK = mesos_pb2.FrameworkInfo()
    FRAMEWORK.user = ''
    FRAMEWORK.name = 'OpenLava'

    # Setup the loggers
    LOGGERS = (__name__, 'mesos')
    for log in LOGGERS:
        logging.getLogger(log).setLevel(logging.DEBUG)

    # TODO: authentication
    FRAMEWORK.principal = 'openlava-framework'
    DRIVER = native.MesosSchedulerDriver(OpenLavaScheduler(EXECUTOR),
                                         FRAMEWORK,
                                         'master:5050')
    STATUS = 0 if DRIVER.run() == mesos_pb2.DRIVER_STOPPED else 1

    DRIVER.stop()

    sys.exit(STATUS)
