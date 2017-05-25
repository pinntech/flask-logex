"""
Handles importing many of the core classes, methods and models of the project.

:copyright: (c) 2016 Pinn Technologies, Inc.
:license: All rights reserved
"""

import click
click.secho('>>> import os',
            fg='white')
import os  # NOQA
import sys  # NOQA
sys.path.append(os.getcwd())

click.secho('>>> import flask_logex',
            fg='white')
import flask_logex  # NOQA
click.secho('>>> from flask_logex import exceptions',
            fg='white')
from flask_logex import exceptions  # NOQA
click.secho('>>> from flask_logex import logger',
            fg='white')
from flask_logex import logger  # NOQA
click.secho('>>>',
            fg='white')
