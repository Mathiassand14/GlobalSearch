from __future__ import annotations


def _dockerfile() -> str:
    with open('Dockerfile', 'r', encoding='utf-8') as f:
        return f.read()


def test_uv_layer_caching_and_manifests():
    df = _dockerfile()
    assert 'COPY pyproject.toml requirements*.txt uv.lock /app/' in df
    assert 'uv sync --frozen' in df


def test_pyqt6_runtime_dependencies_and_env():
    df = _dockerfile()
    # Ensure critical X11/Qt libs are installed
    assert 'libxkbcommon-x11-0' in df and 'libx11-6' in df and 'libgl1' in df
    # Offscreen platform for headless containers
    assert 'QT_QPA_PLATFORM=offscreen' in df

