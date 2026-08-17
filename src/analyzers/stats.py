from collections import deque
from typing import Dict, Optional
import math

class SpreadStats:
    def __init__(self, window: int = 0):
        self.window = window
        self.data: Dict[tuple, deque] = {}

    def update(self, symbol: str, exchange: str, spread: float):
        if self.window <= 0:
            return
        key = (symbol, exchange)
        if key not in self.data:
            self.data[key] = deque(maxlen=self.window)
        self.data[key].append(spread)

    def get_stats(self, symbol: str, exchange: str) -> Optional[Dict[str, float]]:
        key = (symbol, exchange)
        if key not in self.data or not self.data[key]:
            return None
        values = list(self.data[key])
        n = len(values)
        mean = sum(values) / n
        variance = sum((x - mean) ** 2 for x in values) / n
        std = math.sqrt(variance)
        return {
            "avg": mean,
            "min": min(values),
            "max": max(values),
            "std": std,
            "count": n
        }
