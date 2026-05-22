from pathlib import Path
import os
from typing import Any

import yaml


class ConfigError(Exception):
    pass


class Config:
    def __init__(
        self,
        api_key: str,
        api_host: str,
        model: str,
        limit_messages: int | None,
        limit_chars: int | None,
        temperature: float,
        system_prompt: str | None,
        streaming: bool,
    ) -> None:
        self.api_key = api_key
        self.api_host = api_host
        self.model = model
        self.limit_messages = limit_messages
        self.limit_chars = limit_chars
        self.temperature = temperature
        self.system_prompt = system_prompt
        self.streaming = streaming


def _parse_int(value: str, name: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exception:
        raise ConfigError(f'Invalid {name}: {value}') from exception
    if parsed < 1:
        raise ConfigError(f'Invalid {name}: {value}')
    return parsed


def _parse_float(value: str, name: str) -> float:
    try:
        parsed = float(value)
    except ValueError as exception:
        raise ConfigError(f'Invalid {name}: {value}') from exception
    return parsed


def _parse_bool(value: str, name: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {'1', 'true', 'yes', 'y', 'on'}:
        return True
    if normalized in {'0', 'false', 'no', 'n', 'off'}:
        return False
    raise ConfigError(f'Invalid {name}: {value}')


def _read_yaml(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        data = yaml.safe_load(path.read_text(encoding='utf-8'))
    except OSError as exception:
        raise ConfigError(f'Failed to read {path}') from exception
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ConfigError('config.yaml must be a mapping')
    return data


def _get_value(
    env_name: str,
    yaml_data: dict[str, Any] | None,
    yaml_name: str | None = None,
) -> str | None:
    if env_name in os.environ:
        return os.environ[env_name]
    if yaml_data is None:
        return None
    value = yaml_data.get(yaml_name or env_name.lower())
    if value is None:
        return None
    return str(value)


def load_config(config_path: Path | None = None) -> Config:
    path = config_path or Path('config.yaml')
    yaml_data = _read_yaml(path)
    has_env = any(i in os.environ for i in ['API_KEY', 'API_HOST', 'MODEL'])
    if yaml_data is None and not has_env:
        raise ConfigError('No configuration found: set env vars or create config.yaml')

    api_key = _get_value('API_KEY', yaml_data, 'api_key')
    api_host = _get_value('API_HOST', yaml_data, 'api_host')
    model = _get_value('MODEL', yaml_data, 'model')

    if not api_key:
        raise ConfigError('Missing API_KEY')
    if not api_host:
        raise ConfigError('Missing API_HOST')
    if not model:
        raise ConfigError('Missing MODEL')

    limit_messages_raw = _get_value('LIMIT_MESSAGE', yaml_data, 'limit_message')
    if limit_messages_raw is None:
        limit_messages_raw = _get_value('LIMIT_MESSAGES', yaml_data, 'limit_messages')
    limit_chars_raw = _get_value('LIMIT_CHARS', yaml_data, 'limit_chars')
    temperature_raw = _get_value('TEMPERATURE', yaml_data, 'temperature')
    streaming_raw = _get_value('STREAMING', yaml_data, 'streaming')

    limit_messages = _parse_int(limit_messages_raw, 'LIMIT_MESSAGE') if limit_messages_raw else None
    limit_chars = _parse_int(limit_chars_raw, 'LIMIT_CHARS') if limit_chars_raw else None
    temperature = _parse_float(temperature_raw, 'TEMPERATURE') if temperature_raw else 0.2

    if temperature < 0 or temperature > 1:
        raise ConfigError('TEMPERATURE must be between 0 and 1')

    system_prompt = None
    if yaml_data is not None:
        prompt_value = yaml_data.get('system_prompt')
        if prompt_value is not None:
            system_prompt = str(prompt_value)

    streaming = _parse_bool(streaming_raw, 'STREAMING') if streaming_raw else False

    return Config(
        api_key=api_key,
        api_host=api_host,
        model=model,
        limit_messages=limit_messages,
        limit_chars=limit_chars,
        temperature=temperature,
        system_prompt=system_prompt,
        streaming=streaming,
    )
