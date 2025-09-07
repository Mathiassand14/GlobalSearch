from __future__ import annotations

from typing import Iterable, List

try:  # Numba is mandatory per requirements, but guard import for tests
    from numba import njit
except Exception:  # pragma: no cover - fallback if numba unavailable
    def njit(signature_or_function=None, **kwargs):  # type: ignore
        def wrapper(fn):
            return fn

        return wrapper


@njit(cache=True, fastmath=True)
def _cosine_numba(a, b) -> float:  # type: ignore[no-redef]
    num = 0.0
    da = 0.0
    db = 0.0
    n = len(a)
    for i in range(n):
        x = a[i]
        y = b[i]
        num += x * y
        da += x * x
        db += y * y
    if da == 0.0 or db == 0.0:
        return 0.0
    return num / ((da) ** 0.5 * (db) ** 0.5)


def cosine_similarity_numba(a: Iterable[float], b: Iterable[float]) -> float:
    va = [float(x) for x in a]
    vb = [float(x) for x in b]
    if len(va) != len(vb):
        raise ValueError("vector shapes must match")
    return float(_cosine_numba(va, vb))


def cosine_similarity_np(a: Iterable[float], b: Iterable[float]) -> float:
    va = [float(x) for x in a]
    vb = [float(x) for x in b]
    if len(va) != len(vb):
        raise ValueError("vector shapes must match")
    num = 0.0
    da = 0.0
    db = 0.0
    for i in range(len(va)):
        x = va[i]
        y = vb[i]
        num += x * y
        da += x * x
        db += y * y
    if da == 0.0 or db == 0.0:
        return 0.0
    return num / ((da ** 0.5) * (db ** 0.5))


def batch_cosine_parallel(vectors: List[Iterable[float]], query: Iterable[float], n_jobs: int = 2) -> List[float]:
    try:
        from joblib import Parallel, delayed  # type: ignore

        q = list(query)
        return list(Parallel(n_jobs=n_jobs)(delayed(cosine_similarity_numba)(v, q) for v in vectors))
    except Exception:  # Fallback to sequential if joblib missing
        q = list(query)
        return [cosine_similarity_numba(v, q) for v in vectors]


def gpu_available() -> bool:
    # Placeholder detection; real GPU path would use numba.cuda or cupy
    try:
        from numba import cuda  # type: ignore

        return bool(getattr(cuda, "is_available", lambda: False)())
    except Exception:
        return False
