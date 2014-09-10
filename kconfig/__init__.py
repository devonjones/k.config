"""
Classes and finctions that implement the config paradigm for Knewton.
"""

import os
import copy
import yaml

class ConfigPathDefaults(object):
	"""
	This class is a singleton intended to hold the paths that will be looked at,
	in order, for finding config files.
	If you want to override the defaults of [".", "~/.knewton", "/etc/knewton"],
	do the following:
	import kconfig
	MyConfigPath = kconfig.ConfigPathDefaults(
		[os.path.abspath("config/tests/configs")])
	MyConfig = kconfig.ConfigDefault(config_path=MyConfigPath)
	"""
	def __init__(self, pathlist=None):
		if not pathlist:
			pathlist = [
				"",
				os.path.join('~', '.knewton'),
				'/etc/knewton/']
		self.prefixes = pathlist

	def __call__(self):
		return self

ConfigPath = ConfigPathDefaults()

def find_config_path(file_name, config_path=None):
	"""
	Not intended for calling outside of this module.
	This function will look in all paths, in order
	for the requested file both with and without .yml
	Parameters:
	 - file_name: the file name to search for.
	Raises:
	 - IOError if no file is found
	"""
	if not config_path:
		config_path = ConfigPath
	for prefix in config_path.prefixes:
		file_path = os.path.expanduser(os.path.join(prefix, file_name))
		if os.path.exists(file_path):
			return file_path
		if os.path.exists(file_path + ".yml"):
			return file_path + ".yml"
	raise IOError("Config file %s does not exist" % (file_name))

def fetch_config(default, config=None, config_path=None):
	"""
	Returns the content of a yml config file as a hash
	Parameters:
	 - default: default file name to look for
	 - config: override with this file name instead. (optional)
	   Note: the pattern of using config is intended to make using this with
	   OptionsParser easier.  Otherwise, generally ignore the use of the
	   config argument.
	Raises:
	 - IOError if no file is found
	"""
	if not config_path:
		config_path = ConfigPath
	retcfg = default
	if config:
		retcfg = config
	return yaml.load(file(find_config_path(retcfg, config_path=config_path)))

def fetch_config_mtime(default, config=None, config_path=None):
	"""Returns the modified time of a config file. Will return -1
	if the file does not exist, so we don't break on injected
	data.
	Parameters:
	 - default: default file name to look for
	 - config: override with this file name instead. (optional)
	   Note: the pattern of using config is intended to make using this with
	   OptionsParser easier.  Otherwise, generally ignore the use of the
	   config argument.
	"""
	if not config_path:
		config_path = ConfigPath
	retcfg = default
	if config:
		retcfg = config

	try:
		filename = find_config_path(retcfg, config_path=config_path)
	except IOError:
		return -1

	mtime = os.stat(filename).st_mtime
	return mtime

class ConfigDefault(object):
	"""
	This is a caching singleton for the behavior of fetch_config
	"""
	def __init__(self, config_path=None):
		self.config_types = {}
		self.mtimes = {}
		if not config_path:
			config_path = ConfigPath
		self.config_path = config_path

	def __call__(self):
		return self

	def config_exists(self, default, config=None):
		retcfg = default
		if config:
			retcfg = config
		try:
			find_config_path(retcfg, config_path=self.config_path)
		except IOError:
			return False
		return True

	def fetch_config(self, default, config=None):
		"""
		Returns the content of a yml config file as a hash.  If this config
		file has been read,
		this will instead return a cached value.
		Parameters:
		 - default: default file name to look for
		 - config: override with this file name instead. (optional)
		   Note: the pattern of using config is intended to make using this with
		   OptionsParser easier.  otherwise, generally ignore the use of the
		   config argument.
		Raises:
		 - IOError if no file is found
		"""
		key = str(default) + "__" + str(config)
		curr_mtime = fetch_config_mtime(
			default, config=None, config_path=self.config_path)
		if key in self.config_types:
			mtime = self.mtimes.get(key)
			if mtime is not None and mtime == curr_mtime:
				return self.config_types[key]

		value = fetch_config(default, config, config_path=self.config_path)
		self._add_config(value, default, config, curr_mtime)
		return value

	def _add_config(self, config_hash, default, config=None, mtime=-1):
		"""
		Adds a config to the cache
		"""
		key = str(default) + "__" + str(config)
		self.config_types[key] = config_hash
		self.mtimes[key] = mtime

Config = ConfigDefault()

class ConfigTest(ConfigDefault):
	"""
	This is a caching singleton for application testing.  Use this class
	to override the default behavior of Config like so:
	import config
	cache = {'memcached/sessions.yml__None':
	  {'memcache':
	    {'namespace': 'test', 'port': 11211, 'address': 'localhost'}}}
	kconfig.Config = kconfig.ConfigTest(cache)

	If ConfigTest does not have a cached value, it will attempt to
	fall back on reading the configs from disk.
	"""
	def __init__(self, config_types=None, mtimes=None, config_path=None):
		self.config_types = copy.deepcopy(config_types)
		if self.config_types is None:
			self.config_types = {}

		self.mtimes = copy.deepcopy(mtimes)
		if self.mtimes is None:
			self.mtimes = {}
		if not config_path:
			config_path = ConfigPath
		self.config_path = config_path

	def fetch_config(self, default, config=None):
		"""
		Returns values from the cache
		"""
		key = str(default) + "__" + str(config)
		if not self.config_types.has_key(key):
			return super(ConfigTest, self).fetch_config(default, config)
		return self.config_types[key]

	def add_config(self, config_hash, default, config=None):
		"""
		Adds a dict to the cache for tests
		"""
		self._add_config(config_hash, default, config)
