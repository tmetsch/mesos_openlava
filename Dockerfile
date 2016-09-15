FROM tmetsch/mesos_docker

# dependencies
RUN apt-get update --fix-missing
RUN apt-get install --no-install-recommends -y build-essential wget autoconf libncurses5-dev itcl3-dev tcl-dev python2.7

RUN update-ca-certificates -f && apt-get clean && rm -rf /var/lib/apt/lists/*

# install openlava
WORKDIR /tmp
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

ADD etc/lsf.* /opt/openlava-3.3/etc/
ADD etc/lsb.* /opt/openlava-3.3/etc/

RUN echo "source /opt/openlava-3.3/etc/openlava.sh" >> /root/.bashrc
RUN mkdir -p /home/openlava/
RUN touch /home/openlava/.bashrc
RUN echo "source /opt/openlava-3.3/etc/openlava.sh" >> /home/openlava/.bashrc

# Mesos DCOS service part
ADD mesoslava/ /tmp/mesoslava/
ADD bin/openlava_node.sh /tmp/

ENV PYTHONPATH=/usr/local/lib/python2.7/site-packages

WORKDIR /
