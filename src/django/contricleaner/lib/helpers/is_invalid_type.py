def is_invalid_type(value):
    """Check if the value is not a string or list of strings."""
    if isinstance(value, str):
        return False
    elif isinstance(value, list):
        return any(is_invalid_type(v) for v in value)
    else:
        return True
