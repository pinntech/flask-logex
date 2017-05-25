"""
Management commands for the application.

:copyright: (c) 2016 Pinn Technologies, Inc.
:license: All rights reserved
"""

from shell import shell  # NOQA
from unit_tests import unit_tests  # NOQA

import click
import subprocess


@click.command()
@click.option('--eb', default=False, is_flag=True)
def install(eb):
    """Install requirements.txt in order for scientific prerequisites."""
    virtual = "virtualenv -p python2.7 .venv;"
    activate = ". .venv/bin/activate;"
    requirements = "cat requirements.txt | xargs pip install;"
    call = virtual + activate + requirements
    if eb:
        subprocess.call('echo "StrictHostKeyChecking=no" > /root/.ssh/config;', shell=True)
        activate = ". /opt/python/run/venv/bin/activate;"
        call = activate + requirements
    subprocess.call(call, shell=True)
