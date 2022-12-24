#!/bin/bash -eux

python3 -m pylint $(find . -name "*.py" -not -path "./collector/repos/*") --reports=yes --rcfile=.pylintrc
