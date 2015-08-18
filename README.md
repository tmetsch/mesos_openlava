# OpenLava as DCOS service for Apache Mesos

***Note***: very much work in progress! Feel free to help :-) I use this
to learn Apache Mesos' APIs & behaviours.

to run this stuff:

    $ docker-compose up

This will start a mesos-master, 1 mesos-slave and the
[openlava](http://openlava.org) master frameowkr. It is a "simulated"
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
* based on the previous one an image is defined which incapsulates the
OpenLava & the OpenLava framework (this could be split into two to be more
lightweight)

## testing

You can scale the Mesos cluster by running:

    $ docker-compose scale node1=10    

To submit jobs:

    $ docker exec -u openlava mesosopenlava_openlavamaster_1 /opt/openlava-2.2/bin/bsub -J "myArray[1-100]" /bin/sleep 1

To list jobs:

    $ docker exec -u openlava mesosopenlava_openlavamaster_1 /opt/openlava-2.2/bin/bjobs

In the meantime feel free to see the openlava cluster shrink and grow based on 
demand :-)
