#!/usr/bin/env python3
"""
## Classes to store Network I/O Statistics.

Ground truth comes from `/proc/net/dev`, a file with stats updated by the *nix kernel.

:copyright: (c) 2018 by Yaroslav Bulatov under The Unlicense <https://unlicense.org>
:copyright: (c) 2021 by Leo Gallucci under Apache License 2.0.
:license: Apache 2.0, see LICENSE for more details.
"""
import re
import time
from dataclasses import dataclass
from typing import Dict
from typing import List

from iometrics.average_metrics import AverageMetrics


@dataclass
class NetworkStats:

    """Simple data class to store network's relevant statistics."""

    bytes_recv: int = 0
    bytes_sent: int = 0


class NetworkMetrics:

    """Tracks and computes network received and sent MBytes/s metrics."""

    # pylint: disable=too-few-public-methods
    # One is reasonable in this case.

    def __init__(self) -> None:
        self.mb_recv_ps = AverageMetrics()
        self.mb_sent_ps = AverageMetrics()

        self.last_stats: Dict[str, NetworkStats] = get_network_bytes()
        self.last_log_time: float = time.time()

    def update_stats(self) -> None:
        """Compute metrics since last measurement then returns stats per second."""
        time_delta: float = time.time() - self.last_log_time

        # Important: You should wait at least 1 second between calls to the get_network_bytes function.
        # Before ~0.9 seconds `/proc/net/dev` will show the exact same values as last the time.
        if time_delta < 0.99:
            return

        new_stats: Dict[str, NetworkStats] = get_network_bytes()

        aggr_mb_recv_ps: float = 0.0
        aggr_mb_sent_ps: float = 0.0

        for device_name, last_stats in self.last_stats.items():
            bytes_recv_delta: int = new_stats[device_name].bytes_recv - last_stats.bytes_recv
            bytes_sent_delta: int = new_stats[device_name].bytes_sent - last_stats.bytes_sent

            # There's a bug that sometimes the delta is negative messing up the average.
            bytes_recv_delta = max(0, bytes_recv_delta)
            bytes_sent_delta = max(0, bytes_sent_delta)

            mb_recv_ps: float = bytes_recv_delta / 1e6 / time_delta
            mb_sent_ps: float = bytes_sent_delta / 1e6 / time_delta

            aggr_mb_recv_ps += mb_recv_ps
            aggr_mb_sent_ps += mb_sent_ps

        self.mb_recv_ps.update(aggr_mb_recv_ps)
        self.mb_sent_ps.update(aggr_mb_sent_ps)

        self.last_log_time = time.time()
        self.last_stats = new_stats


def get_network_bytes() -> Dict[str, NetworkStats]:
    """Return received, transmitted bytes (since the kernel started)."""
    # Important: You should wait at least 1 second between calls to this function.
    # Before ~0.9 seconds `/proc/net/dev` will show the exact same values as last the time.

    interface_filter_out = re.compile(r"^(lo|tun.+|face.+|bond.+|.+\.\d+)$")

    # Note: all counters at /proc/* are starting with zero when the kernel starts.
    with open("/proc/net/dev") as file:
        content: str = file.read()

    lines: List[str] = content.splitlines()
    lines = lines[2:]  # strip header

    # Accumulate the stats of each device:
    stats: Dict[str, NetworkStats] = {}

    for device_line in lines:
        fields: List[str] = device_line.strip().split()
        device_name: str = fields[0].strip(":")

        if interface_filter_out.match(device_name):
            continue

        device_stats = NetworkStats(
            # Using max because sometimes it returns a negative (wrong) number
            bytes_recv=max(0, int(fields[1])),
            bytes_sent=max(0, int(fields[9])),
        )

        stats[device_name] = device_stats

    return stats


# `__all__` is left here for documentation purposes and as a
# reference to which interfaces are meant to be imported.
__all__ = [
    "NetworkMetrics",
]
