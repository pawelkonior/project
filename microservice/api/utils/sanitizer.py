from nh3 import clean as nh3_clean


def sanitize_string(value: str | None) -> str | None:
    """Sanitize a string using NH3 to prevent XSS attacks."""
    if value is None:
        return None
    return nh3_clean(value)
