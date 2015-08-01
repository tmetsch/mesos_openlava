FROM devopsmesos_master

# dependecies
RUN apt-get update --fix-missing
RUN apt-get install -y build-essential wget autoconf libncurses5-dev itcl3-dev tcl

# install openlava
RUN wget http://www.openlava.org/tarball/openlava-2.2.tar.gz

RUN tar -xzvf openlava-2.2.tar.gz
WORKDIR openlava-2.2/

RUN ./configure
RUN make
RUN make install

RUN cd config; cp lsb.hosts lsb.params lsb.queues lsb.users lsf.cluster.openlava lsf.conf lsf.shared openlava.* /opt/openlava-2.2/etc

RUN useradd -r openlava

RUN chown -R openlava:openlava /opt/openlava-2.2
RUN cp /opt/openlava-2.2/etc/openlava /etc/init.d
RUN cp /opt/openlava-2.2/etc/openlava.* /etc/profile.d

ADD lsf.cluster.openlava /opt/openlava-2.2/etc/

RUN echo "source /opt/openlava-2.2/etc/openlava.sh" >> /root/.bashrc
RUN mkdir -p /home/openlava/
RUN touch /home/openlava/.bashrc
RUN echo "source /opt/openlava-2.2/etc/openlava.sh" >> /home/openlava/.bashrc

ADD src /tmp

ENV PYTHONPATH=/mesos-0.23.0/build/3rdparty/libprocess/3rdparty/protobuf-2.5.0/python/build/lib.linux-x86_64-2.7:/mesos-0.23.0/build/3rdparty/distribute-0.6.26:/mesos-0.23.0/build/src/python/dist/mesos.native-0.23.0-py2.7-linux-x86_64.egg:/mesos-0.23.0/build/src/python/dist/mesos.interface-0.23.0-py2.7.egg

WORKDIR /mesos-0.23.0/build