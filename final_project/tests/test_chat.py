from gigavibe.chat import build_messages, parse_command, print_help, print_welcome


def test_build_messages_with_system_prompt() -> None:
    history = [{'role': 'user', 'content': 'привет'}]
    result = build_messages(history, 'ты помощник')
    assert result[0] == {'role': 'system', 'content': 'ты помощник'}
    assert result[1:] == history


def test_build_messages_empty_history() -> None:
    result = build_messages([], 'промпт')
    assert len(result) == 1
    assert result[0]['role'] == 'system'


def test_parse_command_defaults() -> None:
    paragraphs, length, auto = parse_command('/filechunk')
    assert paragraphs == 1
    assert length is None
    assert auto is False


def test_build_messages_no_system_prompt() -> None:
    history = [{'role': 'user', 'content': 'привет'}]
    result = build_messages(history, None)
    assert result == history


def test_parse_command_paragraph() -> None:
    paragraphs, length, auto = parse_command('/filechunk paragraph=3')
    assert paragraphs == 3
    assert length is None


def test_parse_command_len() -> None:
    paragraphs, length, auto = parse_command('/filechunk len=200')
    assert paragraphs is None
    assert length == 200


def test_parse_command_auto() -> None:
    _, _, auto = parse_command('/filechunk -y')
    assert auto is True


def test_parse_command_all_flags() -> None:
    paragraphs, _, auto = parse_command('/filechunk paragraph=2 -y')
    assert paragraphs == 2
    assert auto is True


def test_print_welcome_output(capsys: object) -> None:
    from gigavibe.settings import Config

    config = Config(
        api_key='k',
        api_host='h',
        model='m',
        limit_messages=10,
        limit_chars=None,
        temperature=0.5,
        system_prompt=None,
        streaming=False,
    )
    print_welcome(config)
    captured = capsys.readouterr()
    assert 'GigaVibe' in captured.out
    assert 'm' in captured.out


def test_print_help_output(capsys: object) -> None:
    print_help()
    captured = capsys.readouterr()
    assert '/help' in captured.out
    assert '/reset' in captured.out
    assert '/filechunk' in captured.out
