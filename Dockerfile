FROM tmetsch/mesos_docker

# dependencies
RUN apt-get update
RUN apt-get install --no-install-recommends -y build-essential wget autoconf libncurses5-dev itcl3-dev tcl-dev python2.7 automake

RUN update-ca-certificates -f && apt-get clean && rm -rf /var/lib/apt/lists/*

# install openlava
WORKDIR /tmp
# RUN wget http://www.openlava.org/tarball/openlava-2.2.tar.gz
# RUN tar -xzvf openlava-2.2.tar.gz
ADD openlava-2.2 /tmp/openlava-2.2
WORKDIR openlava-2.2

RUN ./bootstrap.sh
RUN ./configure
RUN make
RUN make install

RUN cd config; cp lsb.hosts lsb.params lsb.queues lsb.users lsf.cluster.openlava lsf.conf lsf.shared openlava.* /opt/openlava-2.2/etc
RUN useradd -r openlava
RUN usermod -aG docker openlava

RUN chown -R openlava:openlava /opt/openlava-2.2
RUN cp /opt/openlava-2.2/etc/openlava /etc/init.d
RUN cp /opt/openlava-2.2/etc/openlava.* /etc/profile.d

ADD etc/lsf.* /opt/openlava-2.2/etc/
ADD etc/lsb.* /opt/openlava-2.2/etc/

ADD bin/elim /opt/openlava-2.2/sbin/

RUN echo "source /opt/openlava-2.2/etc/openlava.sh" >> /root/.bashrc
RUN mkdir -p /home/openlava/
RUN touch /home/openlava/.bashrc
RUN echo "source /opt/openlava-2.2/etc/openlava.sh" >> /home/openlava/.bashrc

# Mesos DCOS service part
ADD mesoslava/ /tmp/mesoslava/
ADD bin/executor.py /tmp/
ADD bin/scheduler.py /tmp/

ENV PYTHONPATH=/usr/local/lib/python2.7/site-packages

WORKDIR /
