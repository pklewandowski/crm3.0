from pprint import pprint

from django.conf import settings
from django.shortcuts import render
from litex.regon import REGONAPI
from gusregon import GUS



class GusApi:
    service_url = 'https://wyszukiwarkaregon.stat.gov.pl/wsBIR/UslugaBIRzewnPubl.svc'  # TODO: get from config file/variable
    default_user_key = settings.GUSAPI_KEY  # 'a36a67dd1fcb46599458'

    def __init__(self, user_key=None):
        self.user_key = user_key or self.default_user_key
        self.get_api()

    def get_api(self):
        raise NotImplementedError

    def get_by_nip(self, nip):
        raise NotImplementedError

    def search(self, nip):
        print('not implemented')

    def get_pkd(self, nip):
        print('not implemented')
        pass

    def detailed_report(self, regon, type):
        print('not implemented')


# https://pypi.org/project/litex.regon/
"""
from apps.gus.gusapi import LitexClient
a = LitexClient()
a.get_by_nip('5251593572')
"""


class LitexClient(GusApi):

    def __init__(self, user_key=None):
        super().__init__(user_key)

    @staticmethod
    def _format_nip_data(obj):
        import re

        # lxml.objectify.ObjectifiedElement to dict
        def to_dict(element):
            ret = {}
            if element.getchildren() == []:
                return element.text
            else:
                for elem in element.getchildren():
                    subdict = to_dict(elem)
                    ret[re.sub('{.*}', '', elem.tag)] = subdict
            return ret

        return to_dict(obj)


    def get_api(self):
        self.api = REGONAPI(self.service_url)
        self.api.login(self.user_key)

    def get_by_nip(self, nip):
        return LitexClient._format_nip_data(self.api.search(nip=nip, detailed=True)[0])

    def detailed_report(self, regon, type='PublDaneRaportFizycznaOsoba'):
        return self.api.full_report(regon, type)


# https://pypi.org/project/gusregon/
class GusregonClient(GusApi):

    def __init__(self, user_key):
        super().__init__(user_key)

    def get_api(self):
        self.api = GUS(api_key=self.user_key)

    def get_by_nip(self, nip):
        return self.api.get_address(nip=nip)

    def search(self, nip):
        return self.api.search(nip=nip)

    def get_pkd(self, nip):
        self.api.get_pkd(nip=nip)
