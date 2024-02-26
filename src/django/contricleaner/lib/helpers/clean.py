import re
from unidecode import unidecode


def clean(column):
    """
    Remove punctuation and excess whitespace from a value before using it to
    find matches. This should be the same function used when developing the
    training data read from training.json as part of train_gazetteer.
    """
    column = unidecode(column)
    column = re.sub("\n", " ", column)
    column = re.sub("-", "", column)
    column = re.sub("/", " ", column)
    column = re.sub("'", "", column)
    column = re.sub(",", "", column)
    column = re.sub(":", " ", column)
    column = re.sub(" +", " ", column)
    column = column.strip().strip('"').strip("'").lower().strip()
    if not column:
        column = None
    return column
