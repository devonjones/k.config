import unittest
import k.config
import os

class ConfigDefaultsTest(unittest.TestCase):
	def setUp(self):
		self.orig = k.config.ConfigPath

	def test_default_configs(self):
		prefixes = k.config.ConfigPath().prefixes
		self.assertTrue("" in prefixes)
		self.assertTrue(os.path.join('~', '.knewton') in prefixes)
		self.assertTrue('/etc/knewton/' in prefixes)
		self.assertEqual(len(prefixes), 3)

	def test_overload_config_defaults(self):
		k.config.ConfigPath = k.config.ConfigPathDefaults(
			["./k/config/tests/configs"])
		prefixes = k.config.ConfigPath().prefixes
		self.assertTrue("./k/config/tests/configs" in prefixes)
		self.assertEqual(len(prefixes), 1)

	def tearDown(self):
		k.config.ConfigPath = self.orig

class ConfigTests(unittest.TestCase):
	def setUp(self):
		self.orig = k.config.ConfigPath
		self.config_path = k.config.ConfigPath = k.config.ConfigPathDefaults(
			[os.path.abspath("k/config/tests/configs")])
		k.config.Config.config_types = {}
		k.config.Config.config_path = self.config_path

	def test_find_config_path(self):
		path = k.config.find_config_path('databases/reports')
		parts = path.split("/")
		self.assertEqual(parts[-1], 'reports.yml')
		self.assertEqual(parts[-2], 'databases')
		self.assertRaises(
			IOError, k.config.find_config_path, 'databases/foo')

	def test_fetch_config(self):
		payload = k.config.fetch_config(
			'memcached/sessions.yml', config_path=self.config_path)
		self.assertTrue('memcache' in payload.keys())
		self.assertEqual(len(payload.keys()), 1)
		self.assertTrue('namespace' in payload['memcache'].keys())
		self.assertEqual('test', payload['memcache']['namespace'])
		self.assertTrue('port' in payload['memcache'].keys())
		self.assertEqual(11211, payload['memcache']['port'])
		self.assertTrue('address' in payload['memcache'].keys())
		self.assertEqual('localhost', payload['memcache']['address'])
		self.assertEqual(len(payload['memcache'].keys()), 3)
		self.assertRaises(IOError, k.config.fetch_config, 'databases/foo')

	def test_override_fetch_config(self):
		payload = k.config.fetch_config(
			'databases/reports',
			'memcached/sessions.yml',
			config_path=self.config_path)
		self.assertTrue('memcache' in payload.keys())
		self.assertEqual(len(payload.keys()), 1)
		self.assertTrue('namespace' in payload['memcache'].keys())
		self.assertEqual('test', payload['memcache']['namespace'])
		self.assertTrue('port' in payload['memcache'].keys())
		self.assertEqual(11211, payload['memcache']['port'])
		self.assertTrue('address' in payload['memcache'].keys())
		self.assertEqual('localhost', payload['memcache']['address'])
		self.assertEqual(len(payload['memcache'].keys()), 3)
		self.assertRaises(IOError, k.config.fetch_config, 'databases/foo')

	def test_config(self):
		payload = k.config.Config().fetch_config('memcached/sessions.yml')
		self.assertTrue('memcache' in payload.keys())
		self.assertEqual(len(payload.keys()), 1)
		self.assertTrue('namespace' in payload['memcache'].keys())
		self.assertEqual('test', payload['memcache']['namespace'])
		self.assertTrue('port' in payload['memcache'].keys())
		self.assertEqual(11211, payload['memcache']['port'])
		self.assertTrue('address' in payload['memcache'].keys())
		self.assertEqual('localhost', payload['memcache']['address'])
		self.assertEqual(len(payload['memcache'].keys()), 3)

		cache = k.config.Config().config_types
		self.assertTrue('memcached/sessions.yml__None' in cache.keys())
		print cache.keys()
		self.assertEqual(len(cache.keys()), 1)
		self.assertTrue(
			'memcache' in cache['memcached/sessions.yml__None'].keys())
		self.assertEqual(len(cache.keys()), 1)

		payload2 = k.config.Config().fetch_config(
			'memcached/sessions.yml')
		self.assertEqual(cache['memcached/sessions.yml__None'], payload2)

	def test_discovery(self):
		payload = k.config.Config().fetch_discovery('mysql', 'reports')
		self.assertTrue('server_list' in payload.keys())
		server_list = payload['server_list']
		self.assertEqual(len(server_list), 1)
		config = server_list[0]
		self.assertTrue('header' in config.keys())
		header = config['header']
		self.assertEqual(header['service_class'], 'mysql')
		self.assertEqual(header['metadata']['protocol'], 'mysql')
		self.assertEqual(header['metadata']['version'], 1.0)
		self.assertEqual(config['encoding'], 'utf8')
		self.assertEqual(config['database'], 'reports')
		self.assertEqual(config['username'], 'reports')
		self.assertEqual(config['password'], 'reports')
		self.assertEqual(config['host'], 'localhost')
		
	def test_discovery_no_server_list(self):
		payload = k.config.Config().fetch_config(
			'discovery/mysql/knewmena.yml')
		self.assertTrue(not payload.has_key('server_list'))
		payload = k.config.Config().fetch_discovery('mysql', 'knewmena')
		self.assertTrue('server_list' in payload.keys())
		server_list = payload['server_list']
		self.assertEqual(len(server_list), 1)
		config = server_list[0]
		self.assertTrue('header' in config.keys())
		header = config['header']
		self.assertEqual(header['service_class'], 'mysql')
		self.assertEqual(header['metadata']['protocol'], 'mysql')
		self.assertEqual(header['metadata']['version'], 1.0)
		self.assertEqual(config['encoding'], 'utf8')
		self.assertEqual(config['database'], 'knewmena')
		self.assertEqual(config['username'], 'knewmena')
		self.assertEqual(config['password'], 'knewmena')
		self.assertEqual(config['host'], 'localhost')

	def test_config_injection(self):
		self.assertRaises(
			IOError,
			k.config.Config().fetch_config,
			'fake_config/not_here')
		config = {
			'host': 'localhost',
			'port': 12345,
		}
		k.config.Config()._add_config(config, 'fake_config/not_here')
		payload = k.config.Config().fetch_config('fake_config/not_here')
		self.assertEqual('localhost', payload['host'])
		self.assertEqual(12345, payload['port'])
		
	def tearDown(self):
		k.config.ConfigPath = self.orig

class ConfigTestTests(unittest.TestCase):
	def setUp(self):
		self.orig = k.config.ConfigPath
		k.config.ConfigPath = k.config.ConfigPathDefaults(
			[os.path.abspath("config/tests/configs")])
		self.cache = {
				'memcached/sessions.yml__None': {
					'memcache': {
						'namespace': 'test',
						'port': 11211,
						'address': 'localhost'
					}
				}
			}

	def test_override(self):
		k.config.Config = k.config.ConfigTest(self.cache)
		payload = k.config.Config().fetch_config('memcached/sessions.yml')
		self.assertTrue('memcache' in payload.keys())
		self.assertEqual(len(payload.keys()), 1)
		self.assertTrue('namespace' in payload['memcache'].keys())
		k.config.Config().add_config({}, 'databases/reports.yml')
		payload = k.config.Config().fetch_config('databases/reports.yml')
		self.assertEqual(len(payload.keys()), 0)

	def tearDown(self):
		k.config.ConfigPath = self.orig
		k.config.Config = k.config.ConfigDefault()

