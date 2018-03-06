import re

from string import Template
from configparser import ConfigParser
from baker.secret import Encryption, SecretKey


def replace():
    # read configs
    config = ConfigParser()
    config.optionxform = str
    config.read('values.cfg')

    # instance encryption
    secret_key = SecretKey('my secret key ninja_+=')
    encryption = Encryption(secret_key.generate())

    # find and decrypt secret values
    def decrypt_secrets(items):
        def call(value):
            secret_val = re.search('_secret\((.+?)\)', value)
            if secret_val:
                return encryption.decrypt(secret_val.group(1))
            return value
        return dict(map(lambda i: (i[0], call(i[1])), items))

    # replace files
    for file_location in config.sections():
        values = dict(config.items(file_location))
        values = decrypt_secrets(values.items())
        template = open(file_location).read()
        replacement = Template(template).substitute(values)
        open(file_location[:-4], 'w').write(replacement)
