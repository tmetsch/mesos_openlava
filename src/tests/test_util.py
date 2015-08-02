__author__ = 'tmetsch'

import unittest

from mesoslava import util


class UnitTestCase(unittest.TestCase):

    def test_add_host_to_cluster_for_sanity(self):
        """
        test addition an removal of hosts from lsf.cluster config file.
        """
        util.add_host_to_cluster('foo', 'lsf.cluster.openlava')
        util.rm_host_from_cluster('foo', 'lsf.cluster.openlava')

    def test_add_hosts_for_sanity(self):
        """
        test the handling of /etc/hosts.
        """
        util.add_hosts('foo', '192.168.0.1', filename='hosts')
        util.rm_hosts('foo', filename='hosts')
