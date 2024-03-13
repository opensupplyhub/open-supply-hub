def is_valid_type(value):
    """Check if the value is a string or list of strings."""
    if isinstance(value, str):
        return True
    elif isinstance(value, list):
        return all(is_valid_type(v) for v in value)
    else:
        return False
