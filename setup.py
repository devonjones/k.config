#!/usr/bin/env python
from setuptools import setup, Command

class PyTest(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        import sys,subprocess
        errno = subprocess.call([sys.executable, 'runtests.py'])
        raise SystemExit(errno)

def get_version():
	build_version = 1
	return build_version

setup(
	name='k.config',
	version='0.1.%s' % get_version(),
	url = 'https://wiki.knewton.net/index.php/Tech',
	author='Devon Jones',
	author_email='devon@knewton.com',
	license = 'Proprietary',
	packages=['k', 'k.config'],
    cmdclass = {'test': PyTest},
	install_requires=[
		'PyYAML>=3.09',
	],
	description = 'The knewton config library.',
	long_description = '\n' + open('README').read(),
)
