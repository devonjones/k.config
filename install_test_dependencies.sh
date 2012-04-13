#!/bin/bash

# Install test and system-level runtime dependencies here.

set -e

sudo apt-get install -y python-setuptools python-yaml
sudo pip install pytest
sudo pip install coverage
sudo pip install pytest_cov
