from __future__ import annotations

import math

from src.core.performance import batch_cosine_parallel, cosine_similarity_np, cosine_similarity_numba, gpu_available


def test_cosine_similarity_matches_numpy() -> None:
    a = [1.0, 2.0, 3.0, 4.0]
    b = [4.0, 3.0, 2.0, 1.0]
    c1 = cosine_similarity_np(a, b)
    c2 = cosine_similarity_numba(a, b)
    assert math.isclose(c1, c2, rel_tol=1e-6)


def test_batch_cosine_parallel_runs() -> None:
    vecs = [[1, 0, 0], [0, 1, 0], [1, 1, 0]]
    q = [1, 0, 0]
    sims = batch_cosine_parallel(vecs, q, n_jobs=2)
    assert sims[0] > sims[1]
    assert len(sims) == 3


def test_gpu_available_returns_bool() -> None:
    assert isinstance(gpu_available(), bool)

