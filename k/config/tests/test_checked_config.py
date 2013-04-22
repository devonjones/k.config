import os.path
import unittest

from k.config.checked_config import CheckedConfig
from k.config.checked_config import NestedField
from k.config.checked_config import ListField
from k.config.checked_config import StringField
from k.config.checked_config import IntField
from k.config.checked_config import BoolField

CONFIGS_DIR = os.path.join(os.path.dirname(__file__), "configs")

class TestConfig(CheckedConfig):
	CONFIG_FIELDS = [
		StringField("name", pattern="^\w+$"),
		IntField("age", lower_bound=0, upper_bound=150),
		NestedField("attributes",
			BoolField("cool_guy", default=True),
			BoolField("smart_guy", default=False),
			BoolField("rad_guy", default=True)
		),
		ListField("email_addresses",
			StringField("email_address")
		)
	]

class DatabaseConfig(CheckedConfig):
	CONFIG_FIELDS = [
		NestedField("database",
			StringField("adapter", "mysql"),
			StringField("encoding", "utf8"),
			StringField("database"),
			StringField("username"),
			StringField("password"),
			StringField("host")
		)
	]

class TestCheckedConfig(unittest.TestCase):

	def setUp(self):
		self.config_dict = {
			"name": "Brad",
			"age": "31",
			"attributes": {
				"cool_guy": "true",
				"smart_guy": "false",
			},
			"email_addresses": [
				"bradley@knewton.com",
				"prodsupport@knewton.com"
			]
		}

	def test_validate_config(self):
		config = TestConfig(self.config_dict)

		self.assertEqual("Brad", config.name)
		self.assertEqual(31, config.age)
		self.assertEqual(True, config.attributes.cool_guy)
		self.assertEqual(False, config.attributes.smart_guy)
		self.assertEqual(True, config.attributes.rad_guy)
		self.assertEqual(2, len(config.email_addresses))
		self.assertEqual("bradley@knewton.com", config.email_addresses[0])
		self.assertEqual("prodsupport@knewton.com", config.email_addresses[1])

	def test_missing_field(self):
		del self.config_dict["name"]
		with self.assertRaises(ValueError) as ve:
			TestConfig(self.config_dict)
		self.assertEqual("Missing config field: 'name'", ve.exception.message)

	def test_int_lower_bounds(self):
		self.config_dict["age"] = -10
		with self.assertRaises(ValueError) as ve:
			TestConfig(self.config_dict)
		self.assertEqual("Value for field 'age': -10 is less than lower bound 0",
				ve.exception.message)

	def test_int_upper_bounds(self):
		self.config_dict["age"] = 200
		with self.assertRaises(ValueError) as ve:
			TestConfig(self.config_dict)
		self.assertEqual("Value for field 'age': 200 is greater than upper bound 150",
				ve.exception.message)

	def test_int_invalid(self):
		self.config_dict["age"] = "cheese"
		with self.assertRaises(ValueError) as ve:
			TestConfig(self.config_dict)
		self.assertEqual("Value for field 'age': invalid literal for int() with base 10: 'cheese'",
				ve.exception.message)

	def test_string_pattern(self):
		self.config_dict["name"] = "Ke$ha"
		with self.assertRaises(ValueError) as ve:
			TestConfig(self.config_dict)
		self.assertEqual("Value for field 'name': 'Ke$ha' does not match pattern.",
				ve.exception.message)

	def test_bad_name(self):
		with self.assertRaises(ValueError) as ve:
			StringField("_bad_name")
		self.assertEqual("'_bad_name' is an invalid name for a config field. "
				"Config field names must be valid python identifiers and cannot "
				"start with '_'.", ve.exception.message)

	def test_keyword_name(self):
		with self.assertRaises(ValueError) as ve:
			StringField("with")
		self.assertEqual("'with' is an invalid name for a config field. "
				"It matches a python keyword.", ve.exception.message)

	def test_load_from_file(self):
		config = DatabaseConfig(os.path.join(CONFIGS_DIR, "databases/reports.yml"))

		self.assertEqual("mysql", config.database.adapter)
		self.assertEqual("utf8", config.database.encoding)
		self.assertEqual("reports", config.database.database)
		self.assertEqual("reports", config.database.username)
		self.assertEqual("reports", config.database.password)
		self.assertEqual("localhost", config.database.host)

if __name__ == "__main__":
	unittest.main()
