import collections
import keyword
import re
import types

from k.config import Config

def _validate(config_dict, config_fields):
	"""Validate a parsed config dictionary

	Validates the contents of config_dict against the fields
	defined in this CheckedConfig. Makes sure that all required
	fields are present and have appropriate values.

	Args:
	  config_dict: a dictionary containing config fields and
		values to validate.

	Returns:
	  A dictionary of validated fields and values.
	"""
	valid_dict = {}
	for field in config_fields:
		try:
			value = config_dict[field.name]
		except KeyError:
			if field.default is not None:
				value = field.default
			else:
				raise ValueError("Missing config field: '{0}'".format(field.name))

		valid_dict[field.name] = field.validate(value)
	return valid_dict

class CheckedConfig(object):
	"""Defines a schema for a config file

	Allows you to define the field names, types, and some basic
	validation for a config file. Subclasses should override
	the CONFIG_FIELDS field to describe the fields available
	on this config. CONFIG_FIELDS should be a list of Field
	subclasses. Example:

	class FooConfig(CheckedConfig):
		CONFIG_FIELDS = [
			StringField("name", pattern="\w+"),
			IntField("age", lower_bound=0, upper_bound=150),
			NestedField("attributes",
				BoolField("cool_guy", default=False),
				BoolField("smart_guy", default=False)
			)
		]

	config.yml contents:

	name: Brad
	age: 31
	attributes:
		cool_guy: true
		smart_guy: false

	After being checked, the resulting config fields can be
	accessed via simple attribute access:

	> config = FooConfig("config.yml")
	> print config.name
	Brad
	> print config.attributes.cool_guy
	True

	Invalid values will cause ValueErrors to be raised:
	> config = FooConfig({"name": "Brad", "age": -10})
	Traceback (most recent call last):
	  File "<stdin>", line 1, in <module>
	  ValueError: Value for field 'age': -10 is less than lower bound 0
	"""
	# override in subclasses to define the fields in this config
	CONFIG_FIELDS = []

	def __init__(self, config):
		"""Initialize this CheckedConfig

		Args:
		  config: a dict or a str. If a dict, it contains the
		    unvalidated fields and values of this config. If a
		    str, it contains the location of a config file that
		    will be loaded using Config.
		"""
		if isinstance(config, types.StringTypes):
			config = Config.fetch_config(config)

		valid_config = _validate(config, self.CONFIG_FIELDS)
		self.__dict__.update(valid_config)

class Field(object):
	"""An abstract field definition

	Subclasses are used to define fields in a CheckedConfig.
	"""

	# Acceptable values must start with a letter, and be followed by zero or
	# more alpha-numeric or _ characters. Any valid python identifier that
	# does not start with _ should match.
	FIELD_PATTERN = re.compile("^[a-zA-Z]\w*$")

	def __init__(self, name, default=None):
		"""Initialize this Field

		Args:
		  name: A str. The name of this field. Must be a valid python
		    identifier that does not begin with '_'.
		  default: The default value that this field will be set to
		    if it is not present in the config file. If this is set
		    to None (the default), then there is no default value and
		    an error will be raised if the field is missing.
		"""
		self.validate_name(name)
		self.name = name
		self.default = default

	def validate_name(self, name):
		"""Validate a field name

		Makes sure that the name is a valid python identifier that does
		not start with '_' and that it is not a python keyword.

		Args:
		  name: A str.

		Raises:
		  ValueError: If this is an invalid name.
		"""
		if not re.match(self.FIELD_PATTERN, name):
			raise ValueError("'{0}' is an invalid name for a config field. "
					"Config field names must be valid python "
					"identifiers and cannot start with '_'.".format(name))

		if keyword.iskeyword(name):
			raise ValueError("'{0}' is an invalid name for a config field. "
					"It matches a python keyword.".format(name))

	def validate(self, value):
		"""Validate the supplied value against this field definition

		Abstract method. Should be implemented by subclasses.
		"""
		raise NotImplementedError("validate not implemented")

