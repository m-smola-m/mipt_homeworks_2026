from pathlib import Path

from gigavibe import reader
from gigavibe.reader import FileError, expand_file_tokens, read_text_file


def test_file_content_injected_into_message(tmp_path: Path) -> None:
    code = tmp_path / 'main.py'
    code.write_text('print("Hello world!")\n', encoding='utf-8')
    text = f'В чём ошибка? @::{code}::'
    expanded, errors = expand_file_tokens(text)
    assert errors == []
    assert 'print("Hello world!")' in expanded


def test_unexisted_file() -> None:
    expanded, errors = expand_file_tokens('Смотри @::/нет/такого/файла.py::')
    assert expanded == 'Смотри '
    assert len(errors) == 1
    assert 'File not found' in errors[0]


def test_file_too_big(tmp_path: Path) -> None:
    original = reader.MAX_FILE_SIZE
    reader.MAX_FILE_SIZE = 5
    try:
        fat_file = tmp_path / 'роман.txt'
        fat_file.write_bytes(b'123456')
        expanded, errors = expand_file_tokens(f'читай @::{fat_file}::')
        assert expanded == 'читай '
        assert errors
    finally:
        reader.MAX_FILE_SIZE = original


def test_multiple_files(tmp_path: Path) -> None:
    f1 = tmp_path / 'models.py'
    f2 = tmp_path / 'views.py'
    f1.write_text('class User:\n    pass\n', encoding='utf-8')
    f2.write_text('def index():\n    return "ok"\n', encoding='utf-8')
    text = f'Посмотри на оба файла @::{f1}:: и @::{f2}::'
    expanded, errors = expand_file_tokens(text)
    assert errors == []
    assert 'class User' in expanded
    assert 'def index' in expanded


def test_read_text_file() -> None:
    try:
        read_text_file('/No_such_dir.txt')
    except FileError as exception:
        assert 'File not found' in str(exception)
    else:
        raise AssertionError('Ожидали FileError')
