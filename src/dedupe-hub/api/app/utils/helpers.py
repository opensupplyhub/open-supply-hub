from typing import Dict, List

def transform_to_dict(items):
    dict_data: List[Dict[str, str]] = []
    for item in items:
        dict_item = {
            'id': '{}'.format(item.id),
            'country': item.country_code,
            'name': item.name,
            'address': item.address
        }
        dict_data.append(dict_item)
    return dict_data