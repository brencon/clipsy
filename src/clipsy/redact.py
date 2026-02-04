"""Sensitive data detection and masking for clipboard entries."""

import re
from dataclasses import dataclass
from enum import Enum


class SensitiveType(Enum):
    """Types of sensitive data that can be detected."""

    API_KEY = "api_key"
    PASSWORD = "password"
    SSN = "ssn"
    CREDIT_CARD = "credit_card"
    PRIVATE_KEY = "private_key"
    CERTIFICATE = "certificate"
    TOKEN = "token"


@dataclass
class SensitiveMatch:
    """A detected sensitive data match."""

    sensitive_type: SensitiveType
    start: int
    end: int
    original: str
    masked: str


# Pattern definitions for sensitive data detection
PATTERNS: dict[SensitiveType, list[re.Pattern]] = {
    SensitiveType.API_KEY: [
        re.compile(r"sk-[a-zA-Z0-9]{20,}", re.ASCII),  # OpenAI
        re.compile(r"sk-proj-[a-zA-Z0-9_-]{20,}", re.ASCII),  # OpenAI project keys
        re.compile(r"AKIA[A-Z0-9]{16}", re.ASCII),  # AWS Access Key
        re.compile(r"ghp_[a-zA-Z0-9]{36}", re.ASCII),  # GitHub PAT
        re.compile(r"gho_[a-zA-Z0-9]{36}", re.ASCII),  # GitHub OAuth
        re.compile(r"github_pat_[a-zA-Z0-9_]{22,}", re.ASCII),  # GitHub fine-grained PAT
        re.compile(r"xox[baprs]-[a-zA-Z0-9-]{10,}", re.ASCII),  # Slack tokens
        re.compile(r"AIza[a-zA-Z0-9_-]{35}", re.ASCII),  # Google API Key
        re.compile(r"sq0[a-z]{3}-[a-zA-Z0-9_-]{22,}", re.ASCII),  # Square
        re.compile(r"sk_live_[a-zA-Z0-9]{24,}", re.ASCII),  # Stripe live
        re.compile(r"sk_test_[a-zA-Z0-9]{24,}", re.ASCII),  # Stripe test
        re.compile(r"rk_live_[a-zA-Z0-9]{24,}", re.ASCII),  # Stripe restricted
        re.compile(r"pk_live_[a-zA-Z0-9]{24,}", re.ASCII),  # Stripe publishable
        re.compile(r"pk_test_[a-zA-Z0-9]{24,}", re.ASCII),  # Stripe test publishable
    ],
    SensitiveType.PASSWORD: [
        re.compile(r"(?:password|passwd|pwd|pass|secret|token|api_key|apikey|auth)[=:\s]+['\"]?(\S{6,})['\"]?", re.IGNORECASE),
    ],
    SensitiveType.SSN: [
        re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # 123-45-6789
        re.compile(r"\b\d{9}\b"),  # 123456789 (only if looks like SSN context)
    ],
    SensitiveType.CREDIT_CARD: [
        re.compile(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b"),  # 16 digits
        re.compile(r"\b\d{4}[- ]?\d{6}[- ]?\d{5}\b"),  # Amex format
    ],
    SensitiveType.PRIVATE_KEY: [
        re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.ASCII),
        re.compile(r"-----BEGIN RSA PRIVATE KEY-----", re.ASCII),
        re.compile(r"-----BEGIN EC PRIVATE KEY-----", re.ASCII),
        re.compile(r"-----BEGIN OPENSSH PRIVATE KEY-----", re.ASCII),
    ],
    SensitiveType.CERTIFICATE: [
        re.compile(r"-----BEGIN CERTIFICATE-----", re.ASCII),
        re.compile(r"-----BEGIN X509 CERTIFICATE-----", re.ASCII),
    ],
    SensitiveType.TOKEN: [
        re.compile(r"eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}", re.ASCII),  # JWT
        re.compile(r"Bearer\s+[a-zA-Z0-9_-]{20,}", re.ASCII),  # Bearer token
    ],
}


