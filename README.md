# OpenLava as DCOS service for Apache Mesos

***Note***: this is very much work in progress! Feel free to help :-)

to run this stuff:

    $ docker-compose -p tmetsch up

This will start a mesos-master, 1 mesos-slave and the
[OpenLava](http://openlava.org) master framework. It is a "simulated"
distributed environment for testing only atm. The idea for integrating
openlava on Mesos is the following:

As long as the queues are empty reject offers from mesos OR if a queues has
pending jobs offers are accepted and the openlava services are started as a
task.

Tasks are completed in case they are idle for a while.

Openlava itself could make use of firing up docker containers to run the
actual workload.

There are several docker images being used here:

* the Apache Mesos & Marathon images from  this
 [repo](https://github.com/tmetsch/docker_compose_mesos).
* based on the previous one an image is defined which combines OpenLava & the
OpenLava framework (this could be split into two to be more
lightweight)

## testing

You can scale the Mesos cluster by running:

    $ docker-compose -p tmetsch scale node1=10    

To submit jobs:

    $ docker exec -u openlava tmetsch_openlavamaster_1 /opt/openlava-3.1/bin/bsub -J "myArray[1-100]" /bin/sleep 3

To list jobs:

    $ docker exec -u openlava tmetsch_openlavamaster_1 /opt/openlava-3.1/bin/bjobs

To watch the current hosts (Mesos Tasks) in the OpenLava cluster:

    $ watch docker exec -u openlava tmetsch_openlavamaster_1 /opt/openlava-3.1/bin/bhosts

In the meantime feel free to see the openlava cluster shrink and grow based on 
demand :-)

