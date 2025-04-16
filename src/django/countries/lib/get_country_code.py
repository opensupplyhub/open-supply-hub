import re

from countries.lib.countries import COUNTRY_CODES, COUNTRY_NAMES


def get_country_code(country):
    # TODO: Handle minor spelling errors in country names
    remove_new_lines_pattern = re.compile(r'[\n\r]+')

    country = str(country).strip()
    country = remove_new_lines_pattern.sub(' ', country)

    if country.upper() in COUNTRY_NAMES:
        return country.upper()
    elif country.lower() in COUNTRY_CODES:
        return COUNTRY_CODES[country.lower()]
    else:
        raise ValueError(
            "Could not find a country code for '{0}'.".format(country))
