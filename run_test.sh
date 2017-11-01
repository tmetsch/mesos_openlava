#!/bin/bash

pep8 -r mesoslava/*.py tests/*.py

pylint -r n mesoslava/*.py tests/*.py

nosetests --with-coverage --cover-package mesoslava
