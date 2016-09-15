"""
Set of helpers routines called by both the framework and executor.
"""

import socket
import subprocess

__author__ = 'tmetsch'

# TODO: this file is one big pain in the a**. Should work with proper
# python API calls instead of calling subprocess.

OPENLAVA_PATH = '/opt/openlava-3.3'


def get_ip(hostname):
    """
    Return ip of a given host..
    """
    hname = socket.gethostbyname(hostname)
    return hname


def start_lava(is_master=False):
    """
    Fire up the openlava service.
    """
    # TODO: very poor approach for now
    hostname = subprocess.check_output('hostname').rstrip()

    add_to_cluster_conf(hostname)
    subprocess.check_output([OPENLAVA_PATH + '/sbin/lim'],
                            env={'LSF_ENVDIR': OPENLAVA_PATH + '/etc'})
    subprocess.check_output([OPENLAVA_PATH + '/sbin/res'],
                            env={'LSF_ENVDIR': OPENLAVA_PATH + '/etc'})
    subprocess.check_output([OPENLAVA_PATH + '/sbin/sbatchd'],
                            env={'LSF_ENVDIR': OPENLAVA_PATH + '/etc'})
    if is_master:
        subprocess.check_output([OPENLAVA_PATH + '/bin/badmin', 'hclose',
                                 hostname],
                                env={'LSF_ENVDIR': OPENLAVA_PATH + '/etc'})
    return hostname


def stop_lava():
    """
    Kill Openlava processes.
    """
    subprocess.check_output(['pkill', 'lim'])
    subprocess.check_output(['pkill', 'pim'])
    subprocess.check_output(['pkill', 'res'])
    subprocess.check_output(['pkill', 'sbatchd'])
    subprocess.check_output(['pkill', '-SIGCHLD', 'mesos-slave'])


def get_queue_length(queue='normal'):
    """
    Get the length pending jobs in a queue.
    """
    tmp = subprocess.check_output([OPENLAVA_PATH + '/bin/bqueues',
                                   queue]).split('\n')[1]
    lst = [elem for elem in tmp.split(' ') if len(elem) is not 0]
    return int(lst[8])


def njobs_per_host(hostname):
    """
    Return number of jobs for a given host.
    """
    tmp = subprocess.check_output([OPENLAVA_PATH + '/bin/bhosts',
                                   hostname]).split('\n')[1]
    lst = [elem for elem in tmp.split(' ') if len(elem) is not 0]
    return int(lst[4])


def get_bhosts():
    """
    Return an array with info about the current hosts in the cluster.
    """
    tmp_str = subprocess.check_output([OPENLAVA_PATH + '/bin/bhosts'])
    return _parse_output(tmp_str)


def get_bqueues():
    """
    Return an array with info about the current queues.
    """
    tmp_str = subprocess.check_output([OPENLAVA_PATH + '/bin/bqueues'])
    return _parse_output(tmp_str)


def get_clusters():
    """
    Return an array with info about the accessible clusters.
    """
    tmp_str = subprocess.check_output([OPENLAVA_PATH + '/bin/lsclusters'])
    return _parse_output(tmp_str)


def get_hosts_load():
    """
    Return an array with load info about the current hosts in the cluster.
    """
    tmp_str = subprocess.check_output([OPENLAVA_PATH + '/bin/lsload'])
    return _parse_output(tmp_str)


def get_hosts():
    """
    Return an array with load info about the current hosts in the cluster.
    """
    tmp_str = subprocess.check_output([OPENLAVA_PATH + '/bin/lshosts'])
    return _parse_output(tmp_str)


def add_to_cluster_conf(hostname,
                        filename=OPENLAVA_PATH + '/etc/lsf.cluster.openlava'):
    """
    Adds a hostname to the lsf.cluster config file.
    """
    filep = open(filename, 'r')
    cache = []
    for line in filep.readlines():
        if line.find('End     Host') == 0:
            new = '{} {:>17} {:>14} {:>5} {:>7} {:>7} ' \
                  '\n'.format(hostname, '!', '!', '1', '-', '-')
            cache.append(new)
        cache.append(line)
    with open(filename, 'w') as filep:
        filep.writelines(cache)


def rm_from_cluster_conf(hostname,
                         filename=OPENLAVA_PATH + '/etc/lsf.cluster.openlava'):
    """
    Removes a hostname to the lsf.cluster config file.
    """
    filep = open(filename, 'r')
    cache = []
    for line in filep.readlines():
        if line.find(hostname) == 0:
            pass
        else:
            cache.append(line)
    with open(filename, 'w') as filep:
        filep.writelines(cache)


def add_host_to_cluster(hostname, max_jobs=0, resources=None, model=None):
    """
    Add a host to the cluster.
    """
    cmd = [OPENLAVA_PATH + '/bin/lsaddhost']
    if max_jobs > 0:
        cmd.extend(['-M', str(max_jobs)])
    if resources is not None:
        cmd.extend(['-R', resources])
    if model is not None:
        cmd.extend(['-m', model])
    cmd.append(hostname)
    subprocess.check_output(cmd)


def rm_host_from_cluster(hostname):
    """
    Remove a host from the cluster.
    """
    subprocess.check_output([OPENLAVA_PATH + '/bin/lsrmhost', hostname])

# TODO: Following should be replaced with DNS stuff imho.


def add_to_hosts(hostname, ip_addr, filename='/etc/hosts'):
    """
    Adds a hostname to /etc/hosts - openlava is very picky about this :-/
    """
    with open(filename, 'a') as filep:
        filep.write(ip_addr + '\t' + hostname + '\n')
    filep.close()


def rm_from_hosts(hostname, filename='/etc/hosts'):
    """
    Removes a hostname from /etc/hosts - openlava is very picky about this :-/
    """
    filep = open(filename, 'r')
    cache = []
    for line in filep.readlines():
        if line.find(hostname) > 0:
            pass
        else:
            cache.append(line)
    with open(filename, 'w') as filep:
        filep.writelines(cache)
    filep.close()


def _parse_output(tmp_str):
    """
    Parses the output from lava commans into lists.
    """
    tmp = []
    for line in tmp_str.split('\n'):
        if len(line) == 0:
            continue
        tmp.append([item for item in line.split(' ') if len(item.strip()) > 0])
    return tmp
