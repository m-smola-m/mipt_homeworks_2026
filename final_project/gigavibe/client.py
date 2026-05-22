from typing import Callable

from openai import OpenAI

from .settings import Config


class Llm:
    def __init__(self, config: Config) -> None:
        self._client = OpenAI(api_key=config.api_key, base_url=config.api_host)
        self._model = config.model
        self._temperature = config.temperature

    def complete(self, messages: list[dict[str, str]]) -> str:
        answer = self._client.chat.completions.create(
            model=self._model,
            messages=messages,  # type: ignore[arg-type]
            temperature=self._temperature,
        )
        content = answer.choices[0].message.content
        return content or ''

    def stream_complete(
        self,
        messages: list[dict[str, str]],
        on_token: Callable[[str], None],
    ) -> str:
        stream = self._client.chat.completions.create(
            model=self._model,
            messages=messages,  # type: ignore[arg-type]
            temperature=self._temperature,
            stream=True,
        )
        parts = []
        for i in stream:
            token = i.choices[0].delta.content or ''  # type: ignore[union-attr]
            if token:
                on_token(token)
                parts.append(token)
        return ''.join(parts)