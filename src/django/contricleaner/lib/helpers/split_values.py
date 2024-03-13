from typing import Union, Set


def split_values(value: Union[str, list, set], split: str) -> Set[str]:
    '''
    Split a string, list, or set of strings into a set of strings.
    If a list or set is passed, the function will recursively split
    each value in the list or set.
    '''
    if isinstance(value, str):
        return set(value.split(split))
    elif isinstance(value, (list, set)):
        res = set()
        for v in value:
            res = res.union(split_values(v, split))
        return res
