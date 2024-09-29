import os

from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse

from apps.address.models import Address
from apps.document.models import DocumentType
from apps.user.models import UserBatchUploadBuffer, User, UserBatchUploadLog
from apps.user.utils import set_username
from apps.user_func.adviser.models import Adviser
from apps.user_func.broker.models import Broker
from apps.user_func.client.models import Client
from py3ws.csvutl import validator

HEADER = [
    {"column": "user.first_name", "csv_header": "Imię", "validators": [validator.VALIDATOR_TYPE_NOT_NULL]},
    {"column": "user.last_name", "csv_header": "Nazwisko", "validators": [validator.VALIDATOR_TYPE_NOT_NULL]},
    {"column": "user.company_name", "csv_header": "Nazwa Firmy", "validators": []},
    {"column": "user.tags", "csv_header": "tagi", "validators": []},
    {"column": "user.phone_one", "csv_header": "telefon", "validators": [validator.VALIDATOR_TYPE_NOT_NULL, validator.VALIDATOR_TYPE_NUMERIC]},
    {"column": "user.email", "csv_header": "mail", "validators": [validator.VALIDATOR_TYPE_EMAIL, validator.VALIDATOR_TYPE_GLOBAL_UNIQUE]},
    {"column": "client.adviser_email", "csv_header": "mail opiekuna", "validators": [validator.VALIDATOR_TYPE_EMAIL]},
    {"column": "user.personal_id", "csv_header": "PESEL", "validators": [validator.VALIDATOR_TYPE_PESEL, validator.VALIDATOR_TYPE_GLOBAL_UNIQUE]},
    {"column": "user.nip", "csv_header": "NIP", "validators": [validator.VALIDATOR_TYPE_NIP, validator.VALIDATOR_TYPE_GLOBAL_UNIQUE]},
    {"column": "user.regon", "csv_header": "REGON", "validators": [validator.VALIDATOR_TYPE_GLOBAL_UNIQUE]},
    {"column": "user.krs", "csv_header": "KRS", "validators": [validator.VALIDATOR_TYPE_KRS, validator.VALIDATOR_TYPE_GLOBAL_UNIQUE]},
    {"column": "address.city", "csv_header": "Miasto", "validators": []},
    {"column": "address.street", "csv_header": "ulica", "validators": []},
    {"column": "address.street_no", "csv_header": "nr", "validators": []},
    {"column": "address.apartment_no", "csv_header": "nr lokalu", "validators": []},
    {"column": "addres.post_code", "csv_header": "kod pocztowy", "validators": []}
]


