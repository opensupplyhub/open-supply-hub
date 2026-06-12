from api.models.partner_field import PartnerField


def _validate_integer(value: object) -> int:
    if isinstance(value, bool):
        raise ValueError("Expected an integer, not a boolean.")
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    try:
        return int(str(value).strip())
    except (TypeError, ValueError) as error:
        raise ValueError(
            f"Expected an integer, not '{value}'."
        ) from error


def _validate_number(value: object) -> float:
    if isinstance(value, bool):
        raise ValueError("Expected a number, not a boolean.")
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).strip())
    except (TypeError, ValueError) as error:
        raise ValueError(
            f"Expected a number, not '{value}'."
        ) from error


def _validate_boolean(value: object) -> bool:
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in ("true", "1", "yes"):
        return True
    if normalized in ("false", "0", "no"):
        return False
    raise ValueError(f"Expected a boolean, not '{value}'.")


CELL_PARSERS = {
    PartnerField.STRING: lambda value: str(value).strip(),
    PartnerField.INT: _validate_integer,
    PartnerField.FLOAT: _validate_number,
}

LEAF_TYPE_VALIDATORS = {
    "integer": _validate_integer,
    "number": _validate_number,
    "boolean": _validate_boolean,
}
