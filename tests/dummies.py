"""
Dummies for testing.
"""

__author__ = 'tmetsch'


class DummyDriver(object):
    """
    Dummy Mesos driver.
    """

    def __init__(self):
        self.decline_called = 0  # number of time decline got called.
        self.accept_called = 0  # number of time accept got called.
        self.abort_called = 0  # number of time abort got called.
        self.stat_update_called = 0

    def acceptOffers(self, iden_list, operation_list):  # nopep8 - mesos' fault
        """
        Accept offer.
        """
        self.accept_called += 1

    def declineOffer(self, offer_iden):  # nopep8 - mesos' fault
        """
        Decline offer.
        """
        self.decline_called += 1

    def abort(self):
        """
        Abort.
        """
        self.abort_called += 1

    def sendStatusUpdate(self, status):  # nopep8 - mesos' fault
        """
        Status update.
        """
        self.stat_update_called += 1


class DummyLava(object):
    """
    Dummy implementation of OpenLava control interface.
    """

    def __init__(self, is_master=True):
        """
        Init.
        """
        self.hostname = 'foo'
        self.my_ip = '10.1.1.2'
        self.queue_length = 11
        self.hosts = {'foo': {'is_master': True}}
        self.is_running = False

    def add_host(self, host, ip_addr, is_master,
                 max_jobs=None, resource_tags=None):
        """
        Add a host to the cluster.
        """
        self.hosts[host] = resource_tags

    def rm_host(self, host, is_master):
        """
        remove host from cluster.
        """
        self.hosts.pop(host)

    def start_lava(self, is_master):
        """
        start lava
        """
        self.is_running = True

    def stop_lava(self):
        """
        stop lava.
        """
        self.is_running = False

    def get_queue_length(self, queue):
        """
        Return queue length.
        """
        return self.queue_length

    def get_job_info(self):
        """
        Return job info.
        """
        return self.queue_length, 1

    def get_hosts(self):
        """
        Return current available hosts.
        """
        return self.hosts

    def host_njobs(self, hostname):
        """
        Return jos per host.
        """
        return 0


class DummyScheduler(object):
    """
    Dummy Scheduler.
    """

    def __init__(self):
        """
        Init.
        """
        self.goal = 0.0

    def get_current(self):
        """
        Return some dummy info.
        """
        return 0.01, 100
