from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, List, Optional, Sequence, Tuple


@dataclass(slots=True)
class _Node:
    pass


@dataclass(slots=True)
class _Term(_Node):
    value: str


@dataclass(slots=True)
class _Not(_Node):
    child: _Node


@dataclass(slots=True)
class _And(_Node):
    left: _Node
    right: _Node


@dataclass(slots=True)
class _Or(_Node):
    left: _Node
    right: _Node


class ExactSearchStrategy:
    """Parses boolean expressions and builds Elasticsearch queries (req 1.1, 4.4, 5.1)."""

    FIELDS: Tuple[str, ...] = ("title^2", "content")

    def __init__(self) -> None:
        self._token_re = re.compile(
            r"\s*(\()|\s*(\))|\s*(AND|OR|NOT)\b|\s*\"([^\"]+)\"|\s*([^\s\)\(]+)",
            re.IGNORECASE,
        )

    # ---------- Public API ----------
    def build_query(self, expression: str) -> dict:
        root = self._parse(expression)
        return self._to_es(root)

    def search(self, es_client: Any, index: str, expression: str, size: int = 10) -> dict:
        body = {
            "size": int(size),
            "query": self.build_query(expression),
            "highlight": {"fields": {"content": {}}},
        }
        return es_client.search(index=index, **body)

    # ---------- Parsing ----------
    def _tokenize(self, s: str) -> List[str]:
        tokens: List[str] = []
        pos = 0
        while pos < len(s):
            m = self._token_re.match(s, pos)
            if not m:
                raise ValueError(f"Unexpected token at position {pos}")
            pos = m.end()
            if m.group(1):
                tokens.append("(")
            elif m.group(2):
                tokens.append(")")
            elif m.group(3):
                tokens.append(m.group(3).upper())
            elif m.group(4):
                tokens.append(m.group(4))
            elif m.group(5):
                tokens.append(m.group(5))
            else:
                # Only whitespace matched; advance
                continue
        return tokens

    def _parse(self, s: str) -> _Node:
        tokens = self._tokenize(s)
        if not tokens:
            raise ValueError("Empty expression")
        # Shunting-yard to RPN
        output: List[_Node] = []
        ops: List[str] = []

        def prec(op: str) -> int:
            return {"NOT": 3, "AND": 2, "OR": 1}.get(op, 0)

        def apply_op(op: str) -> None:
            if op == "NOT":
                if not output:
                    raise ValueError("NOT missing operand")
                child = output.pop()
                output.append(_Not(child))
            else:
                if len(output) < 2:
                    raise ValueError(f"{op} missing operands")
                right = output.pop()
                left = output.pop()
                output.append(_And(left, right) if op == "AND" else _Or(left, right))

        i = 0
        while i < len(tokens):
            t = tokens[i]
            if t == "(":
                ops.append(t)
            elif t == ")":
                while ops and ops[-1] != "(":
                    apply_op(ops.pop())
                if not ops:
                    raise ValueError("Mismatched parenthesis")
                ops.pop()  # remove '('
            elif t in ("AND", "OR", "NOT"):
                while ops and ops[-1] in ("AND", "OR", "NOT") and prec(ops[-1]) >= prec(t):
                    apply_op(ops.pop())
                ops.append(t)
            else:
                output.append(_Term(t))
            i += 1

        while ops:
            op = ops.pop()
            if op in ("(", ")"):
                raise ValueError("Mismatched parenthesis")
            apply_op(op)

        if len(output) != 1:
            raise ValueError("Invalid expression")
        return output[0]

    # ---------- ES conversion ----------
    def _to_es(self, node: _Node) -> dict:
        if isinstance(node, _Term):
            return {"multi_match": {"query": node.value, "fields": list(self.FIELDS)}}
        if isinstance(node, _Not):
            return {"bool": {"must_not": [self._to_es(node.child)]}}
        if isinstance(node, _And):
            return {"bool": {"must": [self._to_es(node.left), self._to_es(node.right)]}}
        if isinstance(node, _Or):
            return {"bool": {"should": [self._to_es(node.left), self._to_es(node.right)], "minimum_should_match": 1}}
        raise TypeError("Unknown node type")

