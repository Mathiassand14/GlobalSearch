from __future__ import annotations

from src.core.performance.text_processing import count_tokens_ws, split_tokens_ws


def test_count_tokens_ws_and_split_tokens_ws() -> None:
    s = b"hello  world\nthis\tis  a test\n"
    assert count_tokens_ws(s) == 6
    assert split_tokens_ws(s) == ["hello", "world", "this", "is", "a", "test"]

