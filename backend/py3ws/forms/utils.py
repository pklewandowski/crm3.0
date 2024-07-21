from django.conf import settings
from py3ws.utils import utils


# @static_var("h", "[")
def get_dictionary_hierarchy(entry):
    h = '{"id":"%s", "text":"%s"' % (entry.pk, entry.label)
    if entry.children_set.all():
        h += ', "icon":"jstree-folder", "li_attr" : { "class" : "hierarchy-tree-no-checkbox" },  "children":['
        for c in entry.children_set.all():
            h += get_dictionary_hierarchy(c)
        h = h[0: len(h) - 1] + ']'
    else:
        h += ', "icon":"jstree-file"'
    return h + "},"


def get_dictionary_entries(dictname, value='value', label='label', hierarchy=False):
    dict_class = settings.DICTIONARY_CLASS
    if not dict_class:
        raise Exception('brak definicji klasy słownika')
    cl = utils.myimport(dict_class)
    if not hierarchy:
        return []
        # return [(None, '-------')] + [(i, j) for i, j in cl.objects.filter(dictionary__code=dictname, active=True).order_by('sq').values_list(value, label)]
    else:
        h = '['
        for entry in cl.objects.filter(dictionary__code=dictname, active=True, parent=None).order_by('sq'):
            h += get_dictionary_hierarchy(entry)

        h = h[0: len(h) - 1] + ']'
        return h
