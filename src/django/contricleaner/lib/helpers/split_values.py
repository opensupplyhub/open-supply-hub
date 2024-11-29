import re
from typing import Union, List


def split_values(value: Union[str, list, set],
                 split_pattern: str) -> List[str]:
    '''
    Split a string, list, or set of strings into a set of strings.
    If a list or set is passed, the function will recursively split
    each value in the list or set.
    As a result, the function returns a list to ensure compatibility
    with the database for saving, particularly when working with
    moderation events.
    '''
    if isinstance(value, str):
        return list(set(re.split(split_pattern, value)))
    elif isinstance(value, (list, set)):
        res = set()
        for v in value:
            res = res.union(split_values(v, split_pattern))
        return list(res)
