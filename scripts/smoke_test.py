from datetime import datetime, timedelta
from pathlib import Path

from src.core.models.document import Document
from src.core.models.search import MatchType, SearchResult
from src.core.models.topic import TopicNode, TopicTree
from src.core.models.configuration import ApplicationConfig, SearchSettings
from src.core.models.service import ReEncodingResult


def run() -> None:
    now = datetime.utcnow()
    # Document
    Document(
        id="1",
        file_path=Path("/tmp/file.pdf"),
        title="Sample",
        content="Hello",
        page_count=1,
        file_size=100,
        created_date=now,
        modified_date=now + timedelta(seconds=1),
    )

    # SearchResult
    SearchResult(
        document_id="1",
        document_title="Doc",
        page_number=0,
        snippet="...",
        relevance_score=0.9,
        match_type=MatchType.FUZZY,
        highlighted_text="<b>hit</b>",
        topic_path="algorithms/trees",
    )

    # Topic tree
    child = TopicNode(name="binary_trees", path="algorithms/trees/binary_trees")
    parent = TopicNode(name="trees", path="algorithms/trees", children=[child])
    root = TopicNode(name="algorithms", path="algorithms", children=[parent])
    TopicTree(root_nodes=[root], total_topics=3, generation_timestamp=now)

    # Config
    cfg = ApplicationConfig(search_settings=SearchSettings())
    assert cfg.search_settings.fuzzy_edit_distance == 2

    # ReEncodingResult
    ReEncodingResult(
        total_documents=10,
        re_encoded_documents=7,
        failed_documents=3,
        old_model="v1",
        new_model="v2",
        is_complete=True,
    )


if __name__ == "__main__":
    run()
    print("Smoke tests passed.")

