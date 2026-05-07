# Task 1 — parallel sum calculation using multiprocessing
# Computes sum(1..N) by splitting range into chunks, computing partial sums in separate processes.

import sys
import time
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

N = 1_000_000_000  # sum from 1 to N
NUM_WORKERS = 8


def partial_sum(args: tuple[int, int]) -> int:
    """Compute sum of integers from start to end (inclusive)."""
    start, end = args
    s = 0
    for i in range(start, end + 1):
        s += i
    return s


def main():
    chunk_size = N // NUM_WORKERS
    ranges = []
    for i in range(NUM_WORKERS):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < NUM_WORKERS - 1 else N
        ranges.append((start, end))

    start_time = time.perf_counter()

    with Pool(processes=NUM_WORKERS) as pool:
        partial_sums = pool.map(partial_sum, ranges)

    total = sum(partial_sums)
    elapsed = time.perf_counter() - start_time

    expected = N * (N + 1) // 2
    print(f"=== Multiprocessing sum ===")
    print(f"N = {N:,}")
    print(f"Workers: {NUM_WORKERS}")
    print(f"Result: {total:,}")
    print(f"Expected: {expected:,}")
    print(f"Correct: {total == expected}")
    print(f"Time: {elapsed:.4f} s")


if __name__ == "__main__":
    main()
