"""The single doorway every agent uses to talk to Claude.

`ClaudeLLM` calls the Anthropic API. `FakeLLM` returns canned, schema-valid answers so the
whole company can be tested end to end with no API key and no cost (`--dry-run`).
"""
from __future__ import annotations

from typing import Protocol, TypeVar

from pydantic import BaseModel

from . import config

T = TypeVar("T", bound=BaseModel)

# Server-side fallback: if the model declines a request, the API retries it on a
# recommended fallback model inside the same call.
FALLBACK_BETA = "server-side-fallback-2026-07-01"


class AgentError(RuntimeError):
    pass


class LLM(Protocol):
    def structured(self, *, system: str, prompt: str, schema: type[T], effort: str = "medium") -> T: ...
    def research(self, *, system: str, prompt: str, max_searches: int = 5) -> str: ...


class ClaudeLLM:
    def __init__(self, model: str = config.MODEL):
        import anthropic  # imported lazily so dry runs don't need the package configured

        self.client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
        self.model = model
        self.input_tokens = 0
        self.output_tokens = 0

    def _track(self, response) -> None:
        self.input_tokens += response.usage.input_tokens or 0
        self.output_tokens += response.usage.output_tokens or 0

    def structured(self, *, system: str, prompt: str, schema: type[T], effort: str = "medium") -> T:
        response = self.client.beta.messages.parse(
            model=self.model,
            max_tokens=16000,
            system=system,
            messages=[{"role": "user", "content": prompt}],
            output_format=schema,
            output_config={"effort": effort},
            betas=[FALLBACK_BETA],
            fallbacks="default",
        )
        self._track(response)
        if response.stop_reason == "refusal":
            raise AgentError("Model declined the request")
        if response.parsed_output is None:
            raise AgentError(f"No structured output (stop_reason={response.stop_reason})")
        return response.parsed_output

    def research(self, *, system: str, prompt: str, max_searches: int = 5) -> str:
        """Free-form research with Anthropic's server-side web search tool. Returns the final text."""
        messages: list = [{"role": "user", "content": prompt}]
        tools = [{"type": "web_search_20260209", "name": "web_search", "max_uses": max_searches}]
        for _ in range(6):
            response = self.client.beta.messages.create(
                model=self.model,
                max_tokens=16000,
                system=system,
                messages=messages,
                tools=tools,
                output_config={"effort": "medium"},
                betas=[FALLBACK_BETA],
                fallbacks="default",
            )
            self._track(response)
            if response.stop_reason == "refusal":
                raise AgentError("Model declined the research request")
            if response.stop_reason == "pause_turn":
                # Long server-tool turn: send the partial turn back so Claude continues.
                messages.append({"role": "assistant", "content": response.content})
                continue
            return "\n".join(b.text for b in response.content if b.type == "text")
        raise AgentError("Research did not finish")


class FakeLLM:
    """Offline stand-in used by --dry-run and the tests."""

    input_tokens = 0
    output_tokens = 0

    def __init__(self) -> None:
        self.calls: list[str] = []

    def structured(self, *, system: str, prompt: str, schema: type[T], effort: str = "medium") -> T:
        self.calls.append(schema.__name__)
        return schema.example()

    def research(self, *, system: str, prompt: str, max_searches: int = 5) -> str:
        self.calls.append("research")
        return "Dry run: no web research performed."
