#!/bin/sh

# XXX: bit of a hack - assuming mesos dump libs here. need to be done as
# from mesos 1.0 on it doesn'T seem like env vars get copied to the executor.
export PYTHONPATH=/usr/local/lib/python2.7/site-packages

python2.7 /tmp/mesoslava/executor.py
