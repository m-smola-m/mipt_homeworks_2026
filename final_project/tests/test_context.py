from gigavibe.context import apply_limits


def test_oldest_message_drops_at_limit() -> None:
    history = [
        {'role': 'user', 'content': 'Привет, объясни что такое рекурсия'},
        {'role': 'assistant', 'content': 'Рекурсия — это когда функция вызывает сама себя'},
    ]
    new_msg = {'role': 'user', 'content': 'Дай пример на питоне'}
    result = apply_limits(history, new_msg, limit_messages=2, limit_chars=None)
    assert result == [
        {'role': 'assistant', 'content': 'Рекурсия — это когда функция вызывает сама себя'},
        {'role': 'user', 'content': 'Дай пример на питоне'},
    ]


def test_char_limit_trims_old_messages() -> None:
    history = [
        {'role': 'user', 'content': 'напиши мне сортировку пузырьком'},
        {'role': 'assistant', 'content': 'держи'},
    ]
    new_msg = {'role': 'user', 'content': 'а теперь быструю'}
    result = apply_limits(history, new_msg, limit_messages=None, limit_chars=20)
    assert result == [{'role': 'user', 'content': 'а теперь быструю'}]


def test_message_too_long_gets_cut_from_left() -> None:
    new_msg = {'role': 'user', 'content': 'очень длинный вопрос про питон'}
    result = apply_limits([], new_msg, limit_messages=None, limit_chars=5)
    assert result == [{'role': 'user', 'content': 'питон'}]


def test_no_limits_keeps_all_messages() -> None:
    history = [
        {'role': 'user', 'content': 'раз'},
        {'role': 'assistant', 'content': 'два'},
    ]
    new_msg = {'role': 'user', 'content': 'три'}
    result = apply_limits(history, new_msg, limit_messages=None,
                          limit_chars=None)
    assert len(result) == 3
    assert result[-1]['content'] == 'три'


def test_both_limits_applied_together() -> None:
    history = [
        {'role': 'user', 'content': 'первое сообщение'},
        {'role': 'assistant', 'content': 'первый ответ'},
        {'role': 'user', 'content': 'второе сообщение'},
        {'role': 'assistant', 'content': 'второй ответ'},
    ]
    new_msg = {'role': 'user', 'content': 'итого'}
    result = apply_limits(history, new_msg, limit_messages=3, limit_chars=30)
    assert len(result) <= 3
    total = sum(len(m['content']) for m in result)
    assert total <= 30
