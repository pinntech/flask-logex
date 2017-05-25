"""
Run the unit test suite on the application.

:copyright: (c) 2016 Pinn Technologies, Inc.
:license: All rights reserved
"""

import click
import subprocess


@click.command()
@click.argument('unit', default=False)
def unit_tests(unit):
    """Run the unit testing suite on the application."""
    root = './tests/'

    call = ['python', '-m', 'pytest', root]

    if unit:
        call[-1] = call[-1] + 'test_{}.py'.format(unit)
    click.secho('+\n++\n+++ Testing unit {}...'.format(call[-1]), fg='white')

    pytest_return_value = subprocess.call(call)

    return pytest_return_value


if __name__ == '__main__':
    unit_tests()
