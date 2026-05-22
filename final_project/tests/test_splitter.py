from gigavibe.splitter import length_chunks, paragraph_chunks, split_paragraphs


def test_split_poem_by_stanzas() -> None:
    text = 'Раз ромашка\n\nДва ромашка\n\n\nТрррри ромашка'
    result = split_paragraphs(text)
    assert result == [
        'Раз ромашка',
        'Два ромашка',
        'Трррри ромашка',
    ]


def test_split_single_line_no_newlines() -> None:
    result = split_paragraphs('Просто строка без переносов')
    assert result == ['Просто строка без переносов']


def test_split_empty_text() -> None:
    assert split_paragraphs('') == []
    assert split_paragraphs('\n\n\n') == []


def test_paragraph_chunks_pairs_stanzas() -> None:
    text = 'раз\n\nдва\n\nтри\n\nелочка - гори'
    chunks = paragraph_chunks(text, 2)
    assert len(chunks) == 2
    assert 'раз' in chunks[0]
    assert 'три' in chunks[1]


def test_paragraph_chunks_more_than_text() -> None:
    text = 'абзац раз\n\nабзац два'
    chunks = paragraph_chunks(text, 10)
    assert len(chunks) == 1
    assert 'абзац раз' in chunks[0]


def test_length_chunks_splits_word() -> None:
    chunks = length_chunks('Обломов', 3)
    assert chunks == ['Обл', 'омо', 'в']


def test_length_chunks_exact_fit() -> None:
    chunks = length_chunks('питон', 5)
    assert chunks == ['питон']


def test_length_chunks_zero_raises() -> None:
    assert length_chunks('что-то', 0) == []
