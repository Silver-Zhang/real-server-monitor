"""Utility for sanitizing sensitive information in command lines."""

from __future__ import annotations

import re

# Patterns that indicate sensitive values
SENSITIVE_PATTERNS = [
    "password",
    "passwd",
    "token",
    "api_key",
    "api-key",
    "secret",
    "credential",
    "key",
]

# Build regex: match --<sensitive_word>[=| ]<value>
_SENSITIVE_RE = re.compile(
    r"(--(?:"
    + "|".join(re.escape(p) for p in SENSITIVE_PATTERNS)
    + r")[\s=])(\S+)",
    re.IGNORECASE,
)

# Also match -<short> forms like -p <value> for password etc.
# and environment-style KEY=value
_ENV_SENSITIVE_RE = re.compile(
    r"(\b(?:"
    + "|".join(re.escape(p) for p in SENSITIVE_PATTERNS)
    + r")=)(\S+)",
    re.IGNORECASE,
)


def sanitize_command(cmd: str) -> str:
    """Sanitize sensitive arguments in a command string.

    Replaces values of known sensitive flags with '***'.
    """
    result = _SENSITIVE_RE.sub(r"\1***", cmd)
    result = _ENV_SENSITIVE_RE.sub(r"\1***", result)
    return result
