"""Saves parameters to, and loads parameters from, INI configuration files.
"""

import os
import logging
import configparser
import typing as t

from grubhub_dl import models

logger = logging.getLogger(__name__)


class ConfigManager():
	"""Provides a
	"""

	def __init__(self, config_path: str = None):
		"""Load the settings from the user's configuration file, if it exists, and get the
		path to the module that's initializing a ConfigManager"""

		if config_path is not None:
			self.config_path = config_path
		else:
			self.config_path = os.path.expandvars(DEFAULT_CONFIG_PATH)
		
		self._load_settings()

	def _load_settings(self):
		"""Load the user's configuration from file"""
		self.config = configparser.ConfigParser()
		self.config.read(self.config_path)
	
	def _save_settings(self):
		"""Write the user's configuration to file"""
		with open(self.config_path, 'w') as config_file:
			self.config.write(config_file)

	def params_to_config(self, models.Parameters):
		pass


	def config_to_params(self) -> models.Parameters:
		pass

	def get_setting(
		self,
		setting_name: str,
		*,
		title: str = None,
		ask_type: str = 'file',
		always_ask: bool = False,
		dont_save: bool = False,
		required: bool = True
	) -> t.Union[str, None]:
		"""Get the value of a setting from the configuration file, or ask the user to
		provide the value

		The configuration file is divided into sections -- one section for each plugin
		that chooses to leverage ConfigManager. So ``setting_name`` will always be scoped
		to that plugin. For example, the plugins "test_alice" and "test_bob" can both have
		a setting named "input_file" with different values:

		.. code-block:: ini

			[pipelines.reports.test_alice]
			input_file = C:/Users/nickolas.omalley/Downloads/excel_report_alice.xlsx

			[pipelines.reports.test_bob]
			input_file = C:/Users/nickolas.omalley/Downloads/excel_report_bob.xlsx
		
		:param setting_name: The name of the setting in the configuration file that you
			want to get the value of. If the setting doesn't exist, the user will be asked
			to provide a value. The given value will be saved to this setting in the
			user's configuration file, unless dont_save is True.
		:param title: The string to use as the input() or titlebar message when asking the
			user to provide a value for setting_name.
		:param ask_type: How to ask the user for a value. Options are 'file' (tkinter
			askfiledialog), 'dir' (tkinter askdirectory), or 'input' (built-in input()
			function. (default: 'file')
		:param always_ask: Always ask the user to provide the value, even if it already
			exists in the config file.
		:param dont_save: If True, don't save the user-provided value back to the config
			file. (default: False)
		:param required: A value must be provided. If setting_name isn't found in the
			config file, and the user fails to provide a non-blank value, raise an error.
			(default: True)
		"""
		
		setting_value = None
		valid_ask_types = ['input', 'file', 'dir']

		if ask_type not in valid_ask_types:
			raise ValueError(
				('ConfigManager.get_setting only supports these values for the ask_type '
	 			f'parameter: {", ".join(valid_ask_types)}, but {ask_type} was provided')
			)

		if not title:
			title = f'Please select the "{setting_name}" file or folder'
		
		if self.mod_name_full not in self.config:
			self.config[self.mod_name_full] = {}

		if always_ask or setting_name not in self.config[self.mod_name_full]:
			if ask_type == 'input':
				setting_value = self.ask_input(title, required)
			else:
				setting_value = self.ask_input_tk(title, required, ask_type=ask_type)

		if not always_ask and setting_name in self.config[self.mod_name_full]:
			setting_value = self.config[self.mod_name_full][setting_name]

		if not dont_save:
			if setting_value:
				self.config[self.mod_name_full][setting_name] = setting_value
			self._save_settings()
		
		return setting_value