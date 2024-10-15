from watchman.decorators import check


@check
def _check_django():
    return {'ok': True}


def django():
    return {'django': _check_django()}
