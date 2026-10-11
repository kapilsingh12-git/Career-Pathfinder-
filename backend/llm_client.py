"""Thin, failure-tolerant wrapper around the Anthropic API.

Every caller must handle a `None` return (no key / API error / bad JSON) and
fall back to deterministic logic, so the platform never hard-depends on the LLM.
"""
import json
import logging
import re
from typing import Optional

from backend.config import ANTHROPIC_API_KEY, LLM_MODEL

log = logging.getLogger("llm")


class LLMClient:
    def __init__(self) -> None:
        self._client = None
        if ANTHROPIC_API_KEY:
            try:
                import anthropic
                self._client = anthropic.Anthropic(
                    api_key=ANTHROPIC_API_KEY, timeout=45, max_retries=2
                )
            except Exception as exc:  # missing package, bad config, ...
                log.warning("LLM disabled: %s", exc)

    @property
    def available(self) -> bool:
        return self._client is not None

    def complete_json(self, system: str, prompt: str, max_tokens: int = 1800) -> Optional[dict]:
        """Return a parsed JSON object, or None on any failure."""
        if not self._client:
            return None
        try:
            msg = self._client.messages.create(
                model=LLM_MODEL,
                max_tokens=max_tokens,
                system=system + "\nRespond with ONE valid JSON object and nothing else.",
                messages=[{"role": "user", "content": prompt}],
            )
            text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
            match = re.search(r"\{.*\}", text, re.S)   # tolerate stray prose/fences
            return json.loads(match.group(0)) if match else None
        except Exception as exc:
            log.warning("LLM call failed: %s", exc)
            return None


llm = LLMClient()
