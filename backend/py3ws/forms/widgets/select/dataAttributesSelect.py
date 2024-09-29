from django.forms.widgets import Select
import pprint

class DataAttributesSelect(Select):
    def __init__(self, attrs=None, choices=(), data=None):
        super(DataAttributesSelect, self).__init__(attrs, choices)
        self.data = data

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super(DataAttributesSelect, self).create_option(name, value, label, selected, index, subindex=None, attrs=None)
        # adds the data-attributes to the attrs context var
        try:
            for i, v in self.data[option['value']].items():
                option['attrs']['data-%s' % i] = v
        except AttributeError:
            pass
        return option


class DataAttributesSelect1(Select):
    def __init__(self, attrs=None, choices=(), data=None):
        super(DataAttributesSelect1, self).__init__(attrs, choices)
        self.data = data

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super(DataAttributesSelect1, self).create_option(name, value, label, selected, index, subindex=None, attrs=None)
        # adds the data-attributes to the attrs context var
        try:
            option['attrs']['data-%s' % self.data[option['value']]['name']] = self.data[option['value']]['value']
        except AttributeError:
            pass
        return option