# OpenLava as DCOS service for Apache Mesos

***Note***: very much work in progress! Feel free to help :-) Mostly here
for me to play & learn Apache Mesos APIs and behaviours.

to run this stuff:

    $ docker-compose up

This will start a mesos-master, mesos-slaves and the
[openlava](http://openlava.org) master. It is a "simulated" distributed
environment for testing only atm. The idea for integrating openlava on
Mesos is the following:

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

Do another docker run (make sure the host is set to 'testnode') which links to
the openlava framework - and run the mesos slave in background:

    $ docker run -h testnode --link mesosopenlava_master_1:master -i -t mesosopenlava_node2 /bin/bash
    root@testnode:/mesos-0.23.0/build# nohup ./bin/mesos-slave.sh --master=master:5050 &

Within you can now fire up jobs after a while as user *openlava*:

    $ su openlava
    $ bsub /bin/sleep 10

While waiting feel free to scale the node1 with docker-compose & watch the
openlava cluster grow & shrink:

    $ docker-compose scale node1=10