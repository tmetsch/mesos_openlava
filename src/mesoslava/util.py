__author__ = 'tmetsch'

# TODO: this file is one big pain in the a**.

import subprocess


def get_ip():
    '''
    Return the ip address.
    '''
    fp = open('/etc/hosts')
    tmp = fp.readline()
    tmp = tmp.split('\t')
    return tmp[1], tmp[0]


def start_lava(openlava_path):
    '''
    Fire up the openlava service.
    '''
    # TODO: very poor approach for now
    hostname = subprocess.check_output('hostname').rstrip()

    # TODO: configure so that master doesn't take jobs.
    add_host_to_cluster(hostname)
    msg = subprocess.check_output([openlava_path + '/sbin/lim'],
                                  env={'LSF_ENVDIR': '/opt/openlava-2.2/etc'})
    msg = subprocess.check_output([openlava_path + '/sbin/res'],
                                  env={'LSF_ENVDIR': '/opt/openlava-2.2/etc'})
    msg = subprocess.check_output([openlava_path + '/sbin/sbatchd'],
                                  env={'LSF_ENVDIR': '/opt/openlava-2.2/etc'})
    return hostname


def get_queue_length(openlava_path, queue='normal'):
    '''
    Get the length pending jobs in a queue.
    '''
    tmp = subprocess.check_output([openlava_path + '/bin/bqueues',
                                   queue]).split('\n')[1]
    lst = [elem for elem in tmp.split(' ') if len(elem) is not 0]
    return int(lst[8])


def njobs_per_host(openlava_path, hostname):
    '''
    Return number of jobs for a given host.
    '''
    tmp = subprocess.check_output([openlava_path + '/bin/bhosts',
                                   hostname]).split('\n')[1]
    lst = [elem for elem in tmp.split(' ') if len(elem) is not 0]
    return int(lst[4])


def add_host_to_cluster(hostname,
                        filename='/opt/openlava-2.2/etc/lsf.cluster.openlava'):
    '''
    Adds a hostname to the lsf.cluster config file.
    '''
    fp = open(filename, 'r')
    cache = []
    pos = False
    for line in fp.readlines():
        if line.find('End     Host') == 0:
            new = '{} {:>17} {:>14} {:>5} {:>7} {:>7} ' \
                  '\n'.format(hostname, '!', '!', '1', '-', '-')
            cache.append(new)
        cache.append(line)
    with open(filename, 'w') as file:
        file.writelines(cache)


def rm_host_from_cluster(hostname,
                         filename='/opt/openlava-2.2/etc/lsf.cluster.openlava'):
    '''
    Removes a hostname to the lsf.cluster config file.
    '''
    fp = open(filename, 'r')
    cache = []
    for line in fp.readlines():
        if line.find(hostname) == 0:
            pass
        else:
            cache.append(line)
    with open(filename, 'w') as file:
        file.writelines(cache)


# TODO: Following should be replaced with DNS stuff imho.


def add_hosts(hostname, ip, filename='/etc/hosts'):
    '''
    Adds a hostname to /etc/hosts - openlava is very picky about this :-/
    '''
    with open(filename, 'a') as file:
        file.write(ip + '\t' + hostname + '\n')
    file.close()


def rm_hosts(hostname, filename='/etc/hosts'):
    '''
    Removes a hostname from /etc/hosts - openlava is very picky about this :-/
    '''
    fp = open(filename, 'r')
    cache = []
    for line in fp.readlines():
        print line.find(hostname)
        if line.find(hostname) > 0:
            pass
        else:
            cache.append(line)
    with open(filename, 'w') as file:
        file.writelines(cache)
    file.close()
