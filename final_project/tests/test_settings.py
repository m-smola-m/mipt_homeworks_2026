from pathlib import Path

import pytest

from gigavibe.settings import ConfigError, load_config


def write_yaml(path: Path, content: str) -> None:
    path.write_text(content, encoding='utf-8')


def test_config_loads_from_yaml(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    write_yaml(
        tmp_path / 'config.yaml',
        'api_key: supersecret\napi_host: http://localhost:11434/v1/\nmodel: gemma3:270m\n'
        'limit_message: 5\ntemperature: 0.7\n',
    )
    config = load_config()
    assert config.api_key == 'supersecret'
    assert config.model == 'gemma3:270m'
    assert config.limit_messages == 5
    assert config.temperature == 0.7


def test_env_overrides_yaml(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    write_yaml(
        tmp_path / 'config.yaml',
        'api_key: yaml-key\napi_host: http://yaml-host\nmodel: yaml-model\n',
    )
    monkeypatch.setenv('API_KEY', 'env-key')
    monkeypatch.setenv('MODEL', 'qwen3:0.6b')
    config = load_config()
    assert config.api_key == 'env-key'
    assert config.model == 'qwen3:0.6b'
    assert config.api_host == 'http://yaml-host'


def test_no_config_raises_error(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ConfigError, match='No configuration found'):
        load_config()


def test_bad_temperature_raises_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    write_yaml(
        tmp_path / 'config.yaml',
        'api_key: key\napi_host: http://host\nmodel: m\ntemperature: 1.5\n',
    )
    with pytest.raises(ConfigError, match='TEMPERATURE'):
        load_config()


def test_system_prompt_from_yaml(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    write_yaml(
        tmp_path / 'config.yaml',
        'api_key: k\napi_host: http://h\nmodel: m\n'
        'system_prompt: Ты полезный ассистент по Python.\n',
    )
    config = load_config()
    assert config.system_prompt == 'Ты полезный ассистент по Python.'
