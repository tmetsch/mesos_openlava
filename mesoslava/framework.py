"""
OpenLava master run as the framework.
"""

import json
import sys
import uuid

from mesos import interface
from mesos.interface import mesos_pb2

from mesoslava import control
from mesoslava.ui import web

__author__ = 'tmetsch'


class OpenLavaScheduler(interface.Scheduler):
    """
    OpenLava Mesos scheduler.
    """

    def __init__(self, executor, lava_controller, start_ui=True):
        """
        Initialize the SHIM for OpenLava.
        """
        super(OpenLavaScheduler, self).__init__()

        # Mesos related stuff
        self.executor = executor
        self.accepted_tasks = {}
        self.running_tasks = {}

        # OpenLava related stuff
        self.lava_ctrl = lava_controller
        self.master_host = self.lava_ctrl.hostname
        self.master_ip = self.lava_ctrl.my_ip
        self.lava_ctrl.start_lava(True)

        # PID controller
        self.goal = 0
        self.controller = control.Controller(self)
        self.controller.start()

        # Fire up UI thread.
        if start_ui:
            web.Dashboard().start()

    def get_current(self):
        """
        Get current load indicator.
        """
        pending, running = self.lava_ctrl.get_job_info()
        if pending + running > 0.0:
            # Ratio of jobs running vs pending.
            ratio = (running * 1.) / \
                    (running + pending)
        else:
            # no jobs - gradually bring down value to 0.0.
            ratio = len(self.accepted_tasks) / 10.
        return ratio, pending

    def resourceOffers(self, driver, offers):
        """
        Apache Mesos invokes this to inform us about offers. We can accept
        or decline...
        """
        # TODO: add revive and suppressOffers to not constantly decline.
        # TODO: let's become smarter and grab only what we need in \
        #       future. - match pending jobs in queues to offers from mesos
        #       (e.g. GPUs).
        for offer in offers:
            if len(self.accepted_tasks) < self.goal:
                res_tag = None
                # ensure exclusive prio queue first.
                if self.lava_ctrl.get_queue_length('priority') >= 1:
                    res_tag = 'exl_prio'
                operation = self._process_offer(offer, res_tag)
                driver.acceptOffers([offer.id], [operation])
            else:
                # otherwise let's decline.
                driver.declineOffer(offer.id)

    def _process_offer(self, offer, resource_tag):
        """
        Grabs the offer from mesos and fires tasks.
        """
        agent_ip = offer.url.address.ip
        agent_hostname = offer.hostname

        res_offers = {}
        for resource in offer.resources:
            if resource.name not in res_offers:
                res_offers[resource.name] = resource.scalar.value

        task = self._create_task(offer.slave_id.value,
                                 agent_hostname,
                                 agent_ip,
                                 res_offers)

        operation = mesos_pb2.Offer.Operation()
        operation.type = mesos_pb2.Offer.Operation.LAUNCH
        operation.launch.task_infos.extend([task])

        if resource_tag is not None:
            res_offers[resource_tag] = 0.0
        self.accepted_tasks[agent_hostname] = res_offers

        return operation

    def _create_task(self, slave_id, agent_hostname, agent_ip, res_offers):
        """
        Create a task - grabs all offered resources for now.
        """
        # Create the task info obj.
        tid = uuid.uuid4()
        task = mesos_pb2.TaskInfo()
        task.task_id.value = str(tid)
        task.slave_id.value = slave_id
        task.name = 'OpenLava task %d' % tid
        task.executor.MergeFrom(self.executor)

        # add some data for the agent.
        task.data = json.dumps({'master_hostname': self.master_host,
                                'master_ip': self.master_ip,
                                'agent_hostname': str(agent_hostname),
                                'agent_ip': str(agent_ip)})

        for name in res_offers:
            tmp_res = task.resources.add()
            tmp_res.name = name
            tmp_res.type = mesos_pb2.Value.SCALAR
            tmp_res.scalar.value = res_offers[name]

        return task

    def statusUpdate(self, driver, status):
        """
        Called to tell us about the status of our task by Mesos.
        """
        tmp = json.loads(status.data.strip())
        host = tmp['agent_hostname']
        ip_addr = tmp['agent_ip']

        if host not in self.running_tasks:
            # We tell the master to only expose those shares it should
            # expose and not more - currently JOB_SLOTS = CPU offers.
            tmp = self.accepted_tasks[host]

            max_jobs = tmp['cpus']
            # WARN: OpenLava will only know about defined resource names.
            resource_tags = [item for item in tmp if item not in ['cpus',
                                                                  'mem',
                                                                  'disk',
                                                                  'ports']]
            resource_tag = ' '.join(resource_tags)

            self.lava_ctrl.add_host(host, ip_addr, True,
                                    max_jobs=max_jobs,
                                    resource_tags=resource_tag)

            self.running_tasks[host] = ip_addr
        elif status.state == mesos_pb2.TASK_FINISHED:
            self.lava_ctrl.rm_host(host, True)
            self.accepted_tasks.pop(host)
            self.running_tasks.pop(host)
        elif status.state == mesos_pb2.TASK_LOST \
                or status.state == mesos_pb2.TASK_KILLED \
                or status.state == mesos_pb2.TASK_FAILED:
            driver.abort()
            self.accepted_tasks.pop(host)
            self.running_tasks.pop(host)

        # TODO: use proper logging! & Generalize.
        print('Current queue length (normal): {0}'.
              format(self.lava_ctrl.get_queue_length('normal')))
        print('Current queue length (priority): {0}'.
              format(self.lava_ctrl.get_queue_length('priority')))
        print('Current number of hosts: {0}'.
              format(str(len(self.lava_ctrl.get_hosts()) - 2)))
        print('Current goal for # of tasks: {0}'.
              format(self.goal))

        sys.stdout.flush()
