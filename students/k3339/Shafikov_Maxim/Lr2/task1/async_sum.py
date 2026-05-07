# Task 1 — parallel sum calculation using asyncio
# Computes sum(1..N) by splitting range into chunks, using asyncio.to_thread for CPU-bound work.
# Note: sum is CPU-bound, so asyncio alone won't parallelize — we offload to threads via to_thread.

import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

N = 1_000_000_000  # sum from 1 to N
NUM_WORKERS = 8


def partial_sum(start: int, end: int) -> int:
    """Compute sum of integers from start to end (inclusive)."""
    s = 0
    for i in range(start, end + 1):
        s += i
    return s


async def main():
    chunk_size = N // NUM_WORKERS
    tasks = []

    for i in range(NUM_WORKERS):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < NUM_WORKERS - 1 else N
        tasks.append(asyncio.to_thread(partial_sum, start, end))

    start_time = time.perf_counter()
    partial_sums = await asyncio.gather(*tasks)
    total = sum(partial_sums)
    elapsed = time.perf_counter() - start_time

    expected = N * (N + 1) // 2
    print(f"=== Async (to_thread) sum ===")
    print(f"N = {N:,}")
    print(f"Workers: {NUM_WORKERS}")
    print(f"Result: {total:,}")
    print(f"Expected: {expected:,}")
    print(f"Correct: {total == expected}")
    print(f"Time: {elapsed:.4f} s")


if __name__ == "__main__":
    asyncio.run(main())
