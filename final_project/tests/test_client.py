from unittest.mock import MagicMock

from gigavibe.settings import Config
from gigavibe.client import Llm


def _make_config() -> Config:
    return Config(
        api_key='test',
        api_host='http://localhost:11434/v1/',
        model='gemma3:270m',
        limit_messages=10,
        limit_chars=None,
        temperature=0.2,
        system_prompt=None,
        streaming=False,
    )


def test_complete_returns_content() -> None:
    config = _make_config()
    client = Llm(config)

    mock_response = MagicMock()
    mock_response.choices[0].message.content = 'ответ'
    client._client.chat.completions.create = MagicMock(return_value=mock_response)

    result = client.complete([{'role': 'user', 'content': 'привет'}])
    assert result == 'ответ'


def test_complete_returns_empty_on_none_content() -> None:
    config = _make_config()
    client = Llm(config)

    mock_response = MagicMock()
    mock_response.choices[0].message.content = None
    client._client.chat.completions.create = MagicMock(return_value=mock_response)

    result = client.complete([{'role': 'user', 'content': 'привет'}])
    assert result == ''


def test_stream_complete_collects_tokens() -> None:
    config = _make_config()
    client = Llm(config)

    def make_chunk(text: str) -> MagicMock:
        chunk = MagicMock()
        chunk.choices[0].delta.content = text
        return chunk

    chunks = [make_chunk('при'), make_chunk('вет')]
    client._client.chat.completions.create = MagicMock(return_value=iter(chunks))

    tokens: list[str] = []
    result = client.stream_complete(
        [{'role': 'user', 'content': 'hi'}],
        on_token=tokens.append,
    )
    assert result == 'привет'
    assert tokens == ['при', 'вет']
