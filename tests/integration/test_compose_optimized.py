from __future__ import annotations


def _read() -> str:
    with open('docker-compose.yml', 'r', encoding='utf-8') as f:
        return f.read()


def test_compose_has_only_es_and_app():
    text = _read()
    assert 'services:' in text
    assert 'elasticsearch:' in text and '\n  app:' in text
    # ensure no other common services appear
    assert 'postgresql:' not in text and 'redis:' not in text


def test_elasticsearch_healthcheck_present():
    text = _read()
    es_idx = text.find('elasticsearch:')
    assert 'healthcheck:' in text[es_idx:es_idx + 500]


def test_app_build_target_and_depends():
    text = _read()
    app_idx = text.find('\n  app:')
    segment = text[app_idx:app_idx + 800]
    assert 'target: runtime' in segment
    assert 'depends_on:' in segment and 'condition: service_healthy' in segment


def test_app_environment_and_volumes():
    text = _read()
    app_idx = text.find('\n  app:')
    segment = text[app_idx:app_idx + 800]
    assert 'ELASTICSEARCH_URL=' in segment
    assert ('./:/app' in segment) or ('./:/opt/project' in segment)
