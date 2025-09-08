# syntax=docker/dockerfile:1.7

# Base image with Python 3.11 and uv installed
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PATH="/root/.local/bin:${PATH}"

WORKDIR /app

# Install curl and build prerequisites for some packages; install uv
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       curl ca-certificates \
       libgl1 libopengl0 libegl1 libglib2.0-0 libdbus-1-3 \
       libxkbcommon-x11-0 libxkbcommon0 \
        libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 \
        libxcb-render-util0 libxcb-shape0 libxcb-xfixes0 libxcb-xinerama0 \
        libfontconfig1 libfreetype6 libxrender1 libxext6 libx11-6 \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh

# ---------- Dev/Test stage ----------
FROM base AS dev

# Leverage Docker layer caching: copy only manifests first
COPY pyproject.toml requirements*.txt uv.lock /app/
# Sync dependencies (dev included). Try frozen first for reproducibility.
RUN uv sync --frozen || uv sync

# Default command runs tests
ENTRYPOINT ["uv", "run"]
CMD ["pytest", "-q"]

# ---------- Runtime stage ----------
FROM base AS runtime

# Copy only manifests to install deps with cache
COPY pyproject.toml requirements*.txt uv.lock /app/
# Sync runtime dependencies only
RUN uv sync --frozen --no-dev || uv sync --no-dev

# Run the application via module entrypoint
ENV QT_QPA_PLATFORM=offscreen
ENTRYPOINT ["uv", "run"]
CMD ["python", "-m", "src.main"]
