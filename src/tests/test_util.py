"""
Set of very simple test to verify the util routines work.
"""
__author__ = 'tmetsch'

import unittest

from mesoslava import util


class UnitTestCase(unittest.TestCase):
    """
    Test the util routines.
    """

    def test_add_host_to_cluster_for_sanity(self):
        """
        test addition an removal of hosts from lsf.cluster config file.
        """
        util.add_to_cluster_conf('foo', 'lsf.cluster.openlava')
        util.rm_from_cluster_conf('foo', 'lsf.cluster.openlava')

    def test_add_hosts_for_sanity(self):
        """
        test the handling of /etc/hosts.
        """
        util.add_to_hosts('foo', '192.168.0.1', filename='hosts')
        util.rm_from_hosts('foo', filename='hosts')