class CsvBatchUpload:
    def __init__(self, process_id, user):
        self.process_id = process_id
        self.user = user

    def _get_row(self, data_row, idx):
        row = {}

        for i in HEADER:
            column = i['column'].split('.')[1]
            row[column] = data_row[i['csv_header'].lower()][:UserBatchUploadBuffer._meta.get_field(column).max_length]

        row['errors'] = data_row['__errors__']
        row['process_id'] = self.process_id
        row['sq'] = idx

        return row

    def _validate_csv_user_ids(self, row: dict, idx):
        q = Q()
        if row['pesel']:
            q |= Q(personal_id=row['pesel'])
        if row['nip']:
            q |= Q(nip=row['nip'])
        if row['krs']:
            q |= Q(krs=row['krs'])
        if row['regon']:
            q |= Q(regon=row['regon'])
        if row['mail']:
            q |= Q(email=row['mail'])
        if row['telefon']:
            q |= Q(phone_one=row['telefon'])

        if not q:
            row['__errors__'].append(
                {
                    'row': idx + 2,
                    'code': 2000,  # todo: DRUT!!!
                    'field': '__row__',
                    'record': None,
                    'message': 'Nie znaleziono żadnego identyfikatora klienta',
                    'missing': ''
                }
            )
            return False

        if User.objects.filter(q).count():
            row['__errors__'].append(
                {
                    'row': idx + 2,
                    'code': 2000,  # todo: DRUT!!!
                    'field': '__row__',
                    'record': None,
                    'message': 'Klient o podanym numerze telefonu, pesel, nip, regon, krs lub email już istnieje w systemie',
                    'missing': ''
                }
            )
            return False

        return True

    def _validate_csv_adviser(self, row, idx):
        if row['__errors__']:
            for e in row['__errors__']:
                if e['field'] == 'mail opiekuna':
                    # it means that some other errors are on the advisor email field. No need to check further then
                    return

        if row['mail opiekuna']:
            try:
                adviser = User.objects.get(email=row['mail opiekuna'])
                return adviser

            except User.DoesNotExist:
                row['__errors__'].append(
                    {
                        'row': idx + 2,
                        'code': 2000,  # todo: DRUT!!!
                        'field': 'mail opiekuna',
                        'record': None,
                        'message': 'Nie znaleziono opiekuna o podanym adresie e-mail',
                        'missing': ''
                    }
                )
                return

    def load_users_into_buffer_table(self, data):
        UserBatchUploadBuffer.objects.filter(process_id=self.process_id).delete()

        if not data:
            return True

        valid = True

        for idx, row in enumerate(data):
            valid = valid and self._validate_csv_user_ids(row, idx)
            adviser = self._validate_csv_adviser(row, idx)

            db_row = self._get_row(row, idx)

            if adviser:
                db_row['adviser'] = adviser.pk

            # We have to set empty unique fields as None to avoid unique constraints error (any values lik '' etc.)
            # To do this we get list of table columns which have entry _unique=True and set None for the row columns if equal to '' or not if condition
            for n in list(map(lambda y: y.name, list(filter(lambda x: vars(x)['_unique'], User._meta.fields)))):
                if n in db_row:
                    db_row[n] = None if db_row[n] == '' or not db_row[n] else db_row[n]

            UserBatchUploadBuffer.objects.create(**db_row)

        return valid

    def _get_address(self, row):
        if row.street and row.city:
            return Address.objects.create(
                city=row.city,
                street=row.street,
                street_no=row.street_no,
                apartment_no=row.apartment_no
            )
        return None

    def _get_user(self, row, address):
        return User.objects.create(
            username=set_username(first_name=row.first_name, last_name=row.last_name, company_name=row.company_name),
            first_name=row.first_name,
            last_name=row.last_name,
            company_name=row.company_name,
            tags=row.tags.split(',') if row.tags else None,
            phone_one=row.phone_one,
            email=row.email,
            personal_id=row.personal_id,
            nip=row.nip,
            regon=row.regon,
            krs=row.krs,
            home_address=address,
            process_id=self.process_id
        )

    def _upload_user_func(self, row, user, user_type):
        cl = None
        if user_type == 'CLIENT':
            cl = Client

        elif user_type == 'BROKER':
            cl = Broker

        if cl:
            cl.objects.create(
                user=user,
                document_type=DocumentType.objects.get(code=user_type),
                adviser=Adviser.objects.get(pk=row.adviser) if row.adviser else None
            )

    def _log_upload(self, row_count):
        UserBatchUploadLog.objects.create(
            id=self.process_id,
            created_by=self.user.username,
            row_count=row_count
        )

    def upload(self, user_type):
        if not user_type:
            raise Exception('Parameter "user_type" must be given')

        rows = UserBatchUploadBuffer.objects.filter(process_id=self.process_id)

        if not rows:
            return

        with transaction.atomic():
            for row in rows:
                self._upload_user_func(row, self._get_user(row, self._get_address(row)), user_type)

            self._log_upload(rows.count())
            rows.delete()


def download():
    template_name = 'client_csv_import.xls'

    output_file_path = os.path.join(settings.MEDIA_ROOT, f'files/templates/')
    os.makedirs(output_file_path, exist_ok=True)

    output_file_path = os.path.join(output_file_path, template_name)

    with open(output_file_path, 'r+b') as f:
        response = HttpResponse(f.read(), content_type='%s; %s' % ('application/vnd.ms-excel', 'charset=utf-8'))
        response['Content-Disposition'] = f'attachment; filename="{template_name}"'
        f.close()

        return response
