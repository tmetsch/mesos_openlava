__author__ = 'tmetsch'

import unittest

from mesoslava import util

class UnitTestCase(unittest.TestCase):

    def test_add_host_for_sanity(self):
        util.add_host_to_cluster('foo', 'lsf.cluster.openlava')
        util.rm_host_from_cluster('foo', 'lsf.cluster.openlava')
