import unittest
import k.config
import sys
import os

class ConfigDefaultsTest(unittest.TestCase):
	def setUp(self):
		self.orig = k.config.KnewtonConfigPath

	def test_default_configs(self):
		prefixes = k.config.KnewtonConfigPath().prefixes
		self.assertTrue("" in prefixes)
		self.assertTrue(os.path.join('~', '.knewton') in prefixes)
		self.assertTrue('/etc/knewton/' in prefixes)
		self.assertTrue('/etc/knewton/discovery/' in prefixes)
		self.assertEqual(len(prefixes), 4)

	def test_overload_config_defaults(self):
		k.config.KnewtonConfigPath = k.config.KnewtonConfigPathDefaults(["./k/config/tests/configs"])
		prefixes = k.config.KnewtonConfigPath().prefixes
		self.assertTrue("./k/config/tests/configs" in prefixes)
		self.assertEqual(len(prefixes), 1)

	def tearDown(self):
		k.config.KnewtonConfigPath = self.orig

class ConfigTests(unittest.TestCase):
	def setUp(self):
		self.orig = k.config.KnewtonConfigPath
		k.config.KnewtonConfigPath = k.config.KnewtonConfigPathDefaults([os.path.abspath("k/config/tests/configs")])

	def test_find_knewton_config_path(self):
		path = k.config.find_knewton_config_path('databases/reports')
		parts = path.split("/")
		self.assertEqual(parts[-1], 'reports.yml')
		self.assertEqual(parts[-2], 'databases')
		self.assertRaises(IOError, k.config.find_knewton_config_path, 'databases/foo')

	def test_fetch_knewton_config(self):
		payload = k.config.fetch_knewton_config('memcached/sessions.yml')
		self.assertTrue('memcache' in payload.keys())
		self.assertEqual(len(payload.keys()), 1)
		self.assertTrue('namespace' in payload['memcache'].keys())
		self.assertEqual('test', payload['memcache']['namespace'])
		self.assertTrue('port' in payload['memcache'].keys())
		self.assertEqual(11211, payload['memcache']['port'])
		self.assertTrue('address' in payload['memcache'].keys())
		self.assertEqual('localhost', payload['memcache']['address'])
		self.assertEqual(len(payload['memcache'].keys()), 3)
		self.assertRaises(IOError, k.config.fetch_knewton_config, 'databases/foo')

	def test_knewton_config(self):
		payload = k.config.KnewtonConfig().fetch_config('memcached/sessions.yml')
		self.assertTrue('memcache' in payload.keys())
		self.assertEqual(len(payload.keys()), 1)
		self.assertTrue('namespace' in payload['memcache'].keys())
		self.assertEqual('test', payload['memcache']['namespace'])
		self.assertTrue('port' in payload['memcache'].keys())
		self.assertEqual(11211, payload['memcache']['port'])
		self.assertTrue('address' in payload['memcache'].keys())
		self.assertEqual('localhost', payload['memcache']['address'])
		self.assertEqual(len(payload['memcache'].keys()), 3)

		cache = k.config.KnewtonConfig().config_types
		self.assertTrue('memcached/sessions.yml__None' in cache.keys())
		self.assertEqual(len(cache.keys()), 1)
		self.assertTrue('memcache' in cache['memcached/sessions.yml__None'].keys())
		self.assertEqual(len(cache.keys()), 1)

		payload2 = k.config.KnewtonConfig().fetch_config('memcached/sessions.yml')
		self.assertEqual(cache['memcached/sessions.yml__None'], payload2)

	def tearDown(self):
		k.config.KnewtonConfigPath = self.orig

class KnewtonConfigTestTests(unittest.TestCase):
	def setUp(self):
		self.orig = k.config.KnewtonConfigPath
		k.config.KnewtonConfigPath = k.config.KnewtonConfigPathDefaults([os.path.abspath("config/tests/configs")])
		self.cache = {'memcached/sessions.yml__None': {'memcache': {'namespace': 'test', 'port': 11211, 'address': 'localhost'}}}

	def test_override(self):
		k.config.KnewtonConfig = k.config.KnewtonConfigTest(self.cache)
		payload = k.config.KnewtonConfig().fetch_config('memcached/sessions.yml')
		self.assertTrue('memcache' in payload.keys())
		self.assertEqual(len(payload.keys()), 1)
		self.assertTrue('namespace' in payload['memcache'].keys())
		k.config.KnewtonConfig().add_config({}, 'databases/reports.yml')
		payload = k.config.KnewtonConfig().fetch_config('databases/reports.yml')
		self.assertEqual(len(payload.keys()), 0)

	def tearDown(self):
		k.config.KnewtonConfigPath = self.orig
		k.config.KnewtonConfig = k.config.KnewtonConfigDefault()

