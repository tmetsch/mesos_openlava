"""
Unittest for TODO module.
"""

import unittest

import mock  # py 3 -> unittest.mock
from mesos.interface import mesos_pb2

from tests import dummies
from mesoslava import framework


class OpenLavaSchedulerTest(unittest.TestCase):
    """
    Test for class .
    """

    def setUp(self):
        self.driver = dummies.DummyDriver()

        executor = mesos_pb2.ExecutorInfo()

        offer = mock.Mock()
        attrs = {'hostname': 'node1'}
        offer.configure_mock(**attrs)
        slave_id = mock.MagicMock(value='123')
        attrs = {'name': 'cpus'}
        resource = mock.MagicMock()
        resource.configure_mock(**attrs)
        resources = [resource]
        offer.slave_id = slave_id
        offer.resources = resources

        self.update = mock.MagicMock()
        attrs = {'data': '{"agent_hostname": "node1", '
                         '"agent_ip": "10.1.1.12"}'}
        self.update.configure_mock(**attrs)

        self.offers = [offer]

        self.cut = framework.OpenLavaScheduler(executor,
                                               dummies.DummyLava(),
                                               start_ui=False)
        # stop the controller & manually set goal
        self.cut.controller.done = True
        self.cut.goal = 1

    def test_resource_offers_for_success(self):
        """
        Test for success.
        """
        self.cut.resourceOffers(self.driver, self.offers)

    def test_status_update_for_success(self):
        """
        Test for success.
        """
        self.cut.resourceOffers(self.driver, self.offers)
        self.cut.statusUpdate(self.driver, self.update)

    def test_resource_offers_for_failure(self):
        """
        Test for failure.
        """
        # N/A

    def test_status_update_for_failure(self):
        """
        Test for failure.
        """
        self.cut.resourceOffers(self.driver, self.offers)
        self.cut.statusUpdate(self.driver, self.update)

        # let's call home and claim we failed
        self.update.state = mesos_pb2.TASK_FAILED
        self.cut.statusUpdate(self.driver, self.update)

        # assure we cleaned up.
        self.assertNotIn('node1', self.cut.accepted_tasks)
        self.assertNotIn('node1', self.cut.running_tasks)

        # driver should abort.
        self.assertTrue(self.driver.abort_called == 1)

    def test_resource_offers_for_sanity(self):
        """
        Test for sanity.
        """
        self.cut.resourceOffers(self.driver, self.offers)

        # should fill accepted tasks dictionaries
        self.assertIn('node1', self.cut.accepted_tasks)
        # task has not reported home yet...
        self.assertTrue(len(self.cut.running_tasks) == 0)

        # ensure driver got called with accept.
        self.assertTrue(self.driver.accept_called == 1)
        print self.driver.decline_called
        self.assertTrue(self.driver.decline_called == 0)

    def test_status_update_for_sanity(self):
        """
        Test for sanity.
        """
        # offer some resources
        self.cut.resourceOffers(self.driver, self.offers)

        # let the task call home...
        self.cut.statusUpdate(self.driver, self.update)

        # should fill running tasks dict.
        self.assertIn('node1', self.cut.running_tasks)

        # let's call home and claim we are done.
        self.update.state = mesos_pb2.TASK_FINISHED
        self.cut.statusUpdate(self.driver, self.update)

        # assure we cleaned up.
        self.assertNotIn('node1', self.cut.accepted_tasks)
        self.assertNotIn('node1', self.cut.running_tasks)
