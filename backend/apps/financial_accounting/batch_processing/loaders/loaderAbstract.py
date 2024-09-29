import os
import re
from abc import ABC, abstractmethod


class LoaderAbstract(ABC):
    source_type = 'FILE'

    def __init__(self):
        self.path = None
        self.type = None

    @abstractmethod
    def clean(self, txt):
        pass
        # raise NotImplementedError('subclasses must override clean()')

    @abstractmethod
    def process(self, filename, data, file):
        pass
        # raise NotImplementedError('subclasses must override load()')

    @abstractmethod
    # rozksięgowanie transakcji dla produktów
    def account_products(self):
        pass

    def _get_file_content(self, filename, encoding='ISO-8859-2'):
        with open(file=os.path.join(self.path, filename), mode='rt', encoding=encoding, errors='ignore') as f:
            data = f.read().encode(encoding='utf-8').decode()

        return self.clean(data)

    def load(self, filename, file_id):
        data = self._get_file_content(filename)
        return self.process(filename, data, file_id)

    def check_filename_format(self, filename):
        return True

    def get_file_list(self):
        return [
            f for f in os.listdir(self.path)
            if os.path.isfile(os.path.join(self.path, f)) and self.check_filename_format(str(f))
        ]

    def _get_regex_value(self, regex, data, group, raise_error=False):
        result = re.findall(regex, data)
        if not result:
            if raise_error:
                raise Exception('nie znaleziono wartości regex: ' + regex)
            return None
        if group is not None or group != 0:
            try:
                return result[0][group - 1]
            except IndexError:
                return None
        return result
