import os
import shutil

from string import Template

from baker import settings
from baker import logger


class ReplaceTemplate:
    def __init__(self, configs):
        self.configs = configs

    def replace(self):
        for config in self.configs:
            template_file = self._file(config.template)
            template = BakerTemplate(template_file)
            replaced = template.replace(config.variables) if config.variables else template_file
            target = config.template

            if hasattr(config, 'path'):
                target = config.path

            if settings.get('TEMPLATE_EXT') and target.endswith(settings.get('TEMPLATE_EXT')):
                ext_size = len(settings.get('TEMPLATE_EXT')) + 1
                target = target[:-ext_size]

            self._file(target, mode='w', content=replaced)
            self._add_file_permission(config, target)
            logger.log(config.name, config.template, target)

    @staticmethod
    def _file(path, mode='r', content=None):
        file = open(path, mode)
        try:
            if mode == 'r':
                return file.read()
            elif content:
                return file.write(content)
        finally:
            file.close()

    @staticmethod
    def _add_file_permission(config, path):
        if hasattr(config, 'user') or hasattr(config, 'group'):
            user = config.user if hasattr(config, 'user') else None
            group = config.group if hasattr(config, 'group') else None
            shutil.chown(path, user, group)
        if hasattr(config, 'mode'):
            os.chmod(path, int(config.mode, 8))


class BakerTemplate(Template):
    delimiter = '{{'
    pattern = r'''
        \{\{\ *(?:
        (?P<escaped>\\)                     | # escape with {{\escape}} or {{\ escape }}} 
        (?P<named>[_a-z][_a-z0-9]*)\ *}}    | # identifier {{var}} or {{ var }}
        \b\B(?P<braced>)                    | # braced identifier disabled
        (?P<invalid>)                         # ill-formed delimiter expr
        )
    '''

    def replace(self, mapping):
        try:
            if settings.get('CONFIG_CASE_SENSITIVE'):
                return super(BakerTemplate, self).substitute(mapping)
            else:
                return self.ignore_case_substitute(mapping)
        except KeyError as e:
            raise KeyError('Missing variable %s' % e)

    def ignore_case_substitute(self, mapping):
        if not mapping:
            raise TypeError(
                "Descriptor 'ignore_case_substitute' of 'BakerTemplate' "
                "object needs an argument."
            )

        def convert(mo):
            named = mo.group('named')
            if named is not None:
                return str(mapping[named.lower()])
            if mo.group('escaped') is not None:
                return self.delimiter
            if mo.group('invalid') is not None:
                self._invalid(mo)
            raise ValueError('Unrecognized named group in pattern', self.pattern)
        return self.pattern.sub(convert, self.template)
