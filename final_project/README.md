# GigaVibeMiptCode

Чат-бот в консоли для общения с LLM. Написан на Python, работает через Ollama

## Как запустить

Скачать Ollama на сайте ollama.com. После установки запустить:

```bash
ollama pull gemma3:270m
pip install -r requirements.txt
```

Создать файл `config.yaml` в папке `final_project`:

```yaml
api_key: ваш_ключ
api_host: http://localhost:11434/v1/
model: gemma3:270m
temperature: 0.2
limit_message: 20
limit_chars: 2000
streaming: true
system_prompt: Ты полезный ассистент.
```


Как запустить:

```bash
cd final_project
python main.py
```

Тесты

```bash
pytest tests/ -v
```

## Команды

- \q - выйти
- /reset - очистить историю и экран
- /filechunk - обработать большой файл по частям

Режимы чанков:

```
/filechunk paragraph=4     # по 4 абзаца
/filechunk -y              # без подтверждения каждого чанка
/filechunk len=500         # по 500 символов
```