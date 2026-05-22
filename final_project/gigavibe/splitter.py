def split_paragraphs(text: str) -> list[str]:
    paragraphs: list[str] = []
    curr: list[str] = []
    for i in text.splitlines():
        if i.strip() == '':
            if curr:
                paragraphs.append('\n'.join(curr))
                curr = []
        else:
            curr.append(i)
    if curr:
        paragraphs.append('\n'.join(curr))
    return paragraphs


def paragraph_chunks(text: str, n: int) -> list[str]:
    if n < 1:
        return []
    paragraphs = split_paragraphs(text)
    chunks = []
    for i in range(0, len(paragraphs), n):
        chunk = '\n\n'.join(paragraphs[i:i + n])
        if chunk:
            chunks.append(chunk)
    return chunks


def length_chunks(text: str, chunk_len: int) -> list[str]:
    if chunk_len < 1:
        return []
    chunks = []
    for i in range(0, len(text), chunk_len):
        chunk = text[i : i + chunk_len]
        if chunk:
            chunks.append(chunk)
    return chunks


def iter_chunks(
    text: str,
    paragraphs_per_chunk: int | None,
    chunk_len: int | None,
) -> list[str]:
    if chunk_len is not None:
        return length_chunks(text, chunk_len)
    return paragraph_chunks(text, paragraphs_per_chunk or 1)
