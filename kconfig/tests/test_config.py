import unittest
import kconfig
import os

class ConfigDefaultsTest(unittest.TestCase):
	def setUp(self):
		self.orig = kconfig.ConfigPath

	def test_default_configs(self):
		prefixes = kconfig.ConfigPath().prefixes
		self.assertTrue("" in prefixes)
		self.assertTrue(os.path.join('~', '.knewton') in prefixes)
		self.assertTrue('/etc/knewton/' in prefixes)
		self.assertEqual(len(prefixes), 3)

	def test_overload_config_defaults(self):
		kconfig.ConfigPath = kconfig.ConfigPathDefaults(
			["./kconfig/tests/configs"])
		prefixes = kconfig.ConfigPath().prefixes
		self.assertTrue("./kconfig/tests/configs" in prefixes)
		self.assertEqual(len(prefixes), 1)

	def tearDown(self):
		kconfig.ConfigPath = self.orig

class ConfigTests(unittest.TestCase):
	def setUp(self):
		self.orig = kconfig.ConfigPath
		self.config_path = kconfig.ConfigPath = kconfig.ConfigPathDefaults(
			[os.path.abspath("kconfig/tests/configs")])
		kconfig.Config.config_types = {}
		kconfig.Config.config_path = self.config_path

	def test_find_config_path(self):
		path = kconfig.find_config_path('databases/reports')
		parts = path.split("/")
		self.assertEqual(parts[-1], 'reports.yml')
		self.assertEqual(parts[-2], 'databases')
		self.assertRaises(
			IOError, kconfig.find_config_path, 'databases/foo')

	def test_fetch_config(self):
		payload = kconfig.fetch_config(
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
		self.assertRaises(IOError, kconfig.fetch_config, 'databases/foo')

	def test_override_fetch_config(self):
		payload = kconfig.fetch_config(
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
		self.assertRaises(IOError, kconfig.fetch_config, 'databases/foo')

	def test_config(self):
		payload = kconfig.Config().fetch_config('memcached/sessions.yml')
		self.assertTrue('memcache' in payload.keys())
		self.assertEqual(len(payload.keys()), 1)
		self.assertTrue('namespace' in payload['memcache'].keys())
		self.assertEqual('test', payload['memcache']['namespace'])
		self.assertTrue('port' in payload['memcache'].keys())
		self.assertEqual(11211, payload['memcache']['port'])
		self.assertTrue('address' in payload['memcache'].keys())
		self.assertEqual('localhost', payload['memcache']['address'])
		self.assertEqual(len(payload['memcache'].keys()), 3)

		cache = kconfig.Config().config_types
		self.assertTrue('memcached/sessions.yml__None' in cache.keys())
		print cache.keys()
		self.assertEqual(len(cache.keys()), 1)
		self.assertTrue(
			'memcache' in cache['memcached/sessions.yml__None'].keys())
		self.assertEqual(len(cache.keys()), 1)

		payload2 = kconfig.Config().fetch_config(
			'memcached/sessions.yml')
		self.assertEqual(cache['memcached/sessions.yml__None'], payload2)

	def test_config_injection(self):
		self.assertRaises(
			IOError,
			kconfig.Config().fetch_config,
			'fake_config/not_here')
		config = {
			'host': 'localhost',
			'port': 12345,
		}
		kconfig.Config()._add_config(config, 'fake_config/not_here')
		payload = kconfig.Config().fetch_config('fake_config/not_here')
		self.assertEqual('localhost', payload['host'])
		self.assertEqual(12345, payload['port'])

	def tearDown(self):
		kconfig.ConfigPath = self.orig

class ConfigTestTests(unittest.TestCase):
	def setUp(self):
		self.orig = kconfig.ConfigPath
		kconfig.ConfigPath = kconfig.ConfigPathDefaults(
			[os.path.abspath("./kconfig/tests/configs")])
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
		kconfig.Config = kconfig.ConfigTest(self.cache)
		payload = kconfig.Config().fetch_config('memcached/sessions.yml')
		self.assertTrue('memcache' in payload.keys())
		self.assertEqual(len(payload.keys()), 1)
		self.assertTrue('namespace' in payload['memcache'].keys())
		kconfig.Config().add_config({}, 'databases/reports.yml')
		payload = kconfig.Config().fetch_config('databases/reports.yml')
		self.assertEqual(len(payload.keys()), 0)

	def tearDown(self):
		kconfig.ConfigPath = self.orig
		kconfig.Config = kconfig.ConfigDefault()

