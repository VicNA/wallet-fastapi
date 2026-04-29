import asyncio
import random

BASE_DELAY = 0.01


async def backoff(attempt: int):
    delay = BASE_DELAY * (2 ** attempt)
    jitter = random.uniform(0, delay / 2)
    await asyncio.sleep(delay + jitter)
