
from apps.document.models import Document, DocumentAttribute


# TODO: docelowo przenieść jako standardowa funkcjonalność w procesie
class PZ1:
    @staticmethod
    def _status_flow_copy_data(user, id, mapping):
        document = Document.objects.get(pk=id)
        # mapping: {'source_attr_code': 'dest_attr_code'}

        tmp = []
        for k, v in mapping.items():
            tmp.append(k)
            tmp.append(v)

        attributes = {i.attribute.code: i for i in DocumentAttribute.objects.filter(attribute__code__in=tmp, document_id=document.pk)}

        for k, v in mapping.items():
            attributes[v].value = attributes[k].value
            attributes[v].save()

    @staticmethod
    def dcr_copy_data(user, id):
        # {'source_attr_code': 'dest_attr_code'}
        mapping = {
            '1_9fd0e82fe574444d8832fc0186e92195': '1_b0618ba527264770b70cc35ea1053f23',  # max kwota II
            '1_1380877d7fc14dbe9a43ae2d70e4270d': '1_4fd23d32bf484093ae2bc6a2e7973a8d',  # max kwota IV
            '1_3331fd8606554eeea38197bcfab6a845': '1_5820c757fdd74d3a8def353ebddf68b5',  # prowizja II
            '1_a91d15fb72164bd8833aaad5c83bdd3e': '1_58bf55f6da8049639ea73b68fd6ae652',  # prowizja IV
        }
        PZ1._status_flow_copy_data(user, id, mapping)

    @staticmethod
    def dcz_copy_data(user, id):
        # {'source_attr_code': 'dest_attr_code'}
        mapping = {
            '1_b0618ba527264770b70cc35ea1053f23': '1_b0618ba527264770b70cc35ea1053f23_1',  # max kwota II
            '1_4fd23d32bf484093ae2bc6a2e7973a8d': '1_4fd23d32bf484093ae2bc6a2e7973a8d_1',  # max kwota IV
            '1_5820c757fdd74d3a8def353ebddf68b5': '1_5820c757fdd74d3a8def353ebddf68b5_1',  # prowizja II
            '1_58bf55f6da8049639ea73b68fd6ae652': '1_58bf55f6da8049639ea73b68fd6ae652_1',  # prowizja IV
            '1_c032458a6e4d4377870718a356044230': '1_c032458a6e4d4377870718a356044230_1'  # forma zabezpieczenia
        }
        PZ1._status_flow_copy_data(user, id, mapping)

    @staticmethod
    def dcg_copy_data(user, id):
        # {'source_attr_code': 'dest_attr_code'}
        mapping = {
            '1_b0618ba527264770b70cc35ea1053f23_1': '1_b0618ba527264770b70cc35ea1053f23_2',  # max kwota II
            '1_4fd23d32bf484093ae2bc6a2e7973a8d_1': '1_4fd23d32bf484093ae2bc6a2e7973a8d_2',  # max kwota IV
            '1_5820c757fdd74d3a8def353ebddf68b5_1': '1_5820c757fdd74d3a8def353ebddf68b5_2',  # prowizja II
            '1_58bf55f6da8049639ea73b68fd6ae652_1': '1_58bf55f6da8049639ea73b68fd6ae652_2',  # prowizja IV
            '1_c032458a6e4d4377870718a356044230_1': '1_c032458a6e4d4377870718a356044230_2'  # forma zabezpieczenia
        }
        PZ1._status_flow_copy_data(user, id, mapping)
