import unittest
import config
import sys
import os

class ConfigDefaultsTest(unittest.TestCase):
	def setUp(self):
		self.orig = config.KnewtonConfigPath

	def test_default_configs(self):
		prefixes = config.KnewtonConfigPath().prefixes
		self.assertTrue("" in prefixes)
		self.assertTrue(os.path.join('~', '.knewton') in prefixes)
		self.assertTrue('/etc/knewton/' in prefixes)
		self.assertEqual(len(prefixes), 3)

	def test_overload_config_defaults(self):
		config.KnewtonConfigPath = config.KnewtonConfigPathDefaults(["./config/tests/configs"])
		prefixes = config.KnewtonConfigPath().prefixes
		self.assertTrue("./config/tests/configs" in prefixes)
		self.assertEqual(len(prefixes), 1)

	def tearDown(self):
		config.KnewtonConfigPath = self.orig

class ConfigTests(unittest.TestCase):
	def setUp(self):
		self.orig = config.KnewtonConfigPath
		config.KnewtonConfigPath = config.KnewtonConfigPathDefaults([os.path.abspath("config/tests/configs")])

	def test_find_knewton_config_path(self):
		path = config.find_knewton_config_path('databases/reports')
		parts = path.split("/")
		self.assertEqual(parts[-1], 'reports.yml')
		self.assertEqual(parts[-2], 'databases')
		self.assertRaises(IOError, config.find_knewton_config_path, 'databases/foo')

	def test_fetch_knewton_config(self):
		payload = config.fetch_knewton_config('memcached/sessions.yml')
		self.assertTrue('memcache' in payload.keys())
		self.assertEqual(len(payload.keys()), 1)
		self.assertTrue('namespace' in payload['memcache'].keys())
		self.assertEqual('test', payload['memcache']['namespace'])
		self.assertTrue('port' in payload['memcache'].keys())
		self.assertEqual(11211, payload['memcache']['port'])
		self.assertTrue('address' in payload['memcache'].keys())
		self.assertEqual('localhost', payload['memcache']['address'])
		self.assertEqual(len(payload['memcache'].keys()), 3)
		self.assertRaises(IOError, config.fetch_knewton_config, 'databases/foo')

	def test_knewton_config(self):
		payload = config.KnewtonConfig().fetch_config('memcached/sessions.yml')
		self.assertTrue('memcache' in payload.keys())
		self.assertEqual(len(payload.keys()), 1)
		self.assertTrue('namespace' in payload['memcache'].keys())
		self.assertEqual('test', payload['memcache']['namespace'])
		self.assertTrue('port' in payload['memcache'].keys())
		self.assertEqual(11211, payload['memcache']['port'])
		self.assertTrue('address' in payload['memcache'].keys())
		self.assertEqual('localhost', payload['memcache']['address'])
		self.assertEqual(len(payload['memcache'].keys()), 3)

		cache = config.KnewtonConfig().config_types
		self.assertTrue('memcached/sessions.yml__None' in cache.keys())
		self.assertEqual(len(cache.keys()), 1)
		self.assertTrue('memcache' in cache['memcached/sessions.yml__None'].keys())
		self.assertEqual(len(cache.keys()), 1)

		payload2 = config.KnewtonConfig().fetch_config('memcached/sessions.yml')
		self.assertEqual(cache['memcached/sessions.yml__None'], payload2)

	def tearDown(self):
		config.KnewtonConfigPath = self.orig

class KnewtonConfigTestTests(unittest.TestCase):
	def setUp(self):
		self.orig = config.KnewtonConfigPath
		config.KnewtonConfigPath = config.KnewtonConfigPathDefaults([os.path.abspath("config/tests/configs")])
		self.cache = {'memcached/sessions.yml__None': {'memcache': {'namespace': 'test', 'port': 11211, 'address': 'localhost'}}}

	def test_override(self):
		config.KnewtonConfig = config.KnewtonConfigTest(self.cache)
		payload = config.KnewtonConfig().fetch_config('memcached/sessions.yml')
		self.assertTrue('memcache' in payload.keys())
		self.assertEqual(len(payload.keys()), 1)
		self.assertTrue('namespace' in payload['memcache'].keys())
		config.KnewtonConfig().add_config({}, 'databases/reports.yml')
		payload = config.KnewtonConfig().fetch_config('databases/reports.yml')
		self.assertEqual(len(payload.keys()), 0)

	def tearDown(self):
		config.KnewtonConfigPath = self.orig
		config.KnewtonConfig = config.KnewtonConfigDefault()


