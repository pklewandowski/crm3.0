import pprint

import datetime
from py3ws import utils as py3ws_utils

from apps.document.models import Document, DocumentAttribute, DocumentTypeAttribute, DocumentTypeSection
from apps.user_func.adviser.models import Adviser
from apps.user_func.broker.models import Broker
from apps.user_func.client.models import Client


def getter_result(fn, val):
    return py3ws_utils.call_def_form_str(fn, val)
    # module_name = ".".join(fn.split(".")[:-1])
    # function_name = fn.split(".")[-1]
    # m = __import__(module_name, fromlist=[''])
    # return getattr(m, function_name)(val)


def get_attribute(key, dict):
    if key in dict:
        return dict[key] or ''
    else:
        return ''


def xml_entity(txt):
    if not txt:
        return ''
    return txt.replace('&', '&amp;').replace('>', '&gt;').replace('<', '&lt;')


def get_xml_data(document_id, report_id):
    document = Document.objects.get(pk=document_id)

    xml_client_template = """
    <client>
            <firstName><![CDATA[__FIRST_NAME__]]></firstName>
            <lastName><![CDATA[__LAST_NAME__]]></lastName>
            <companyName><![CDATA[__COMPANY_NAME__]]></companyName>
            <birthDate><![CDATA[__BIRTH_DATE__]]></birthDate>
            <pesel><![CDATA[__PERSONAL_ID__]]></pesel>
            <nip><![CDATA[__NIP__]]></nip>
            <establishDate><![CDATA[__COMPANY_ESTABLISH_DATE__]]></establishDate>
            <isFirm><![CDATA[__IS_FIRM__]]></isFirm>
            <address><![CDATA[__ADDRESS__]]></address>
        </client>"""

    xml_gpd_type = {"PB": "Wnioskujący", "PR": "Poręczyciel", "PRI": "Poręczyciel instytucjonalny", "DZ": "Dłużnik rzeczowy"}

    xml_gpd_template = """
    <guarntorProxyDebtor>
            <name><![CDATA[__NAME__]]></name>
            <regon><![CDATA[__REGON__]]></regon>
            <nip><![CDATA[__NIP__]]></nip>
            <firstName><![CDATA[__FIRST_NAME__]]></firstName>
            <lastName><![CDATA[__LAST_NAME__]]></lastName>
            <birthDate><![CDATA[__BIRTH_DATE__]]></birthDate>
            <pesel><![CDATA[__PERSONAL_ID__]]></pesel>
            <nip><![CDATA[__NIP__]]></nip>
            <establishDate><![CDATA[__COMPANY_ESTABLISH_DATE__]]></establishDate>
            <isFirm><![CDATA[__IS_FIRM__]]></isFirm>
            <address><![CDATA[__ADDRESS__]]></address>
            <contractParty><![CDATA[__CONTACT_PARTY__]]></contractParty>
    </guarntorProxyDebtor>"""

    i_guarantor_template = """
    <institutionalGuarntor>
        <name><![CDATA[__NAME__]]></name>
        <regon><![CDATA[__REGON__]]></regon>
        <nip><![CDATA[__NIP__]]></nip>
        <firstName><![CDATA[__FIRST_NAME__]]></firstName>
        <lastName><![CDATA[__LAST_NAME__]]></lastName>
        <address><![CDATA[__ADDRESS__]]></address>
        <mailAddress><![CDATA[__MAIL_ADDRESS__]]></mailAddress>			
    </institutionalGuarntor>"""

    xml_loan_data_template = """
        <hpt_lenderPrc>__HPT_LENDER_PRC__</hpt_lenderPrc>
        <hpt_igCommision>__HPT_IG_COMMISSION__</hpt_igCommision>
        <hpt_maxGuaranteeAmount>__HPT_MAX_GUARANTEE_AMOUNT__</hpt_maxGuaranteeAmount>
        <hpt_loanTime>__HPT_LOAN_TIME__</hpt_loanTime>
        <hpt_ltvTotal>__HPT_LTV_TOTAL__</hpt_ltvTotal>
        <hpt_ltvGross>__HPT_LTV_GROSS__</hpt_ltvGross>
        <hpt_interest>__HPT_INTEREST__</hpt_interest>
        <hpt_totalAmountNet>__HPT_TOTAL_AMOUNT_NET__</hpt_totalAmountNet>
        <hpt_totalAmountGross>__HPT_TOTAL_AMOUNT_GROSS__</hpt_totalAmountGross>
        
        <prw_lenderPrc>__PRW_LENDER_PRC__</prw_lenderPrc>
        <prw_igCommision>__PRW_IG_COMMISSION__</prw_igCommision>
        <prw_maxGuaranteeAmount>__PRW_MAX_GUARANTEE_AMOUNT__</prw_maxGuaranteeAmount>
        <prw_loanTime>__PRW_LOAN_TIME__</prw_loanTime>
        <prw_ltvTotal>__PRW_LTV_TOTAL__</prw_ltvTotal>
        <prw_ltvGross>__PRW_LTV_GROSS__</prw_ltvGross>
        <prw_interest>__PRW_INTEREST__</prw_interest>
        <prw_totalAmountNet>__PRW_TOTAL_AMOUNT_NET__</prw_totalAmountNet>
        <prw_totalAmountGross>__PRW_TOTAL_AMOUNT_GROSS__</prw_totalAmountGross>
        """

    xml_security_template = """
    <security>
        <type><![CDATA[__TYPE__]]></type>
        <owners>
        __SECURITY_OWNERS__
        </owners>
        <kw><![CDATA[__KW__]]></kw>
        <value>__VALUE__</value>
        <address><![CDATA[__ADDRESS__]]></address>
        <security_type><![CDATA[__SECURITY_TYPE__]]></security_type>
        <notes><![CDATA[__NOTES__]]></notes>
    </security>
    """

    xml_security_owners_template = """   
    <owner>
        <firstName><![CDATA[__FIRST_NAME__]]></firstName>
        <lastName><![CDATA[__LAST_NAME__]]></lastName>
        <companyName><![CDATA[__COMPANY_NAME__]]></companyName>
        <birthDate><![CDATA[__BIRTH_DATE__]]></birthDate>
        <pesel><![CDATA[__PESEL__]]></pesel>
        <address><![CDATA[__ADDRESS__]]></address>
    </owner>
    """

    xml_conditions_template = """
    <condition>
        <description><![CDATA[__DESCRIPTION__]]></description>
        <deadlineDay>__DEADLINE_DAY__</deadlineDay>
    </condition>
    """

    xml_individual_entry_template = """
    <entry>
        <description><![CDATA[__DESCRIPTION__]]></description>
    </entry>
    """

    xml = """<?xml version="1.0" encoding="UTF-8"?>
<document>
    <code><![CDATA[__CODE__]]></code>
    <creationDate><![CDATA[__CREATION_DATE__]]></creationDate>
    <clientType><![CDATA[__CLIENT_TYPE__]]></clientType>
    <source><![CDATA[__SOURCE__]]></source>
    <adviser><![CDATA[__ADVISER__]]></adviser>
    <broker><![CDATA[__BROKER__]]></broker>
    <agreementType><![CDATA[__AGREEMENT_TYPE__]]></agreementType>
    <fastTrack><![CDATA[__FAST_TRACK__]]></fastTrack>
    <clients>__CLIENTS__</clients>
    <guarntorProxyDebtors>__GPDS__</guarntorProxyDebtors>   
    <institutionalGuarntors>__IGS__</institutionalGuarntors>
    <loanData>__LOAN_DATA__</loanData>
    <securities>__SECURITIES__</securities>
    <conditions>
        <agreement>
            <sales>__AGREEMENT_CONDITIONS_SALES__</sales>
            <lo>__AGREEMENT_CONDITIONS_LO__</lo>
            <analysis>__AGREEMENT_CONDITIONS_ANALYSIS__</analysis>
            <proxy>__AGREEMENT_CONDITIONS_PROXY__</proxy>            
        </agreement>
        <beforeLaunch>
            <analysis>__BEFORE_LAUNCH_CONDITIONS_ANALYSIS__</analysis>
            <lo>__BEFORE_LAUNCH_CONDITIONS_LO__</lo>
            <execution>__BEFORE_LAUNCH_CONDITIONS_EXECUTION__</execution>         
        </beforeLaunch>
        <afterLaunch>
            <lo>__AFTER_LAUNCH_CONDITIONS_LO__</lo>
            <execution>__AFTER_LAUNCH_CONDITIONS_EXECUTION__</execution>
        </afterLaunch>
    </conditions>
    <individualEntries>
        __INDIVIDUAL_ENTRIES__
    </individualEntries>
</document>
"""

    global_attr = {i.attribute.pk: i.value for i in DocumentAttribute.objects.filter(document_id=document.pk, attribute__section__parent__isnull=True)}
    client_attr = DocumentAttribute.objects.filter(document_id=document.pk, attribute=DocumentTypeAttribute.objects.get(pk=251))

    loan_security = {}
    loan_conditions = {}

    for i in DocumentAttribute.objects.filter(attribute__section_column__in=[46, 85, 45, 44], document_id=document.pk, parent__isnull=True):
        if i.row_uid not in loan_security.keys():
            loan_security[i.row_uid] = {}
        loan_security[i.row_uid][i.attribute.pk] = i.value

    loan_conditions['agreement'] = {}

    loan_conditions['agreement']['sales'] = [i.value for i in DocumentAttribute.objects.filter(attribute=332,
                                                                                               document_id=document.pk).order_by('row_sq')]
    loan_conditions['agreement']['lo'] = [i.value for i in DocumentAttribute.objects.filter(attribute=327,
                                                                                            document_id=document.pk).order_by('row_sq')]
    loan_conditions['agreement']['analysis'] = [i.value for i in DocumentAttribute.objects.filter(attribute=263,
                                                                                                  document_id=document.pk).order_by('row_sq')]
    loan_conditions['agreement']['proxy'] = [i.value for i in DocumentAttribute.objects.filter(attribute=336,
                                                                                               document_id=document.pk).order_by('row_sq')]

    loan_conditions['before_launch'] = {}

    loan_conditions['before_launch']['analysis'] = [i.value for i in DocumentAttribute.objects.filter(attribute=262,
                                                                                                      document_id=document.pk).order_by('row_sq')]
    loan_conditions['before_launch']['lo'] = [i.value for i in DocumentAttribute.objects.filter(attribute=376,
                                                                                                document_id=document.pk).order_by('row_sq')]
    loan_conditions['before_launch']['execution'] = [i.value for i in DocumentAttribute.objects.filter(attribute=380,
                                                                                                       document_id=document.pk).order_by('row_sq')]

    after_launch = {'lo': {}, 'execution': {}}

    for i in DocumentAttribute.objects.filter(document_id=document.pk, attribute=295):
        after_launch['lo'][i.row_uid] = {"description": i.value}
    for i in DocumentAttribute.objects.filter(document_id=document.pk, attribute=258):
        after_launch['lo'][i.row_uid]["deadline_day"] = i.value

    for i in DocumentAttribute.objects.filter(document_id=document.pk, attribute=389):
        after_launch['execution'][i.row_uid] = {"description": i.value}
    for i in DocumentAttribute.objects.filter(document_id=document.pk, attribute=387):
        after_launch['execution'][i.row_uid]["deadline_day"] = i.value

    loan_conditions['after_launch'] = after_launch

    xml_clients = ""
    xml_gpds = ""
    xml_igs = ""
    xml_securities = ""
    xml_loan_data = xml_loan_data_template

    client_type = 'Osoba fizyczna'

    if document.owner:

        c = document.owner
        if c.is_company:
            client_type = 'Firma'
        xml_client = xml_client_template
        xml_client = xml_client.replace('__IS_FIRM__', 'T' if c.is_company else 'N')
        xml_client = xml_client.replace('__NIP__', c.nip or '')
        xml_client = xml_client.replace('__COMPANY_NAME__', xml_entity(c.company_name or ''))
        xml_client = xml_client.replace('__FIRST_NAME__', xml_entity(c.first_name or ''))
        xml_client = xml_client.replace('__LAST_NAME__', xml_entity(c.last_name or ''))
        xml_client = xml_client.replace('__BIRTH_DATE__', xml_entity(str(c.birth_date) if c.birth_date else ''))
        xml_client = xml_client.replace('__PERSONAL_ID__', xml_entity(c.personal_id or ''))
        xml_client = xml_client.replace('__ADDRESS__', xml_entity(c.get_compact_address()))
        xml_client = xml_client.replace('__COMPANY_ESTABLISH_DATE__', '' if not c.is_company else str(c.company_establish_date or ''))
        xml_clients += xml_client

    for i in client_attr:
        xml_client = xml_client_template

        if not i.value:
            continue

        c = Client.objects.get(pk=i.value)
        if c.user.is_company:
            client_type = 'Firma'
        xml_client = xml_client.replace('__IS_FIRM__', 'T' if c.user.is_company else 'N')
        xml_client = xml_client.replace('__NIP__', c.user.nip or '')
        xml_client = xml_client.replace('__FIRST_NAME__', xml_entity(c.user.first_name or ''))
        xml_client = xml_client.replace('__LAST_NAME__', xml_entity(c.user.last_name or '' if not c.user.is_company else c.user.company_name or ''))
        xml_client = xml_client.replace('__BIRTH_DATE__', xml_entity(str(c.user.birth_date) if c.user.birth_date else ''))
        xml_client = xml_client.replace('__PERSONAL_ID__', xml_entity(c.user.personal_id or ''))
        xml_client = xml_client.replace('__ADDRESS__', xml_entity(c.user.get_compact_address()))
        xml_client = xml_client.replace('__COMPANY_ESTABLISH_DATE__', '' if not c.user.is_company else str(c.user.company_establish_date or ''))
        xml_clients += xml_client

    xml_security_type_dict = {"FLAT": "Mieszkanie",
                              "HOUSE": "Dom",
                              "ESTATE_COM": "Nieruchomość komercyjna",
                              "ESTATE_XXX": "Nieruchomość inna",
                              "LAND": "Działka / Działka rolna",
                              "CAR": "Samochód",
                              "XXX": "Inne"}
    xml_security_sec_type = {"II": "Przewłaszczenie", "IV": "Hipoteka"}

    for i in loan_security.keys():

        sec_type = loan_security[i][36]
        if not sec_type:
            continue

        xml_security = xml_security_template
        xml_security = xml_security.replace("__TYPE__", xml_security_type_dict[loan_security[i][36]] or '' if 36 in loan_security[i] else '')
        xml_security = xml_security.replace("__VALUE__", loan_security[i][282] or '' if 282 in loan_security[i] else '')
        xml_security = xml_security.replace("__KW__", loan_security[i][41] or 'BRAK' if 41 in loan_security[i] else 'BRAK')
        xml_security = xml_security.replace("__NOTES__", xml_entity(loan_security[i][276] or 'BRAK' if 276 in loan_security[i] else 'BRAK'))
        xml_security = xml_security.replace("__ADDRESS__", "%s, %s %s" % (
            xml_entity(loan_security[i][38] or '' if 38 in loan_security[i] else ''),
            xml_entity(loan_security[i][40] or '' if 40 in loan_security[i] else ''),
            xml_entity(loan_security[i][39] or '' if 39 in loan_security[i] else '')
        ))
        try:
            xml_security = xml_security.replace("__SECURITY_TYPE__", xml_security_sec_type[loan_security[i][33]] or '' if 33 in loan_security[i] else '')
        except KeyError:
            pass

        guarantor_type = get_attribute(224, loan_security[i])
        try:
            security_owners = DocumentAttribute.objects.filter(parent=DocumentAttribute.objects.get(row_uid=i, attribute=DocumentTypeAttribute.objects.get(pk=252)))
        except DocumentAttribute.DoesNotExist:
            security_owners = None

        xml_security_owners = ""

        if security_owners:
            for s in security_owners:

                if not s.value:
                    continue

                c = Client.objects.get(pk=int(s.value))

                xml_security_owner = xml_security_owners_template

                xml_security_owner = xml_security_owner.replace('__FIRST_NAME__', xml_entity(c.user.first_name or ''))
                xml_security_owner = xml_security_owner.replace('__COMPANY_NAME__', xml_entity(c.user.company_name or ''))
                xml_security_owner = xml_security_owner.replace('__LAST_NAME__', xml_entity(c.user.last_name or ''))
                xml_security_owner = xml_security_owner.replace('__BIRTH_DATE__', xml_entity(str(c.user.birth_date) or ''))
                xml_security_owner = xml_security_owner.replace('__PESEL__', xml_entity(c.user.personal_id or ''))
                xml_security_owner = xml_security_owner.replace('__ADDRESS__', xml_entity(c.user.get_compact_address()))
                xml_security_owners += xml_security_owner

                xml_gpd = xml_gpd_template
                xml_ig = i_guarantor_template

                if guarantor_type == 'PRI':

                    xml_ig = xml_ig.replace('__NAME__', xml_entity(c.user.company_name or ''))
                    xml_ig = xml_ig.replace('__REGON__', xml_entity(c.user.regon or ''))
                    xml_ig = xml_ig.replace('__NIP__', xml_entity(c.user.nip or ''))
                    xml_ig = xml_ig.replace('__COMPANY_ESTABLISH_DATE__', xml_entity(str(c.user.company_establish_date) or ''))
                    xml_ig = xml_ig.replace('__FIRST_NAME__', xml_entity(c.user.first_name or ''))
                    xml_ig = xml_ig.replace('__LAST_NAME__', xml_entity(c.user.last_name or ''))
                    xml_ig = xml_ig.replace('__ADDRESS__', xml_entity(c.user.get_compact_address()))
                    xml_ig = xml_ig.replace('__MAIL_ADDRESS__', '')
                    xml_igs += xml_ig

                else:
                    xml_gpd = xml_gpd.replace('__NAME__', xml_entity(c.user.company_name or ''))
                    xml_gpd = xml_gpd.replace('__REGON__', xml_entity(c.user.regon or ''))
                    xml_gpd = xml_gpd.replace('__NIP__', xml_entity(c.user.nip or ''))
                    xml_gpd = xml_gpd.replace('__COMPANY_ESTABLISH_DATE__', xml_entity(str(c.user.company_establish_date) or ''))
                    xml_gpd = xml_gpd.replace('__FIRST_NAME__', xml_entity(c.user.first_name or ''))
                    xml_gpd = xml_gpd.replace('__LAST_NAME__', xml_entity(c.user.last_name or ''))
                    xml_gpd = xml_gpd.replace('__BIRTH_DATE__', xml_entity(str(c.user.birth_date) if c.user.birth_date else ''))
                    xml_gpd = xml_gpd.replace('__PERSONAL_ID__', xml_entity(c.user.personal_id or ''))
                    xml_gpd = xml_gpd.replace('__ADDRESS__', xml_entity(c.user.get_compact_address()))
                    xml_gpd = xml_gpd.replace('__CONTACT_PARTY__', xml_entity(xml_gpd_type[guarantor_type] or ''))
                    xml_gpds += xml_gpd

        xml_security = xml_security.replace("__SECURITY_OWNERS__", xml_security_owners or '')
        xml_securities += xml_security

    # LOAN_CONDITIONS
    # -- AGREEMENT CONDITIONS

    xml_conditions = ''
    for i in loan_conditions['agreement']['sales']:
        xml_condition = xml_conditions_template
        xml_condition = xml_condition.replace("__DESCRIPTION__", xml_entity(i))
        xml_condition = xml_condition.replace("__DEADLINE_DAY__", '')
        xml_conditions += xml_condition
    xml = xml.replace("__AGREEMENT_CONDITIONS_SALES__", xml_conditions)

    xml_conditions = ''
    for i in loan_conditions['agreement']['lo']:
        xml_condition = xml_conditions_template
        xml_condition = xml_condition.replace("__DESCRIPTION__", xml_entity(i))
        xml_condition = xml_condition.replace("__DEADLINE_DAY__", '')
        xml_conditions += xml_condition
    xml = xml.replace("__AGREEMENT_CONDITIONS_LO__", xml_conditions)

    xml_conditions = ''
    for i in loan_conditions['agreement']['analysis']:
        xml_condition = xml_conditions_template
        xml_condition = xml_condition.replace("__DESCRIPTION__", xml_entity(i))
        xml_condition = xml_condition.replace("__DEADLINE_DAY__", '')
        xml_conditions += xml_condition
    xml = xml.replace("__AGREEMENT_CONDITIONS_ANALYSIS__", xml_conditions)

    xml_conditions = ''
    for i in loan_conditions['agreement']['proxy']:
        xml_condition = xml_conditions_template
        xml_condition = xml_condition.replace("__DESCRIPTION__", xml_entity(i))
        xml_condition = xml_condition.replace("__DEADLINE_DAY__", '')
        xml_conditions += xml_condition
    xml = xml.replace("__AGREEMENT_CONDITIONS_PROXY__", xml_conditions)

    # --BEFORE LAUNCH
    xml_conditions = ''
    for i in loan_conditions['before_launch']['analysis']:
        xml_condition = xml_conditions_template
        xml_condition = xml_condition.replace("__DESCRIPTION__", xml_entity(i))
        xml_condition = xml_condition.replace("__DEADLINE_DAY__", '')
        xml_conditions += xml_condition
    xml = xml.replace("__BEFORE_LAUNCH_CONDITIONS_ANALYSIS__", xml_conditions)

    xml_conditions = ''
    for i in loan_conditions['before_launch']['lo']:
        xml_condition = xml_conditions_template
        xml_condition = xml_condition.replace("__DESCRIPTION__", xml_entity(i))
        xml_condition = xml_condition.replace("__DEADLINE_DAY__", '')
        xml_conditions += xml_condition
    xml = xml.replace("__BEFORE_LAUNCH_CONDITIONS_LO__", xml_conditions)

    xml_conditions = ''
    for i in loan_conditions['before_launch']['execution']:
        xml_condition = xml_conditions_template
        xml_condition = xml_condition.replace("__DESCRIPTION__", xml_entity(i))
        xml_condition = xml_condition.replace("__DEADLINE_DAY__", '')
        xml_conditions += xml_condition
    xml = xml.replace("__BEFORE_LAUNCH_CONDITIONS_EXECUTION__", xml_conditions)

    xml_conditions = ''
    for k, i in loan_conditions['after_launch']['lo'].items():
        xml_condition = xml_conditions_template
        xml_condition = xml_condition.replace("__DESCRIPTION__", xml_entity(i['description'] if 'description' in i and i['description'] else ''))
        xml_condition = xml_condition.replace("__DEADLINE_DAY__", xml_entity(i['deadline_day'] if 'deadline_day' in i and i['deadline_day'] else ''))
        xml_conditions += xml_condition
    xml = xml.replace("__AFTER_LAUNCH_CONDITIONS_LO__", xml_conditions)

    xml_conditions = ''
    for k, i in loan_conditions['after_launch']['execution'].items():
        xml_condition = xml_conditions_template
        xml_condition = xml_condition.replace("__DESCRIPTION__", xml_entity(i['description'] if 'description' in i and i['description'] else ''))
        xml_condition = xml_condition.replace("__DEADLINE_DAY__", xml_entity(i['deadline_day'] if 'deadline_day' in i and i['deadline_day'] else ''))
        xml_conditions += xml_condition
    xml = xml.replace("__AFTER_LAUNCH_CONDITIONS_EXECUTION__", xml_conditions)

    # INDIVIDUAL_ENTRIES

    xml_individual_entries = ''
    for i in DocumentAttribute.objects.filter(document_id=document.pk, attribute__code='1_3d27a216f23121cd4be6f7e2bb09b942_2'):
        if not i.value:
            continue
        xml_individual_entry = xml_individual_entry_template
        xml_individual_entry = xml_individual_entry.replace("__DESCRIPTION__", xml_entity(i.value))

        xml_individual_entries += xml_individual_entry
    xml = xml.replace("__INDIVIDUAL_ENTRIES__", xml_individual_entries)


    # ADVISER

    id = get_attribute(222, global_attr)
    if id:
        try:
            adviser = Adviser.objects.get(pk=id)
            xml = xml.replace("__ADVISER__", "%s %s" % (xml_entity(adviser.user.first_name or ''), xml_entity(adviser.user.last_name or '')))
        except Adviser.DoesNotExist:
            xml = xml.replace("__ADVISER__", '')
    else:
        xml = xml.replace("__ADVISER__", '')

    # BROKER

    id = get_attribute(248, global_attr)
    if id:
        try:
            broker = Broker.objects.get(pk=id)
            xml = xml.replace("__BROKER__", "%s %s" % (xml_entity(broker.user.first_name or ''), xml_entity(broker.user.last_name or '')))
        except Broker.DoesNotExist:
            xml = xml.replace("__BROKER__", '')
    else:
        xml = xml.replace("__BROKER__", '')

    xml = xml.replace("__CODE__", xml_entity(document.code or ''))
    xml = xml.replace("__CLIENT_TYPE__", xml_entity(client_type or ''))

    # dtc = {"CC": "CC", "BRK": "Pośrednik", "ADV": "Doradca", "RCM": "Polecenie"}

    dtc = {i['lov_value']: i['lov_label'] for i in DocumentTypeAttribute.objects.get(pk=247).lov['data']}

    dtc_attr = get_attribute(247, global_attr)
    if dtc_attr:
        dtc_label = dtc[dtc_attr]
    else:
        dtc_label = ''
    xml = xml.replace("__SOURCE__", dtc_label or '')  # global_attr[247] or '')

    # dtc = {"NEW": "Nowa", "PRLG": "Prolongata", "ANX": "Aneks", "UGD": "Ugoda"}
    dtc = {i['lov_value']: i['lov_label'] for i in DocumentTypeAttribute.objects.get(pk=249).lov['data']}

    dtc_attr = get_attribute(249, global_attr)
    if dtc_attr:
        dtc_label = dtc[dtc_attr]
    else:
        dtc_label = ''
    xml = xml.replace("__AGREEMENT_TYPE__", dtc_label or '')

    # fast track
    if get_attribute(250, global_attr) == "True":
        val = 'Tak'
    else:
        val = 'Nie'

    xml = xml.replace("__CREATION_DATE__", datetime.datetime.strftime(document.creation_date, '%Y-%m-%d'))
    xml = xml.replace("__FAST_TRACK__", val or '')

    xml = xml.replace("__CLIENTS__", xml_clients or '')
    xml = xml.replace("__GPDS__", xml_gpds or '')
    xml = xml.replace("__IGS__", xml_igs or '')
    xml = xml.replace("__LOAN_DATA__", xml_loan_data or '')
    xml = xml.replace("__SECURITIES__", xml_securities or '')

    xml = xml.replace("__HPT_LENDER_PRC__", get_attribute(228, global_attr).replace(".", ","))
    xml = xml.replace("__HPT_IG_COMMISSION__", get_attribute(230, global_attr).replace(".", ","))
    xml = xml.replace("__HPT_MAX_GUARANTEE_AMOUNT__", get_attribute(232, global_attr).replace(".", ","))
    xml = xml.replace("__HPT_LOAN_TIME__", get_attribute(234, global_attr))
    xml = xml.replace("__HPT_LTV_TOTAL__", get_attribute(236, global_attr).replace(".", ","))
    xml = xml.replace("__HPT_LTV_GROSS__", get_attribute(238, global_attr).replace(".", ","))
    xml = xml.replace("__HPT_INTEREST__", get_attribute(240, global_attr).replace(".", ","))
    xml = xml.replace("__HPT_TOTAL_AMOUNT_NET__", get_attribute(242, global_attr).replace(".", ","))
    xml = xml.replace("__HPT_TOTAL_AMOUNT_GROSS__", get_attribute(244, global_attr).replace(".", ","))

    xml = xml.replace("__PRW_LENDER_PRC__", get_attribute(229, global_attr).replace(".", ","))
    xml = xml.replace("__PRW_IG_COMMISSION__", get_attribute(231, global_attr).replace(".", ","))
    xml = xml.replace("__PRW_MAX_GUARANTEE_AMOUNT__", get_attribute(233, global_attr).replace(".", ","))
    xml = xml.replace("__PRW_LOAN_TIME__", get_attribute(235, global_attr).replace(".", ","))
    xml = xml.replace("__PRW_LTV_TOTAL__", get_attribute(237, global_attr).replace(".", ","))
    xml = xml.replace("__PRW_LTV_GROSS__", get_attribute(239, global_attr).replace(".", ","))
    xml = xml.replace("__PRW_INTEREST__", get_attribute(241, global_attr).replace(".", ","))
    xml = xml.replace("__PRW_TOTAL_AMOUNT_NET__", get_attribute(243, global_attr).replace(".", ","))
    xml = xml.replace("__PRW_TOTAL_AMOUNT_GROSS__", get_attribute(245, global_attr).replace(".", ","))

    return xml
