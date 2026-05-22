from pathlib import Path


MAX_FILE_SIZE = 5 * 1024 * 1024


class FileError(Exception):
    pass


def read_text_file(path: str) -> str:
    file_path = Path(path)
    if not file_path.exists():
        raise FileError(f'File not found: {path}')
    size = file_path.stat().st_size
    if size > MAX_FILE_SIZE:
        raise FileError(f'File is too large: {path}')
    try:
        return file_path.read_text(encoding='utf-8', errors='replace')
    except OSError as exc:
        raise FileError(f'Failed to read file: {path}') from exc


def expand_file_tokens(text: str) -> tuple[str, list[str]]:
    errors = []
    while True:
        start = text.find('@::')
        if start == -1:
            break
        end = text.find('::', start + 3)
        if end == -1:
            break

        path = text[start + 3 : end]
        try:
            new_string = '\n' + read_text_file(path)
        except FileError as exception:
            errors.append(str(exception))
            new_string = ''

        text = text[:start] + new_string + text[end + 2 :]

    return text, errors
