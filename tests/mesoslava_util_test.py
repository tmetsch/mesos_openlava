"""
Set of very simple test to verify the util routines work.
"""

import os
import unittest

from mesoslava import lava_control

__author__ = 'tmetsch'


class UtilsTest(unittest.TestCase):
    """
    Test the util routines.
    """

    def test_add_host_to_cluster_for_sanity(self):
        """
        test addition an removal of hosts from lsf.cluster config file.
        """
        lava_control.add_to_cluster_conf('foo',
                                         os.sep.join(['tests', 'files',
                                                      'lsf.cluster.openlava']))
        lava_control.rm_from_cluster_conf('foo',
                                          os.sep.join(['tests', 'files',
                                                       'lsf.cluster.openlava']))

    def test_add_hosts_for_sanity(self):
        """
        test the handling of /etc/hosts.
        """
        lava_control.add_to_hosts('foo', '192.168.0.1',
                                  filename=os.sep.join(['tests', 'files',
                                                        'hosts']))
        lava_control.rm_from_hosts('foo',
                                   filename=os.sep.join(['tests', 'files',
                                                         'hosts']))
