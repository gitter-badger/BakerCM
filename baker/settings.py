from configparser import ConfigParser
from itertools import chain
from pathlib import Path


_HOME_PATH = str(Path.home())
_BAKER_PATH = _HOME_PATH + '/.baker'
_BAKERC_PATH = _HOME_PATH + '/.bakerc'

_default_values = {
    # DEBUG mode is False as default, it can be change in config file.
    # Using option --verbose in command line DEBUG change to true.
    'DEBUG': False,

    # Encode of files and secrets
    'ENCODING': 'utf-8',

    # This method transforms option names on every read, get, or set operation.
    # The default config keys are case insensitive. E.g. True -> for case sensitive.
    'RECIPE_CASE_SENSITIVE': False,

    # Repository url including protocol http/https and domain until the root folder.
    'REPOSITORY': None,

    # Type of repository to use some pattern that is know like: 'github' or 'bitbucket'.
    # Pattern can be customized setting it as 'custom' and filling REPOSITORY_CUSTOM_PATTERN config.
    'REPOSITORY_TYPE': None,

    # Customization of repository access the instructions with configurations.
    # To build pattern use variables to build url to access config in a remote repository.
    # E.g.: '%(repository)s/%(path)s.%(ext)s/%(version)s'
    'REPOSITORY_CUSTOM_PATTERN': None,

    # Absolute path to store instructions when downloaded via baker
    'STORAGE_RECIPE': _BAKER_PATH + '/instructions/',

    # Absolute path to store index of instructions when downloaded via baker
    'STORAGE_RECIPE_INDEX': _BAKER_PATH + '/index',

    # Absolute path to store baker key to use secret values
    'STORAGE_KEY_PATH': _BAKER_PATH + '/baker.key',

    # Absolute path to store templates when downloaded via baker
    'STORAGE_TEMPLATES': _BAKER_PATH + '/templates/',

    # Extension for template files. Set 'None' to disable replacement of template name.
    'TEMPLATE_EXT': 'tpl',
}


def get(key):
    return values()[key]


def load(**kwargs):
    global BAKER_SETTINGS
    BAKER_SETTINGS = _default_values

    _load_bakerc()

    for key, value in kwargs.items():
        values()[key] = value


def values():
    return globals()['BAKER_SETTINGS']


def _load_bakerc():
    def convert_if_bool(string):
        lower_str = string.lower()
        if lower_str in ('true', 'false'):
            return lower_str == 'true'
        return string

    if Path(_BAKERC_PATH).is_file():
        parser = ConfigParser()

        with open(_BAKERC_PATH) as lines:
            lines = chain(("[DEFAULT]",), lines)
            parser.read_file(lines)

        for key, value in parser.defaults().items():
            upper_key = key.upper()
            if upper_key not in values():
                raise AttributeError(
                    "Setting '{0}' at '{1}' is not supported".format(upper_key, _BAKERC_PATH)
                )
            values()[upper_key] = convert_if_bool(value)
