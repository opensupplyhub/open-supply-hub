from watchman.decorators import check


@check
def _check_gazetteercache():
    return {'ok': True}


def gazetteercache():
    return {'gazetteercache': _check_gazetteercache()}
