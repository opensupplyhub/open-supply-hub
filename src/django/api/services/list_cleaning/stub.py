"""
Deterministic stand-in for the Cornell list-cleaning pipeline.

Produces output in the same shape as the aggregated OSDEV-3724 state machine
result ({file_pass, records, usage, prompt_version}) from a handful of simple
rules, so the contributor UI and the accept / reject / apply flow can be
exercised locally without Bedrock or AWS. It is not a substitute for the
prompt: it catches only the obvious cases and never does the judgment half.
"""
import re
import time
from collections import defaultdict

from countries.lib.countries import COUNTRY_NAMES
from countries.lib.get_country_code import get_country_code

ROW_OFFSET = 2  # spreadsheet row of the first data row

TEXT_FIELDS = (
    'name', 'address', 'sector_product_type',
    'facility_type_processing_type', 'number_of_workers', 'parent_company',
)
FILLER = {'n/a', 'na', '#n/a', 'none', 'null', '-', '--', 'tbd', 'unknown',
          'not available'}
PO_BOX_RE = re.compile(
    r'\b(?:p\.?\s*o\.?\s*box|post\s*office\s*box|postal\s*bag|gpo\s*box)\b',
    re.IGNORECASE)
EMAIL_RE = re.compile(r'[\w.+-]+@[\w-]+\.[\w.-]+')
PHONE_RE = re.compile(r'\+?\d(?:[\s().-]*\d){7,}')
PERSON_TITLE_RE = re.compile(
    r'^(mr|mrs|ms|miss|dr|mohammed|mohammad|md)\.?\s', re.IGNORECASE)
WORKERS_JUNK_RE = re.compile(r'[,\s]|approx\.?|about|~', re.IGNORECASE)


def _s(value):
    return '' if value is None else str(value)


def _norm(value):
    return re.sub(r'\s+', ' ', _s(value)).strip()


def _key(value):
    return re.sub(r'[^a-z0-9]+', '', _norm(value).lower())


def _is_filler(value):
    return _norm(value).lower() in FILLER


def _country_name_for(code):
    return COUNTRY_NAMES.get(code, '')


class _RowCheck:
    """One row's findings: changes keyed by field, issues in order."""

    def __init__(self, row):
        self.row = row
        self.changes = []
        self.issues = []
        self.values = {field: _s(row.get(field)) for field in TEXT_FIELDS}
        self.values['country'] = _s(row.get('country'))

    def change(self, field, value, reason):
        # Several rules may touch one field: keep one entry, join reasons.
        for existing in self.changes:
            if existing['field'] == field:
                existing['value'] = value
                existing['reason'] = f"{existing['reason']}+{reason}"
                return
        self.changes.append({'field': field, 'value': value,
                             'reason': reason})

    def issue(self, code, severity, field, note):
        self.issues.append({'code': code, 'severity': severity,
                            'field': field, 'note': note})

    @property
    def blank(self):
        return all(not v for v in self.values.values())

    @property
    def status(self):
        if any(i['severity'] == 'must_fix' for i in self.issues):
            return 'needs_your_action'
        if self.changes:
            return 'auto_corrected'
        return 'unchanged'


def _file_pass(rows):
    """Stage 1: header, exact duplicates and repeated names over the raw
    strings, as the prompt's file pass does."""
    header = set()
    for row in rows:
        header.update(k for k in row.keys() if k != 'row')
    file_pass = {
        'mode': 'file_pass',
        'row_count': len(rows),
        'header_issues': [
            {'column': column, 'note': f'The required column "{column}" is '
                                       'missing from the file header.'}
            for column in ('name', 'address', 'country')
            if column not in header
        ],
        'exact_duplicates': [],
        'repeated_names': [],
    }
    by_name_address = {}
    by_name = defaultdict(list)
    removed_as_duplicate = {}
    for row in rows:
        n = row.get('row')
        name_key = _key(row.get('name'))
        if not name_key:
            continue
        pair_key = (name_key, _key(row.get('address')),
                    _key(row.get('country')))
        if pair_key in by_name_address:
            keep = by_name_address[pair_key]
            file_pass['exact_duplicates'].append(
                {'keep': keep, 'remove': n, 'match': 'exact'})
            removed_as_duplicate[n] = keep
        else:
            by_name_address[pair_key] = n
            by_name[name_key].append((n, _norm(row.get('name'))))
    for name_key, entries in by_name.items():
        if len(entries) > 1:
            file_pass['repeated_names'].append({
                'name': entries[0][1],
                'rows': [n for n, _ in entries],
            })
    return file_pass, removed_as_duplicate


def _tidy_text(check):
    """Whitespace and filler text on every text column."""
    for field, original in list(check.values.items()):
        normalized = _norm(original)
        if normalized != original and normalized:
            check.change(field, normalized, 'whitespace')
            check.values[field] = normalized
        if _is_filler(normalized) and normalized:
            check.change(field, '', 'filler_text')
            check.values[field] = ''


