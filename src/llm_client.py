from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any
from urllib import request
from urllib.error import HTTPError, URLError


RESPONSES_API_URL = "https://api.openai.com/v1/responses"


def load_dotenv(path: Path = Path(".env")) -> dict[str, str]:
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", maxsplit=1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def get_env_value(name: str, *, dotenv_values: dict[str, str] | None = None) -> str | None:
    dotenv_values = dotenv_values or load_dotenv()
    return os.environ.get(name) or dotenv_values.get(name)


class OpenAIResponsesClient:
    def __init__(
        self,
        api_key: str,
        *,
        api_url: str = RESPONSES_API_URL,
        max_retries: int = 2,
        retry_sleep_seconds: float = 2.0,
    ) -> None:
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required to call the OpenAI API.")
        self.api_key = api_key
        self.api_url = api_url
        self.max_retries = max_retries
        self.retry_sleep_seconds = retry_sleep_seconds

    def create_response(
        self,
        *,
        prompt: str,
        model: str,
        max_output_tokens: int,
        reasoning_effort: str | None = None,
        text_verbosity: str | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
    ) -> dict[str, Any]:
        body = {
            "model": model,
            "input": prompt,
            "max_output_tokens": max_output_tokens,
        }
        if reasoning_effort is not None:
            body["reasoning"] = {"effort": reasoning_effort}
        if text_verbosity is not None:
            body["text"] = {"verbosity": text_verbosity}
        if temperature is not None:
            body["temperature"] = temperature
        if top_p is not None:
            body["top_p"] = top_p
        data = json.dumps(body).encode("utf-8")
        http_request = request.Request(
            self.api_url,
            data=data,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        raw = self._send_with_retries(http_request)

        return {
            "raw_response": raw,
            "output_text": extract_output_text(raw),
        }

    def _send_with_retries(self, http_request: request.Request) -> dict[str, Any]:
        last_error: BaseException | None = None
        for attempt in range(self.max_retries + 1):
            try:
                with request.urlopen(http_request, timeout=120) as response:
                    return json.loads(response.read().decode("utf-8"))
            except HTTPError as error:
                detail = error.read().decode("utf-8", errors="replace")
                if not self._should_retry_http_error(error.code) or attempt >= self.max_retries:
                    raise RuntimeError(f"OpenAI API request failed: {error.code} {detail}") from error
                last_error = RuntimeError(f"OpenAI API request failed: {error.code} {detail}")
            except (TimeoutError, URLError) as error:
                if attempt >= self.max_retries:
                    raise RuntimeError(f"OpenAI API request failed: {error}") from error
                last_error = error

            time.sleep(self.retry_sleep_seconds)

        raise RuntimeError(f"OpenAI API request failed: {last_error}")

    @staticmethod
    def _should_retry_http_error(status_code: int) -> bool:
        return status_code == 429 or 500 <= status_code <= 599


def extract_output_text(response: dict[str, Any]) -> str:
    direct = response.get("output_text")
    if isinstance(direct, str):
        return direct

    chunks: list[str] = []
    for item in response.get("output", []):
        for content in item.get("content", []):
            text = content.get("text")
            if isinstance(text, str):
                chunks.append(text)
    return "\n".join(chunks).strip()
