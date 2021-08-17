#!/usr/bin/env python3
"""
## Class to store Generic Statistics.

Computes and stores the average and current value of some metric.

:copyright: (c) 2018 by Yaroslav Bulatov under The Unlicense <https://unlicense.org>
:copyright: (c) 2021 by Leo Gallucci under Apache License 2.0.
:license: Apache 2.0, see LICENSE for more details.
"""
from dataclasses import dataclass


@dataclass
class AverageMetrics:

    """Tracks and computes generic metrics along with average, count, etc."""

    avg_mom: float = 0.5
    val: float = 0.0
    avg: float = 0.0
    smooth_avg: float = 0.0
    tot_sum: float = 0.0
    count: int = 0

    def __init__(self, avg_mom: float = 0.5) -> None:
        self.avg_mom = avg_mom
        self.reset()

    def reset(self) -> None:
        """Reset values when starting a new epoch (for example)."""
        self.val = 0.0
        self.avg = 0.0
        self.smooth_avg = 0.0
        self.tot_sum = 0.0
        self.count = 0

    def update(self, val: float) -> None:
        """Update last value and compute average, count, etc."""
        # Use max(0) to prevent rounding -0.0 negative numbers
        self.val = max(0, val)
        self.tot_sum += val
        if self.count == 0:
            self.smooth_avg = val
        else:
            self.smooth_avg = self.avg * self.avg_mom + val * (1 - self.avg_mom)
        self.count += 1
        self.avg = self.tot_sum / self.count


# `__all__` is left here for documentation purposes and as a
# reference to which interfaces are meant to be imported.
__all__ = [
    "AverageMetrics",
]
