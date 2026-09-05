"""Small text cleaning / CSV sanitization helpers."""
import re

_WHITESPACE_RE = re.compile(r"\s+")
_CSV_INJECTION_PREFIXES = ("=", "+", "-", "@")


def clean_text(text: str | None) -> str:
    """Collapse whitespace and strip a piece of text."""
    if not text:
        return ""
    return _WHITESPACE_RE.sub(" ", text).strip()


def sanitize_csv_field(value: str | None) -> str:
    """Prefix values that could be interpreted as spreadsheet formulas."""
    if value is None:
        return ""
    text = str(value)
    if text.startswith(_CSV_INJECTION_PREFIXES):
        return f"'{text}"
    return text
