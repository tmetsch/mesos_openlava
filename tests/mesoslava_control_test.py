"""
Unittest for TODO module.
"""

import time
import unittest

from mesoslava import control

from tests import dummies


class PIDControllerTest(unittest.TestCase):
    """
    Test for class PIDController.
    """

    def setUp(self):
        self.cut = control.PIDController(1.0, 1.0, 1.0)

    # Tests for success.

    def test_step_for_success(self):
        """
        Test for success.
        """
        self.cut.step(1.0)

    # Tests for failure.

    def test_step_for_failure(self):
        """
        Test for failure.
        """
        pass  # N/A

    # Tests for sanity.

    def test_step_for_sanity(self):
        """
        Test for sanity.
        """
        tmp = self.cut.step(1.0)
        self.assertEquals(tmp, 3.0)  # 1 * 1 + 1 * (1*1) + 1. * (1 - 0) / 1

        tmp = self.cut.step(1.0)  # 3  # dev = 0, i +1
        self.assertEquals(tmp, 3.0)
        tmp = self.cut.step(1.0)  # 4
        self.assertEquals(tmp, 4.0)
        tmp = self.cut.step(1.0)  # 5
        self.assertEquals(tmp, 5.0)


class Controller(unittest.TestCase):
    """
    Test for class Controller.
    """

    def setUp(self):
        self.scheduler = dummies.DummyScheduler()
        self.cut = control.Controller(self.scheduler)

    # Tests for success.

    def test_run_for_success(self):
        """
        Test for success.
        """
        self.cut.start()
        time.sleep(1)
        self.cut.done = True

    # Tests for failure.

    def test_run_for_failure(self):
        """
        Test for failure.
        """
        pass  # N/A

    # Tests for sanity.

    def test_run_for_sanity(self):
        """
        Test for sanity.
        """
        self.cut.start()
        time.sleep(15)  # needs some steps to get > 0.
        self.cut.done = True

        # expect that the goal on the scheduler has changed.
        self.assertEquals(self.scheduler.goal, 1.0)
