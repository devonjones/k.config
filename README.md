kconfig
========

Configuration library for shared config files across projects.

This package is used to centralize configuration into one place on eh file system in a way that can be shared across multiple languages.  All configuration is stored in yaml files, and there is a heirarchy of where the config library will search for these files.  While the name .knewton and /etc/knewton are the defaults, you can use any dierctories you wish.  The library will first search at . then ~/.knewton then /etc/knewton.

Usage
========

import kconfig

conf = kconfig.fetch_config("memcached/sessions.yml")

the .yml is optional: 

conf = kconfig.fetch_config("memcached/sessions")

If you want caching you can do:

conf = kconfig.Config().fetch_config("database/auth.yml")

If you would like to override the search path, before making any calls you can use:

kconfig.ConfigPath([".config", "~/.config", "/etc/config"])

And then follow on calls will search those paths in order instead.

If you want to inject a config via code, you would instead do this:

config = {
	'host': 'localhost',
	'port': 12345
}

kconfig.Config()._add_config(config, 'fake_config/not_here')

