# OpenLava as DCOS service for Apache Mesos

***Note***: very much work in progress! Feel free to help :-)

to run this stuff:

    $ docker-compose up

This will start a mesos-master, mesos-slaves and the [openlava](http://openlava.org) master. It is a "simulated" distributed environment for testing only atm. The idea for integrating openlava on mesos is the following:

As long as the queues are empty reject offers from mesos & remove ideling compute nodes in openlava OR if the queues are full accept offers and fire up openlava service as task (in case no lava service is running on that host already).

Openlava itself could make use of firing up docker containers to run the actual workload.

There are several docker images being used here:

* the Apache Mesos & Marathon images from  this [repo](https://github.com/tmetsch/docker_compose_mesos).
* based on the previous one an image is defined which incapsulates the OpenLava & the OpenLave framework (this could be split into two to be more lightweight)

## Status

OpenLava service get started - LIMs detect each other bhosts reports state
