# Task 1 — parallel sum calculation using threading
# Computes sum(1..N) by splitting range into chunks, computing partial sums in worker threads.

import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

N = 1_000_000_000  # sum from 1 to N
NUM_WORKERS = 8


def partial_sum(start: int, end: int, results: list, idx: int) -> None:
    """Compute sum of integers from start to end (inclusive), store in results[idx]."""
    s = 0
    for i in range(start, end + 1):
        s += i
    results[idx] = s


def main():
    chunk_size = N // NUM_WORKERS
    results = [0] * NUM_WORKERS
    threads = []

    start_time = time.perf_counter()

    for i in range(NUM_WORKERS):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < NUM_WORKERS - 1 else N
        t = threading.Thread(target=partial_sum, args=(start, end, results, i))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    total = sum(results)
    elapsed = time.perf_counter() - start_time

    expected = N * (N + 1) // 2
    print(f"=== Threading sum ===")
    print(f"N = {N:,}")
    print(f"Workers: {NUM_WORKERS}")
    print(f"Result: {total:,}")
    print(f"Expected: {expected:,}")
    print(f"Correct: {total == expected}")
    print(f"Time: {elapsed:.4f} s")


if __name__ == "__main__":
    main()
