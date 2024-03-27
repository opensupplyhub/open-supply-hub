import re
from typing import Union, Set, List


def split_values(
        value: Union[str, list, set],
        split_pattern: str,
        excluded_values: List[str] = []
        ) -> Set[str]:
    '''
    Split a string, list, or set of strings into a set of strings.
    If a list or set is passed, the function will recursively split
    each value in the list or set.
    '''
    if isinstance(value, str):
        res = set()
        for excluded_value in excluded_values:
            if excluded_value in value:
                res.add(excluded_value)
                value = value.replace(excluded_value, '')

        return res.union(re.split(split_pattern, value))
    elif isinstance(value, (list, set)):
        res = set()
        for v in value:
            res = res.union(split_values(v, split_pattern, excluded_values))
        return res
