#!/usr/bin/env python
# -*- coding: utf-8 -*-

from glob import glob

from setuptools import find_packages
from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

extras_require = {}
extras_require[':python_version<="3.5"'] = ['typing']
requirements = [
    'Click>=6.0',
    'jsonschema',
]


setup(
    name='copyrite',
    version='0.1.0',
    description="Updates copyright notices.",
    long_description=readme + '\n\n' + history,
    author="Claudiu Popa",
    author_email='pcmanticore@gmail.com',
    url='https://github.com/PCManticore/copyrite',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    entry_points={
        'console_scripts': [
            'copyrite=copyrite.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    extras_require=extras_require,
    license="MIT license",
    zip_safe=False,
    keywords='copyrite',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
)
