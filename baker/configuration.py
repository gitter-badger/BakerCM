from configparser import ConfigParser
from collections import OrderedDict

from baker.settings import CONFIG_CASE_SENSITIVE, ENCODING
from baker.secret import Encryption, SecretKey


class ReadConfig:
    def __init__(self, file):
        self.configs = []
        self.config_file = file
        filename = file.lower()

        if filename.endswith('.cfg'):
            self.dict_from_ini()
        # elif filename.endswith('.yml'): # TODO: Add support to configure via yaml file
        #     self.dict_from_yaml()
        else:
            raise FileExistsError('Unsupported file format.')

    def dict_from_ini(self):
        parser = ConfigParser()

        if CONFIG_CASE_SENSITIVE:
            parser.optionxform = str

        parser.read(self.config_file, encoding=ENCODING)

        if parser.sections():
            sections = map(lambda x: x.rsplit(':', 1)[0], parser.sections())
            templates = OrderedDict.fromkeys(sections)

            for name in templates:
                variables = self._get_values(parser, name + ':variables')
                secrets = self._get_values(parser, name + ':secrets')
                template = self._get_values(parser, name + ':template')

                if template:
                    template['name'] = name
                else:
                    raise AttributeError('Attribute template is required.')

                self.configs.append(Config(template, variables, secrets))
        else:
            raise FileExistsError('Unable to read configs from file.')

    @staticmethod
    def _get_values(parser, section):
        values = None
        if parser.has_section(section):
            values = dict(parser.items(section))
        return values


class Config:
    def __init__(self, template, variables=None, secrets=None):
        self._template(template)
        self.variables = variables
        self._secrets(secrets)

    def _secrets(self, secrets):
        if secrets:
            if not self.variables:
                self.variables = {}
            secret_key = SecretKey()
            encryption = Encryption(secret_key.key)
            for var, secret in secrets.items():
                decrypted_value = encryption.decrypt(secret)
                self.variables[var] = decrypted_value

    def _template(self, template):
        for var, value in template.items():
            if var not in ['template', 'path', 'name', 'user', 'group', 'mode']:
                raise AttributeError("Unsupported attribute '%s'in config file." % var)
            self.__setattr__(var, value)
