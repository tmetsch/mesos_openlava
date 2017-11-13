# OpenLava as DCOS service for Apache Mesos

***Note***: this is very much work in progress! Feel free to help :-)

to run this stuff:

    $ docker-compose -p tmetsch up

This will start a mesos-master, mesos-agents and the
[OpenLava](http://openlava.org) master framework. It is a "simulated"
distributed environment for testing only atm. The idea for integrating
Openlava on Mesos is the following:

As long as the queues are empty reject offers from mesos OR if a queues has
pending jobs offers are accepted and the openlava services are started as a
task. This is done with the help of a simple PID controller.

Tasks are completed in case they are idle for a while.

Openlava itself could make use of firing up docker containers to run the
actual workload.

There are several docker images being used here:

* the Apache Mesos & Marathon images from  this
 [repo](https://github.com/tmetsch/docker_compose_mesos).
* based on the previous one an image is defined which combines OpenLava & the
OpenLava framework (this could be split into two to be more
lightweight)

## Testing

To submit jobs:

    $ docker exec -u openlava tmetsch_openlavamaster_1 \ 
      /opt/openlava-2.2/bin/bsub -J "myArray[1-100]" /bin/sleep 3

To list jobs:

    $ docker exec -u openlava tmetsch_openlavamaster_1 \ 
      /opt/openlava-2.2/bin/bjobs

To watch the current hosts (Mesos Tasks) in the OpenLava cluster:

    $ watch docker exec -u openlava tmetsch_openlavamaster_1 \
      /opt/openlava-2.2/bin/bhosts

In the meantime feel free to see the openlava cluster shrink and grow based on 
demand :-)

## Important note

OpenLava 2.2 currently requires [this](https://github.com/openlava/2.2/pull/2) 
patch to assure only the offered CPUs are being used.
