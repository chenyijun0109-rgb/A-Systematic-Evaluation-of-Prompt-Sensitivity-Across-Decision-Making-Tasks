from dataclasses import dataclass
import re
from typing import Iterable


@dataclass(frozen=True)
class ParseResult:
    parsed_action: str | None
    parse_success: bool
    invalid_reason: str | None
    normalized_response: str | None
    raw_response: str


def parse_response(
    raw_response: str | None,
    *,
    prefix: str,
    valid_actions: Iterable[str],
) -> ParseResult:
    """Parse a strict one-line LLM action response.

    Expected format examples:
    - CHOICE: A
    - ACTION: PUMP
    """
    raw = "" if raw_response is None else raw_response
    text = _strip_markdown_code_fence(raw.strip())
    expected_prefix = prefix.upper()
    valid = {action.upper() for action in valid_actions}

    if not text:
        return _invalid(raw, "empty_response")

    prefix_pattern = rf"\b{re.escape(expected_prefix)}\s*:"
    if len(re.findall(prefix_pattern, text, flags=re.IGNORECASE)) > 1:
        return _invalid(raw, "multiple_actions")

    match = re.fullmatch(
        rf"{re.escape(expected_prefix)}\s*:\s*([A-Za-z_]+)\s*",
        text,
        flags=re.IGNORECASE,
    )
    if not match:
        if not re.match(prefix_pattern, text, flags=re.IGNORECASE):
            return _invalid(raw, "missing_required_prefix")
        return _invalid(raw, "non_parseable_text")

    action = match.group(1).upper()
    normalized = f"{expected_prefix}: {action}"
    if action not in valid:
        return ParseResult(
            parsed_action=action,
            parse_success=False,
            invalid_reason="invalid_option",
            normalized_response=normalized,
            raw_response=raw,
        )

    return ParseResult(
        parsed_action=action,
        parse_success=True,
        invalid_reason=None,
        normalized_response=normalized,
        raw_response=raw,
    )


def _invalid(raw_response: str, reason: str) -> ParseResult:
    return ParseResult(
        parsed_action=None,
        parse_success=False,
        invalid_reason=reason,
        normalized_response=None,
        raw_response=raw_response,
    )


def _strip_markdown_code_fence(text: str) -> str:
    match = re.fullmatch(r"```(?:[A-Za-z0-9_-]+)?\s*\n(.*?)\n?```", text, flags=re.DOTALL)
    if not match:
        return text
    return match.group(1).strip()
