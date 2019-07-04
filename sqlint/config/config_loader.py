import os
from configparser import ConfigParser, NoSectionError, NoOptionError

# section name in ini file
SECTION = 'sqlint'

# type of each config values
NAME_TYPES = {
  'comma-position': str,  # Comma position in breaking a line
  'keyword-style': str,  # Reserved keyword style
  'indent-steps': int  # indent steps in breaking a line
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_INI = os.path.join(BASE_DIR, 'default.ini')


class ConfigLoader(object):
    def __init__(self, config_file=None):
        # default config
        self.default_config = ConfigParser()
        self.default_config.read(DEFAULT_INI)

        # user config
        self.user_config_file = config_file
        self.user_config = ConfigParser()
        if self.user_config_file and self.user_config_file != DEFAULT_INI:
            self.user_config.read(self.user_config_file)

        # load configs
        self.values = {}
        self._load()

    def _get_with_type(self, config_parser, name, _type):
        """

        Args:
            config_parser:
            name:
            _type:

        Returns:

        """
        if _type == int:
            return config_parser.getint(SECTION, name)
        elif _type == float:
            return config_parser.getfloat(SECTION, name)
        elif _type == bool:
            return config_parser.getboolean(SECTION, name)

        # type is str or others
        return self.default_config.get(SECTION, name)

    def _load(self):
        """

        Returns:

        """
        # load default settings
        for name, _type in NAME_TYPES.items():
            try:
                self.values[name] = self._get_with_type(self.default_config, name, _type)
            except NoSectionError as e:
                raise e
            except NoOptionError as e:
                # raise Error
                raise e
            except ValueError as e:
                # raise Error
                raise e

        if self.user_config_file is None:
            return

        # load user settings
        for name, _type in NAME_TYPES.items():
            try:
                self.values[name] = self._get_with_type(self.user_config, name, _type)
            except NoSectionError:
                continue
            except NoOptionError:
                continue
            except ValueError as e:
                # raise Error
                print(e)

    def get(self, name, default=None):
        """

        Args:
            name:
            default:

        Returns:

        """
        if name in self.values:
            return self.values[name]

        return default
