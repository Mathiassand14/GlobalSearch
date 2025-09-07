from __future__ import annotations

from src.core.search.strategies import ExactSearchStrategy


def test_tokenize_and_parse_basic():
    s = ExactSearchStrategy()
    q = s.build_query('(apple OR "banana bread") AND NOT cherry')
    # Must with: should(apple, banana bread) and must_not(cherry)
    assert "bool" in q
    must = q["bool"]["must"]
    assert isinstance(must, list) and len(must) == 2
    should = must[0]["bool"]["should"]
    assert any(item.get("multi_match", {}).get("query") == "apple" for item in should)
    assert any(item.get("multi_match", {}).get("query") == "banana bread" for item in should)
    assert q["bool"]["must"][1]["bool"]["must_not"][0]["multi_match"]["query"] == "cherry"


def test_invalid_expressions_raise():
    s = ExactSearchStrategy()
    for expr in ["AND apple", "(apple OR banana", "apple OR ) banana"]:
        try:
            s.build_query(expr)
            assert False, "expected ValueError"
        except ValueError:
            pass


def test_search_calls_es_with_built_query():
    class _FakeES:
        def __init__(self) -> None:
            self.calls = []

        def search(self, index: str, **body):  # noqa: ANN001
            self.calls.append((index, body))
            return {"ok": True}

    s = ExactSearchStrategy()
    es = _FakeES()
    res = s.search(es, index="documents", expression="apple AND banana", size=5)
    assert res["ok"] is True
    assert es.calls
    idx, body = es.calls[0]
    assert idx == "documents"
    assert body["size"] == 5
    assert body["query"]["bool"]["must"][0]["multi_match"]["query"] == "apple"
    assert body["query"]["bool"]["must"][1]["multi_match"]["query"] == "banana"

