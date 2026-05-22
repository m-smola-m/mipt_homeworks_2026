Message = dict[str, str]


def _total_chars(messages: list[Message]) -> int:
    return sum(len(i['content']) for i in messages)


def apply_limits(
    history: list[Message],
    new_message: Message,
    limit_messages: int | None,
    limit_chars: int | None,
) -> list[Message]:
    content = new_message['content']
    if limit_chars is not None:
        if len(content) > limit_chars:
            new_message = {'role': new_message['role'], 'content': content[-limit_chars:]}

    bank = list(history) + [new_message]

    if limit_messages is not None:
        while len(bank) > limit_messages:
            bank.pop(0)

    if limit_chars is not None:
        while len(bank) > 1 and _total_chars(bank) > limit_chars:
            bank.pop(0)

    return bank