def _mask_value(value: str, sensitive_type: SensitiveType) -> str:
    """Mask a sensitive value based on its type."""
    if sensitive_type == SensitiveType.SSN:
        # Show last 4 digits: •••-••-6789
        if "-" in value:
            return "•••-••-" + value[-4:]
        return "•••••" + value[-4:]

    if sensitive_type == SensitiveType.CREDIT_CARD:
        # Show last 4 digits: ••••-••••-••••-1234
        digits = re.sub(r"[- ]", "", value)
        return "••••-••••-••••-" + digits[-4:]

    if sensitive_type in (SensitiveType.PRIVATE_KEY, SensitiveType.CERTIFICATE):
        # Just indicate the type
        if "PRIVATE KEY" in value:
            return "[Private Key]"
        return "[Certificate]"

    if sensitive_type == SensitiveType.PASSWORD:
        return "••••••••"

    if sensitive_type == SensitiveType.TOKEN:
        if value.startswith("Bearer "):
            return "Bearer ••••••••"
        # JWT - show first part only
        if value.startswith("eyJ"):
            return value[:10] + "••••••••"
        return "••••••••"

    # API keys - show prefix and last few chars
    if len(value) > 12:
        prefix_len = min(8, len(value) // 4)
        suffix_len = 4
        return value[:prefix_len] + "••••••••" + value[-suffix_len:]

    return "••••••••"


def detect_sensitive(text: str) -> list[SensitiveMatch]:
    """Detect sensitive data in text.

    Args:
        text: The text to scan for sensitive data.

    Returns:
        List of SensitiveMatch objects for each detection.
    """
    matches: list[SensitiveMatch] = []

    for sensitive_type, patterns in PATTERNS.items():
        for pattern in patterns:
            for match in pattern.finditer(text):
                # For password patterns, we capture the password itself in group 1
                if sensitive_type == SensitiveType.PASSWORD and match.lastindex:
                    original = match.group(1)
                    start = match.start(1)
                    end = match.end(1)
                else:
                    original = match.group(0)
                    start = match.start()
                    end = match.end()

                masked = _mask_value(original, sensitive_type)
                matches.append(SensitiveMatch(
                    sensitive_type=sensitive_type,
                    start=start,
                    end=end,
                    original=original,
                    masked=masked,
                ))

    # Sort by start position and remove overlapping matches
    matches.sort(key=lambda m: m.start)
    non_overlapping: list[SensitiveMatch] = []
    last_end = -1
    for match in matches:
        if match.start >= last_end:
            non_overlapping.append(match)
            last_end = match.end

    return non_overlapping


def mask_text(text: str, matches: list[SensitiveMatch] | None = None) -> str:
    """Mask sensitive data in text.

    Args:
        text: The original text.
        matches: Pre-detected matches, or None to detect automatically.

    Returns:
        Text with sensitive data masked.
    """
    if matches is None:
        matches = detect_sensitive(text)

    if not matches:
        return text

    # Build masked text by replacing matched regions
    result = []
    last_pos = 0
    for match in matches:
        result.append(text[last_pos:match.start])
        result.append(match.masked)
        last_pos = match.end
    result.append(text[last_pos:])

    return "".join(result)


def is_sensitive(text: str) -> bool:
    """Check if text contains any sensitive data.

    Args:
        text: The text to check.

    Returns:
        True if sensitive data is detected.
    """
    return len(detect_sensitive(text)) > 0


def get_sensitivity_summary(matches: list[SensitiveMatch]) -> str:
    """Get a summary of detected sensitive types.

    Args:
        matches: List of sensitive matches.

    Returns:
        Human-readable summary like "API Key, Password".
    """
    types = sorted(set(m.sensitive_type.value.replace("_", " ").title() for m in matches))
    return ", ".join(types)
