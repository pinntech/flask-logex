#!/usr/bin/env python

from distutils.core import setup

with open("requirements.txt") as f:
    required = f.read().splitlines()

VERSION = '0.0.1'

setup(name='Flask-LogEx',
      version=VERSION,
      description='Flask Logging and Error Handling Extension.',
      author='Tim Co',
      author_email='tim@pinn.ai',
      url='https://github.com/tcco/flask-logex',
      packages=['flask_logex'],
      install_requires=required,

      # Packaging options:
      zip_safe=False,
      include_package_data=True,

      # Classifiers:
      platforms='any',
      classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Database',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: PyPy',
        ],

      )
