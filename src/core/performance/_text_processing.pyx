# cython: boundscheck=False, wraparound=False, initializedcheck=False, cdivision=True
# A tiny Cython extension for whitespace token counting and simple tokenization.

def count_tokens_ws(bytes data):
    cdef Py_ssize_t n = len(data)
    cdef Py_ssize_t i = 0
    cdef int in_tok = 0
    cdef Py_ssize_t cnt = 0
    while i < n:
        c = data[i]
        if c <= 32:
            if in_tok:
                in_tok = 0
            i += 1
            continue
        else:
            if not in_tok:
                cnt += 1
                in_tok = 1
            i += 1
    return int(cnt)

def split_tokens_ws(bytes data):
    cdef Py_ssize_t n = len(data)
    cdef Py_ssize_t i = 0
    cdef Py_ssize_t start = -1
    cdef list out = []
    while i < n:
        c = data[i]
        if c <= 32:
            if start != -1:
                out.append(data[start:i].decode('utf-8', 'ignore'))
                start = -1
            i += 1
        else:
            if start == -1:
                start = i
            i += 1
    if start != -1:
        out.append(data[start:n].decode('utf-8', 'ignore'))
    return out

