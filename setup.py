import codecs
import os
import re
import ast
from setuptools import setup, find_packages

# Read version from __init__.py
_version_re = re.compile(r'__version__\s+=\s+(.*)')
with open('flask_logex/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

# Read readme file for description
if os.path.isfile('README.rst'):
    with codecs.open('README.rst', 'r', 'utf-8') as f:
        split = re.split('.. contents::', f.read())
        readme = split[1]

install_requirements = [
    'Flask>=0.12.1',
    'Flask-RESTful==0.3.5',
    'pytest>=2.9.2',
    'werkzeug==0.11.10',
]

extras_requirements = {
    'test': ['boto']
}


def setup_package():
    metadata = dict(
        name='Flask-LogEx',
        version=version,
        url='https://github.com/pinntech/flask-logex',
        description='Flask Logging and Error Handling Extension.',
        long_description=readme,
        author='Tim Co <tim@pinn.ai>, David Westerhoff <david@pinn.ai>',
        license='MIT',
        keywords='flask logging exceptions handling errors traceback',
        packages=find_packages(exclude=('tests', 'tests.*')),
        include_package_data=True,
        entry_points={
        },
        classifiers=[
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ],
        install_requires=install_requirements,
        extra_requires=extras_requirements,
    )
    setup(**metadata)


if __name__ == '__main__':
    setup_package()