def _check_country(check):
    country = check.values['country']
    if not country:
        check.issue('missing_country', 'must_fix', 'country',
                    'The country cell is blank. Please add the country the '
                    'facility is in.')
        return
    is_code = (len(country) == 2 and country.upper() in COUNTRY_NAMES
               and country == country.upper())
    if is_code:
        return
    try:
        code = get_country_code(country)
    except ValueError:
        check.issue('unknown_country', 'must_fix', 'country',
                    f'We could not recognise "{country}" as a country. '
                    'Please use the country name or its two-letter code.')
        return
    check.change('country', code, 'country_code')
    check.values['country'] = code


def _check_name(check):
    name = check.values['name']
    if not name:
        check.issue('missing_name', 'must_fix', 'name',
                    'The name cell is blank. Please add the facility name.')
        return
    if len(name) > 200:
        check.issue('too_long', 'must_fix', 'name',
                    'The name is over 200 characters. Please shorten it.')
    if len(name) < 4:
        check.issue('name_incomplete', 'internal_note', 'name',
                    f'The name "{name}" is under four characters and may '
                    'not identify the facility.')
    if name.isupper() and len(name) > 3:
        check.change('name', name.title(), 'casing')
    if EMAIL_RE.search(name) or PERSON_TITLE_RE.match(name):
        check.issue('pii', 'must_fix', 'name',
                    'The name looks like a person or a personal contact '
                    'rather than a business. Please give the business '
                    'name.')


def _trim_country_tail(check, address):
    country_name = _country_name_for(check.values['country'])
    for tail in (country_name, check.values['country']):
        if tail and len(tail) > 1 and address.lower().endswith(tail.lower()):
            trimmed = address[:-len(tail)].rstrip(' ,;.-')
            if trimmed:
                check.change('address', trimmed, 'country_in_address')
            return


def _check_address(check):
    address = check.values['address']
    if not address:
        check.issue('missing_address', 'must_fix', 'address',
                    'The address cell is blank. Please add the street '
                    'address of the facility.')
        return
    if len(address) > 200:
        check.issue('too_long', 'must_fix', 'address',
                    'The address is over 200 characters. Please shorten '
                    'it.')
    if PO_BOX_RE.search(address) and address.count(',') < 2:
        check.issue('address_po_box', 'must_fix', 'address',
                    f'The address "{address}" has no street. Please give '
                    'the street address of the facility.')
    if EMAIL_RE.search(address) or PHONE_RE.search(address):
        check.issue('pii', 'must_fix', 'address',
                    'The address contains an email or phone number. '
                    'Please remove personal contact details.')
    _trim_country_tail(check, address)
    if len([p for p in address.split(',') if p.strip()]) < 2:
        check.issue('address_too_few', 'internal_note', 'address',
                    'The address has fewer than two parts (street, town, '
                    'region or postcode).')


def _check_workers(check):
    workers = check.values['number_of_workers']
    if not workers:
        return
    cleaned = WORKERS_JUNK_RE.sub('', workers)
    cleaned = re.sub(r'^(\d+)\+$', r'\1', cleaned)
    if cleaned != workers and re.fullmatch(r'\d+(-\d+)?', cleaned):
        check.change('number_of_workers', cleaned, 'workers_format')


def _check_parent_company(check):
    if EMAIL_RE.search(check.values['parent_company']):
        check.issue('pii', 'must_fix', 'parent_company',
                    'The parent company cell contains an email address. '
                    'Please give the company name only.')


def _check_repeated_name(check, repeated_rows):
    n = check.row.get('row')
    if n not in repeated_rows:
        return
    others = [r for r in repeated_rows[n]['rows'] if r != n]
    check.issue('repeated_names', 'advisory', 'name',
                'The same name appears on rows '
                f'{", ".join(str(r) for r in others)} with a different '
                'address.')


def _check_row(row, repeated_rows, removed_as_duplicate):
    """Stage 2: one row, rule by rule, to a pipeline record."""
    n = row.get('row')
    check = _RowCheck(row)
    _tidy_text(check)
    if check.blank:
        return {
            'row': n, 'status': 'removed', 'changes': check.changes,
            'issues': [{'code': 'empty_row', 'severity': 'must_fix',
                        'field': 'row',
                        'note': 'Every cell in this row is blank, so '
                                'the row is removed.'}],
            'removed_reason': 'empty',
        }
    _check_country(check)
    _check_name(check)
    _check_address(check)
    _check_workers(check)
    _check_parent_company(check)
    _check_repeated_name(check, repeated_rows)
    if n in removed_as_duplicate:
        return {
            'row': n, 'status': 'removed', 'changes': check.changes,
            'issues': check.issues, 'removed_reason': 'duplicate',
            'duplicate_of': removed_as_duplicate[n],
        }
    return {'row': n, 'status': check.status, 'changes': check.changes,
            'issues': check.issues}


def run_rules(payload):
    started = time.time()
    rows = payload.get('rows') or []
    file_pass, removed_as_duplicate = _file_pass(rows)
    repeated_rows = {
        n: group for group in file_pass['repeated_names']
        for n in group['rows']
    }
    records = [_check_row(row, repeated_rows, removed_as_duplicate)
               for row in rows]
    return {
        'file_pass': file_pass,
        'records': records,
        'usage': {'input_tokens': 0, 'output_tokens': 0,
                  'seconds': round(time.time() - started, 3)},
        'prompt_version': 'stub',
    }
