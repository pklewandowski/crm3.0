import csv
import io

from django.conf import settings

from py3ws.csvutl.validator import validate_csv


def _map_columns_position(source_header, dest_header):
    return [source_header.index(col) for col in dest_header]


def _filter(row, filters: dict, header):
    """
    filter data rows by columns values criteria
    filters parameter should have structure like this: {"column_name": [value_list], "column_name": "value", etc...}
    """
    if not filters:
        return True

    for column, value in filters.items():
        column_position = _get_column_position(column, header)

        result = row[column_position] in value if type(value) == list else row[column_position] == value

        if not result:
            return False

    return True


def _get_column_position(column_name, source_header):
    return source_header.index(column_name)


def build_validators(csv_schema):
    validators = []

    for i in csv_schema:
        if i['validators'] and i['column'] and type(i['validators'] == list):
            for j in i['validators']:
                validators.append({'column': i['csv_header'], 'type': j})

    return validators


def read_csv(csv_data: str, trim=True, delimiter=settings.CSV_DELIMITER):
    if type(csv_data) == str:
        data = list(csv.reader(io.StringIO(csv_data), delimiter=delimiter))
    else:
        data = list(csv.reader(csv_data, delimiter=delimiter))

    if trim:
        for idx, row in enumerate(data):
            data[idx] = (list(map(lambda x: x.strip(), row)))

    return data


def process_csv(data, source_header, dest_header=None, validators=None, filters=None):
    if dest_header is None:
        dest_header = source_header
    csv_data = read_csv(csv_data=data)
    errors = validate_csv(data=csv_data, header=source_header, validators=validators)

    if filters:
        filtered = list(filter(lambda x: _filter(x, filters, source_header), csv_data[1:]))
        return _to_dict(filtered, source_header, dest_header)

    return {'data': _to_dict(csv_data[1:], source_header, dest_header, errors), 'errors': errors}


def _to_dict(csv_data, source_header, dest_header, errors, to_lower=True):
    position = _map_columns_position(source_header, dest_header)
    data = []

    for row_idx, row in enumerate(csv_data):
        data_row = {}
        for idx, col in enumerate(position):
            header_name = source_header[position[idx]].lower() if to_lower else source_header[position[idx]]
            data_row[header_name] = row[position[idx]]

        # + 2 cause data covers header (it's + 1) and errors index starts form 1 but the row no 1 is the header in errors list (another + 1).
        # So when row_idx = 0 => header, 1 => first row
        # A bit crazy but maybe is subject to todo: change
        data_row['__errors__'] = errors[row_idx + 2] if row_idx + 2 in errors else []
        data_row['__row__'] = row_idx + 2

        data.append(data_row)


def _escape_row(row, text_qualifier, trans):
    return list(map(lambda x: f'{text_qualifier}{x.translate(trans)}{text_qualifier}', row))


def write_csv(path, header: list, data: list, text_delimiter='', separator=';'):
    trans = str.maketrans({
        separator: ''
    })
    with open(path, 'wt') as f:
        if header:
            f.write(f'{separator.join(_escape_row(header, text_delimiter, trans))}\n')

        for row in data:
            f.write(f'{separator.join(_escape_row(row, text_delimiter, trans))}\n')

