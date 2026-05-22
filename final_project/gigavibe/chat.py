import os

from .splitter import iter_chunks
from .settings import Config, ConfigError, load_config
from .reader import FileError, expand_file_tokens, read_text_file
from .context import apply_limits
from .client import Llm, _sanitize


Message = dict[str, str]


def build_messages(history: list[Message], system_prompt: str | None) -> list[Message]:
    messages = []
    if system_prompt:
        messages.append({'role': 'system', 'content': system_prompt})
    messages.extend(history)
    return messages


def clear_screen() -> None:
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


def parse_command(text: str) -> tuple[int | None, int | None, bool]:
    tokens = text.strip().split()
    paragraphs_per_chunk: int | None = None
    chunk_len: int | None = None
    auto = False
    for i in tokens[1:]:
        if i == '-y':
            auto = True
            continue
        if i.startswith('paragraph='):
            value = i.split('=', 1)[1]
            paragraphs_per_chunk = int(value)
            continue
        if i.startswith('len='):
            value = i.split('=', 1)[1]
            chunk_len = int(value)
            continue
    if paragraphs_per_chunk is None and chunk_len is None:
        paragraphs_per_chunk = 1
    return paragraphs_per_chunk, chunk_len, auto


def request(
    client: Llm,
    config: Config,
    messages: list[Message],
) -> str | None:
    try:
        if config.streaming:
            text = client.stream_complete(
                messages,
                on_token=lambda token: print(token, end='', flush=True),
            )
            print()
            return text
        return client.complete(messages)
    except KeyboardInterrupt:
        print('\nЗапрос прерван.')
        return None
    except Exception as e:
        print(f'Ошибка запроса: {e}')
        return None


def run_file_with_chunks(client: Llm, config: Config, command_text: str) -> None:
    try:
        paragraphs_per_chunk, chunk_len, auto = parse_command(command_text)
    except ValueError:
        print('Ошибка: неверные параметры /filechunk')
        return
    if paragraphs_per_chunk is not None and chunk_len is not None:
        print('Ошибка: используйте paragraph= или len=, не оба сразу')
        return

    path = input('Введите путь до файла\n').strip()
    if path == '\\q':
        return
    try:
        text = read_text_file(path)
    except FileError as exc:
        print(f'Ошибка: {exc}')
        return

    prompt = input('Что нужно сделать для каждой части?\n').strip()
    if prompt == '\\q':
        return

    chunks = list(iter_chunks(text, paragraphs_per_chunk, chunk_len))
    if not chunks:
        print('Нет частей для обработки')
        return

    print('Начинаю обработку:')
    for i in chunks:
        messages = build_messages([], config.system_prompt)
        user_content = f'{prompt}\n\n{i}' if prompt else i
        messages.append({'role': 'user', 'content': user_content})
        result = request(client, config, messages)
        if result is None:
            continue
        if not config.streaming:
            print(result)
        if auto:
            continue
        while True:
            step = input().strip()
            if step == '\\q':
                return
            if step == '':
                break

    print('Обработка файла завершена.')


def print_welcome(config: Config) -> None:
    print('=== GigaVibe Chat ===')
    print(f'Модель: {config.model}')
    print(f'Температура: {config.temperature}')
    print(f'Стриминг: {"вкл" if config.streaming else "выкл"}')
    print()
    print('Команды:')
    print('  /help          — справка')
    print('  /reset         — очистить историю и экран')
    print('  /filechunk     — обработать файл по частям')
    print('  \\q             — выход')
    print()


def print_help() -> None:
    print()
    print('Команды:')
    print('  /help                      — справка')
    print('  /reset                     — очистить историю и экран')
    print('  /filechunk [paragraph=N] [len=N] [-y]  — обработать файл по частям')
    print('  \\q                         — выход')
    print()
    print('Вставка файла в сообщение: @::путь/к/файлу::')
    print()


def run_chat() -> int:
    try:
        config = load_config()
    except ConfigError as exception:
        print(f'Ошибка конфигурации: {exception}')
        return 1

    client = Llm(config)
    history: list[Message] = []

    print_welcome(config)

    while True:
        try:
            user_input = _sanitize(input('>>> ').strip())
        except EOFError:
            break

        if user_input == '':
            continue
        if user_input == '\\q':
            break
        if user_input == '/help':
            print_help()
            continue
        if user_input == '/reset':
            history = []
            clear_screen()
            print_welcome(config)
            continue
        if user_input.startswith('/file_chunk') or user_input.startswith('/filechunk'):
            run_file_with_chunks(client, config, user_input)
            continue

        expanded, errors = expand_file_tokens(user_input)
        for err in errors:
            print(f'Ошибка файла: {err}')

        user_message: Message = {'role': 'user', 'content': expanded}
        history = apply_limits(history, user_message, config.limit_messages, config.limit_chars)
        messages = build_messages(history, config.system_prompt)

        result = request(client, config, messages)
        if result is None:
            continue
        if not config.streaming:
            print(result)
        history.append({'role': 'assistant', 'content': result})

    return 0


def main() -> None:
    raise SystemExit(run_chat())
