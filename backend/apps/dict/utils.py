from apps.dict.models import DictionaryEntry, Dictionary


def get_all_dict():
    dtc = {}
    d = Dictionary.objects.all()

    for i in d:
        dtc[i.code] = DictionaryEntry.objects.filter(dictionary__code=i.code).order_by('sq')

    return dtc


def get_dict(dict_name):
    d = DictionaryEntry.objects.filter(dictionary__code=dict_name).order_by('sq')
    return [{'pk': i.pk, 'label': i.label, 'value': i.value} for i in d]