#!/usr/bin/env python
from setuptools import setup

setup(
	name='k.config',
	version='0.1', # TODO: replace on build, with build number.
	url = 'https://wiki.knewton.net/index.php/Tech',
	author='Devon Jones',
	author_email='devon@knewton.com',
	license = 'Proprietary',
	packages=['k', 'k.config'],
	install_requires=[
		'PyYAML>=3.09',
	],
	#tests_require=[
	#	'cov-core>=1.3,<2.0',
	#	'coverage>=3.5.1,<3.6',
	#	'mock>=0.7.2,<0.8',
	#	'py>=1.4.6,<1.5',
	#	'pytest>=2.2.1,<2.3',
	#	'pytest-cov>=1.5,<1.6',
	#],
	description = 'The knewton config library.',
	long_description = '\n' + open('README').read(),
)
