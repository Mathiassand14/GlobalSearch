from __future__ import annotations

from typing import List


def _py_count_tokens_ws(data: bytes) -> int:
    in_tok = False
    cnt = 0
    for b in data:
        if b <= 32:
            in_tok = False
        else:
            if not in_tok:
                cnt += 1
                in_tok = True
    return cnt


def _py_split_tokens_ws(data: bytes) -> List[str]:
    buf: List[str] = []
    start = None
    for i, b in enumerate(data):
        if b <= 32:
            if start is not None:
                buf.append(data[start:i].decode("utf-8", "ignore"))
                start = None
        else:
            if start is None:
                start = i
    if start is not None:
        buf.append(data[start:].decode("utf-8", "ignore"))
    return buf


try:  # Attempt to import Cython-accelerated functions
    from ._text_processing import count_tokens_ws as cy_count_tokens_ws  # type: ignore
    from ._text_processing import split_tokens_ws as cy_split_tokens_ws  # type: ignore
except Exception:  # pragma: no cover - fallback path
    cy_count_tokens_ws = None  # type: ignore
    cy_split_tokens_ws = None  # type: ignore


def count_tokens_ws(data: bytes) -> int:
    if cy_count_tokens_ws is not None:
        try:
            return int(cy_count_tokens_ws(data))  # type: ignore[misc]
        except Exception:  # pragma: no cover
            pass
    return _py_count_tokens_ws(data)


def split_tokens_ws(data: bytes) -> List[str]:
    if cy_split_tokens_ws is not None:
        try:
            return list(cy_split_tokens_ws(data))  # type: ignore[misc]
        except Exception:  # pragma: no cover
            pass
    return _py_split_tokens_ws(data)

