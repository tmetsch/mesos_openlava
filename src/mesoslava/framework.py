__author__ = 'tmetsch'

import logging
import os
import time
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
        # TODO: start lim that will become master
        self.executor = executor
        self.ol_mstr = util.start_lava(OPENLAVA_PATH)
        _, self.ol_mstr_ip = util.get_ip()
        self.slaves = {}

    def resourceOffers(self, driver, offers):
        # TODO: as long as the queues are empty don't accepts offers.
        # else accept offer
        # TODO: if queue length is low & host are idleing - mark those tasks
        #  as done & remove openlava host
        for offer in offers:
            offer_cpus = 0
            offer_mem = 0
            for resource in offer.resources:
                if resource.name == "cpus":
                    offer_cpus += resource.scalar.value
                elif resource.name == "mem":
                    offer_mem += resource.scalar.value

            # XXX: we take the complete offer here for now :-P
            # TODO: let's become smarter and grab only what we need in future.
            # no need to run multiple openlava on one hosts I suspect...
            tid = uuid.uuid4()
            task = mesos_pb2.TaskInfo()
            task.task_id.value = str(tid)
            task.slave_id.value = offer.slave_id.value
            task.name = "task %d" % tid
            task.executor.MergeFrom(self.executor)
            # this is the master host
            task.data = self.ol_mstr + ':' + self.ol_mstr_ip

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

            driver.acceptOffers([offer.id], [operation])

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
            util.rm_host_from_cluster(host)
            util.rm_hosts(host)
            subprocess.check_output('/opt/openlava-2.2/bin/lsrmhost ' + host)

        if update.state == mesos_pb2.TASK_LOST or \
           update.state == mesos_pb2.TASK_KILLED or \
           update.state == mesos_pb2.TASK_FAILED:
            driver.abort()

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

    # TODO: authentication
    framework.principal = 'openlava-framework'
    driver = native.MesosSchedulerDriver(OpenLavaScheduler(executor),
                                         framework,
                                         'master:5050')
    status = 0 if driver.run() == mesos_pb2.DRIVER_STOPPED else 1

    time.sleep(120)
    driver.stop()

    sys.exit(status)
