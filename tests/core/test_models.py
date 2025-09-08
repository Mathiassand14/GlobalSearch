from datetime import datetime, timedelta
from pathlib import Path

import pytest

from src.core.models.document import Document
from src.core.models.search import MatchType, SearchResult
from src.core.models.topic import TopicNode, TopicTree
from src.core.models.configuration import ApplicationConfig, SearchSettings
from src.core.models.service import ReEncodingResult


def test_document_validation():
    now = datetime.utcnow()
    doc = Document(
        id="1",
        file_path=Path("/tmp/file.pdf"),
        title="Sample",
        content="Hello",
        page_count=1,
        file_size=100,
        created_date=now,
        modified_date=now + timedelta(seconds=1),
    )
    assert doc.page_count == 1

    with pytest.raises(ValueError):
        Document(
            id="2",
            file_path=Path("/tmp/file.pdf"),
            title="Bad",
            content="",
            page_count=-1,
            file_size=0,
            created_date=now,
            modified_date=now,
        )


def test_search_result_validation_and_topic_path():
    sr = SearchResult(
        document_id="1",
        document_title="Doc",
        page_number=0,
        snippet="...",
        relevance_score=0.9,
        match_type=MatchType.FUZZY,
        highlighted_text="<b>hit</b>",
        topic_path="algorithms/trees",
    )
    assert sr.topic_path == "algorithms/trees"

    with pytest.raises(ValueError):
        SearchResult(
            document_id="1",
            document_title="Doc",
            page_number=-1,
            snippet="...",
            relevance_score=0.9,
            match_type=MatchType.EXACT,
            highlighted_text="hit",
        )


def test_topic_tree_counts():
    child = TopicNode(name="binary_trees", path="algorithms/trees/binary_trees")
    parent = TopicNode(name="trees", path="algorithms/trees", children=[child])
    root = TopicNode(name="algorithms", path="algorithms", children=[parent])
    tree = TopicTree(root_nodes=[root], total_topics=3, generation_timestamp=datetime.utcnow())
    assert tree.total_topics == 3

    with pytest.raises(ValueError):
        TopicTree(root_nodes=[root], total_topics=2, generation_timestamp=datetime.utcnow())


def test_config_and_reencoding_validation():
    cfg = ApplicationConfig(search_settings=SearchSettings())
    assert cfg.search_settings.fuzzy_edit_distance == 2

    res = ReEncodingResult(
        total_documents=10,
        re_encoded_documents=7,
        failed_documents=3,
        old_model="all-MiniLM-L6-v1",
        new_model="all-MiniLM-L6-v2",
        is_complete=True,
    )
    assert res.is_complete is True

    with pytest.raises(ValueError):
        ReEncodingResult(
            total_documents=5,
            re_encoded_documents=4,
            failed_documents=3,
            old_model="a",
            new_model="b",
            is_complete=False,
        )

