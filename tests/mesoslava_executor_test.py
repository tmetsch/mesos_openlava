"""
Unittest for executor module.
"""

import json
import time
import unittest

import mock

from tests import dummies

from mesoslava import executor


class OpenLavaExecutorTest(unittest.TestCase):
    """
    Test for class OpenLavaExecutor.
    """

    def setUp(self):
        task_info = {'master_hostname': 'master',
                     'master_ip': '10.1.1.10',
                     'agent_hostname': 'node1',
                     'agent_ip': '10.1.1.12'}

        self.driver = dummies.DummyDriver()
        self.task = mock.MagicMock()
        task_id = mock.MagicMock(value='123')
        self.task.task_id = task_id
        attrs = {'data': json.dumps(task_info)}
        self.task.configure_mock(**attrs)

        self.cut = executor.OpenLavaExecutor(dummies.DummyLava())

    # Tests for success.

    def test_launch_task_for_success(self):
        """
        Test for success.
        """
        self.cut.launchTask(self.driver, self.task)

    # Tests for failure.

    def test_launch_task_for_failure(self):
        """
        Test for failure.
        """
        pass

    # Tests for sanity.

    def test_launch_task_for_sanity(self):
        """
        Test for sanity.
        """
        self.cut.launchTask(self.driver, self.task)

        executor.TIMEOUT = 1
        executor.COUNT = 1

        time.sleep(1)

        # should call back that task is done.
        self.assertTrue(self.driver.stat_update_called >= 1)