class IntField(Field):
	"""A field that expects an integer value"""

	def __init__(self, name, default=None,
			lower_bound=None, upper_bound=None):
		"""Initialize this IntField

		Args:
		  name: A str. The name of this field.
		  lower_bound: An int or None. The lowest acceptable value
		    for this field. If None, there is no lower bound.
		  upper_bound: An int or None. The highest acceptable value
		    for this field. If None, there is no upper bound.
		"""
		super(IntField, self).__init__(name, default)
		self.lower_bound = lower_bound
		self.upper_bound = upper_bound

	def validate(self, value):
		"""Ensure that the supplied value is a valid integer

		It will attempt to convert the supplied value to an integer
		and ensure that it is between the upper and lower bounds of
		this field if they exist.

		Args:
		  value: An int or value convertable to an int.

		Returns:
		  An int. This is the converted and validated value.

		Raises:
		  ValueError if value is not valid for this field
		"""
		try:
			int_value = int(value)
		except ValueError as ve:
			raise ValueError("Value for field '{0}': {1}".format(self.name, ve.message))

		if self.lower_bound is not None and int_value < self.lower_bound:
			raise ValueError("Value for field '{0}': {1} is less than lower bound {2}".format(
					self.name, int_value, self.lower_bound))
		if self.upper_bound is not None and int_value > self.upper_bound:
			raise ValueError("Value for field '{0}': {1} is greater than upper bound {2}".format(
					self.name, int_value, self.upper_bound))
		return int_value

class StringField(Field):
	"""A field that expects a string value"""

	def __init__(self, name, default=None,
			pattern=None):
		"""Initialize this StringField

		Args:
		  name: A str. The name of this field.
		  pattern: A str or None. A regexp that defines the acceptable
		    pattern for this field. If None, all strings will be
		    accepted.
		"""
		super(StringField, self).__init__(name, default)
		if pattern:
			self.pattern = re.compile(pattern)
		else:
			self.pattern = None

	def validate(self, value):
		"""Ensure that the supplied value is a valid string

		It will attempt to convert the supplied value to a string
		and ensure that it matches the pattern for this field if
		one exists.

		Args:
		  value: A str or value convertable to a str.

		Returns:
		  A str. This is the converted and validated value.

		Raises:
		  ValueError if value is not valid for this field
		"""
		str_value = str(value)
		if self.pattern and not re.match(self.pattern, str_value):
			raise ValueError("Value for field '{0}': '{1}' does not match pattern.".format(self.name, str_value))
		return str_value

class BoolField(Field):
	"""A field that expects a boolean value"""

	TRUE_VALUES = ["true", "True", "1", "yes", True, 1]

	def validate(self, value):
		"""Ensure that supplied value is a valid boolean

		The supplied value will be checked against a list of
		true values. If the value is not in the list, it is
		considered False.

		Args:
		  value: A bool or value convertable to a bool.

		Returns:
		  A bool. This is the converted and validated value.
		"""
		return value in self.TRUE_VALUES

class ListField(Field):
	"""A field that expects a list of values"""

	def __init__(self, name, field_type):
		"""Initialize this ListField

		Args:
		  name: A str. The name of this field.
		  field_type: A Field. All values in this sequence
		    will be validated against it. The name of this
		    field is meaningless and will be ignored.
		"""
		super(ListField, self).__init__(name)
		self.field_type = field_type

	def validate(self, value):
		"""Ensure that supplied value is a valid list field

		Verifies that the supplied value is a list which contains
		fields that validate against self.field_type.

		Args:
		  value: A list. The list should contain values that
		    validate against self.field_type.

		Returns:
		  A list of validated values.

		Raises:
		  ValueError if any of the list field values are not valid.
		"""
		return [self.field_type.validate(v) for v in value]

class NestedField(Field):
	"""A field that contains a dictionary of other fields"""

	def __init__(self, name, *config_fields):
		"""Initialize this NestedField

		Note: NestedFields cannot have default values. However,
		fields nested under them can.

		Args:
		  name: A str. The name of this field.
		  config_fields: A list of Fields. Defines the fields nested
		    under this field.
		"""
		super(NestedField, self).__init__(name)
		self.config_fields = config_fields
		self.tuple_type = collections.namedtuple("NestedField_{0}".format(name),
				[c.name for c in config_fields])

	def validate(self, value):
		"""Ensure that supplied value is a valid nested field

		Verifies that the supplied value contains all the fields defined
		by config_fields and that they have appropriate values (or
		appropriate defaults if the fields are missing).

		Args:
		  value: A dict. Describes the names and values of the fields
		    nested under this field.

		Returns:
		  A namedtuple type. This allows attribute access to nested
		    fields.

		Raises:
		  ValueError if any of the nested field values are not valid.
		"""
		valid_dict = _validate(value, self.config_fields)
		return self.tuple_type(**valid_dict)

