#!/usr/bin/env python3
"""
Exact verifier for an 18-vertex counterexample to WOWII Conjecture 59.

Conjecture 59:
    f(G) >= ceil(sqrt(residue(G) * b(G)))

Here:
  f(G)       = maximum order of an induced forest,
  residue(G) = Havel--Hakimi residue,
  b(G)       = maximum order of an induced bipartite subgraph.

The program uses only Python's standard library and exhaustively checks all
2^18 induced vertex subsets for b(G) and f(G).
"""

from collections import deque
from math import isqrt

N = 18
CORE_EDGES = [
    (0, 5), (1, 5),
    (0, 6), (1, 6), (2, 6),
    (0, 7), (1, 7), (2, 7), (3, 7),
    (0, 8), (1, 8), (2, 8), (3, 8), (4, 8),
    (0, 9), (1, 9), (2, 9), (3, 9), (4, 9),
]
HUB = 10
LEAVES = range(11, 18)

EDGES = CORE_EDGES + [(HUB, v) for v in range(10)] + [(HUB, v) for v in LEAVES]

ADJ = [0] * N
for u, v in EDGES:
    if not (0 <= u < N and 0 <= v < N and u != v):
        raise ValueError(f"Invalid edge {(u, v)}")
    ADJ[u] |= 1 << v
    ADJ[v] |= 1 << u


def connected() -> bool:
    seen = 1
    frontier = 1
    while frontier:
        next_frontier = 0
        bits = frontier
        while bits:
            bit = bits & -bits
            v = bit.bit_length() - 1
            bits -= bit
            next_frontier |= ADJ[v]
        next_frontier &= ~seen
        seen |= next_frontier
        frontier = next_frontier
    return seen == (1 << N) - 1


def havel_hakimi_residue() -> tuple[int, list[list[int]]]:
    seq = sorted((a.bit_count() for a in ADJ), reverse=True)
    trace = [seq.copy()]
    while seq and seq[0] > 0:
        d = seq.pop(0)
        if d > len(seq):
            raise AssertionError("Degree sequence became nongraphical")
        for i in range(d):
            seq[i] -= 1
            if seq[i] < 0:
                raise AssertionError("Negative Havel--Hakimi entry")
        seq.sort(reverse=True)
        trace.append(seq.copy())
    return len(seq), trace


def induced_is_bipartite(mask: int) -> bool:
    color = [-1] * N
    remaining = mask
    while remaining:
        start_bit = remaining & -remaining
        start = start_bit.bit_length() - 1
        color[start] = 0
        q = deque([start])
        remaining &= ~start_bit

        while q:
            u = q.popleft()
            nbrs = ADJ[u] & mask
            while nbrs:
                bit = nbrs & -nbrs
                v = bit.bit_length() - 1
                nbrs -= bit
                if color[v] == -1:
                    color[v] = color[u] ^ 1
                    q.append(v)
                    remaining &= ~bit
                elif color[v] == color[u]:
                    return False
    return True


def induced_is_forest(mask: int) -> bool:
    parent = list(range(N))
    rank = [0] * N

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for u, v in EDGES:
        if not ((mask >> u) & 1 and (mask >> v) & 1):
            continue
        ru, rv = find(u), find(v)
        if ru == rv:
            return False
        if rank[ru] < rank[rv]:
            ru, rv = rv, ru
        parent[rv] = ru
        if rank[ru] == rank[rv]:
            rank[ru] += 1
    return True


def maximum_induced_order(predicate) -> tuple[int, int]:
    best_size = -1
    best_mask = 0
    for mask in range(1 << N):
        size = mask.bit_count()
        if size <= best_size:
            continue
        if predicate(mask):
            best_size = size
            best_mask = mask
    return best_size, best_mask


def vertices(mask: int) -> list[int]:
    return [v for v in range(N) if (mask >> v) & 1]


def ceil_sqrt(x: int) -> int:
    r = isqrt(x)
    return r if r * r == x else r + 1


assert connected()
residue, trace = havel_hakimi_residue()
b, bipartite_witness = maximum_induced_order(induced_is_bipartite)
f, forest_witness = maximum_induced_order(induced_is_forest)
rhs = ceil_sqrt(residue * b)

print(f"|V| = {N}, |E| = {len(EDGES)}, connected = {connected()}")
print(f"degree sequence = {trace[0]}")
print(f"Havel--Hakimi residue = {residue}")
print(f"b(G) = {b}; witness = {vertices(bipartite_witness)}")
print(f"f(G) = {f}; witness = {vertices(forest_witness)}")
print(f"ceil(sqrt(residue*b)) = ceil(sqrt({residue*b})) = {rhs}")
print(f"Conjectured inequality: {f} >= {rhs}  ->  {f >= rhs}")

assert residue == 10
assert b == 17
assert f == 13
assert rhs == 14
assert f < rhs
