"""
Module holding all control theory related stuff.
"""

import threading
import time

__author__ = 'tmetsch'

TARGET = 0.3  # TODO: make configurable.
TIMEOUT = 1


class PIDController(object):
    """
    A PID controller.
    """

    def __init__(self, prop_gain, int_gain, dev_gain, clamp=(0, 100)):
        # P/I/D gains
        self.prop_gain = prop_gain
        self.int_gain = int_gain
        self.dev_gain = dev_gain

        self.i = 0
        self.d = 0
        self.prev = 0

        self.unclamped = True
        self.low, self.high = clamp

    def step(self, error):
        """
        Calculate next goal based on the previous error.
        """
        if self.unclamped:
            self.i += TIMEOUT * error
        self.d = (error - self.prev) / TIMEOUT

        goal = \
            self.prop_gain * error + \
            self.int_gain * self.i + \
            self.dev_gain * self.d

        self.unclamped = (self.low < goal < self.high)
        self.prev = error

        return goal


class Controller(threading.Thread):
    """
    Simple Thread based controller.
    """

    def __init__(self, scheduler):
        super(Controller, self).__init__()

        self.scheduler = scheduler

        # TODO: tune using e.g. AMIGO, Cohen, etc.
        self.pid_ctrl = PIDController(1.0, 0.2, 0.01, clamp=(0, 100))
        self.target = 0.0
        self.current = 0.0

        self.done = False

    def run(self):
        while not self.done:
            error = self.target - self.current
            goal = self.pid_ctrl.step(error)
            self.current, pending = self.scheduler.get_current()

            if pending > 0:
                self.target = 0.3
            else:
                self.target = 0.0

            self.scheduler.goal = max(0., int(goal))

            time.sleep(TIMEOUT)
