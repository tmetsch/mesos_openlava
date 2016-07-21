FROM tmetsch/mesos_docker

# dependencies
RUN apt-get update --fix-missing
RUN apt-get install --no-install-recommends -y build-essential wget autoconf libncurses5-dev itcl3-dev tcl-dev

RUN update-ca-certificates -f && apt-get clean && rm -rf /var/lib/apt/lists/*

# install openlava
RUN wget http://www.openlava.org/tarball/openlava-3.3.tar.gz

RUN tar -xzvf openlava-3.3.tar.gz
WORKDIR openlava-3.3/

RUN ./configure
RUN make
RUN make install

RUN cd config; cp lsb.hosts lsb.params lsb.queues lsb.users lsf.cluster.openlava lsf.conf lsf.shared openlava.* /opt/openlava-3.3/etc
RUN useradd -r openlava

RUN chown -R openlava:openlava /opt/openlava-3.3
RUN cp /opt/openlava-3.3/etc/openlava /etc/init.d
RUN cp /opt/openlava-3.3/etc/openlava.* /etc/profile.d

ADD etc/lsf.cluster.openlava /opt/openlava-3.3/etc/
ADD etc/lsb.* /opt/openlava-3.3/etc/

RUN echo "source /opt/openlava-3.3/etc/openlava.sh" >> /root/.bashrc
RUN mkdir -p /home/openlava/
RUN touch /home/openlava/.bashrc
RUN echo "source /opt/openlava-3.3/etc/openlava.sh" >> /home/openlava/.bashrc

# Mesos DCOS service part
ADD mesoslava/ /tmp/mesoslava/
ADD bin/openlava_node.sh /tmp/

ENV PYTHONPATH=/mesos-0.28.2/build/3rdparty/libprocess/3rdparty/protobuf-2.5.0/python/build/lib.linux-x86_64-2.7:/mesos-0.28.2/build/3rdparty/distribute-0.6.27:/mesos-0.28.2/build/src/python/dist/mesos.native-0.28.2-py2.7-linux-x86_64.egg:/mesos-0.28.2/build/src/python/dist/mesos.interface-0.28.2-py2.7.egg

WORKDIR /mesos-0.28.2/build
