#!/usr/bin/env python3
import re
import time
from typing import Dict
from dataclasses import dataclass

from iometrics.common import AverageMetrics


@dataclass
class NetworkStats:
    """Stores network I/O statistics."""
    bytes_recv: int = 0
    bytes_sent: int = 0

class NetworkMetrics:
    def __init__(self) -> None:
        self.mb_recv_ps = AverageMetrics()
        self.mb_sent_ps = AverageMetrics()

        self.last_stats: Dict[str, NetworkStats] = self.get_network_bytes()
        self.last_log_time: float = time.time()

    def get_network_bytes(self) -> Dict[str, NetworkStats]:
        """Returns received, transmitted bytes (since the kernel started)."""
        # Important: You should wait at least 1 second between calls to this function.
        # Before ~0.9 seconds `/proc/net/dev` will show the exact same values as last the time.

        INTERFACE_FILTER_OUT = re.compile(r'^(lo|tun.+|face.+|bond.+|.+\.\d+)$')

        # Note: all counters at /proc/* are starting with zero when the kernel starts.
        with open('/proc/net/dev') as f1:
            content: str = f1.read()

        lines: list = content.splitlines()
        lines = lines[2:]  # strip header

        # Accumulate the stats of each device:
        stats: Dict[str, NetworkStats] = {}

        for device_line in lines:
            fields: list = device_line.strip().split()
            device_name: str = fields[0].strip(':')

            if INTERFACE_FILTER_OUT.match(device_name):
                continue

            device_stats = NetworkStats(
                # Using max because sometimes it returns a negative (wrong) number
                bytes_recv = max(0, int(fields[1])),
                bytes_sent = max(0, int(fields[9])),
            )

            stats[device_name] = device_stats

        return stats

    def update_stats(self) -> None:
        """Computes metrics since last measurement then returns stats per second."""
        time_delta: float = time.time() - self.last_log_time

        # Important: You should wait at least 1 second between calls to the get_network_bytes function.
        # Before ~0.9 seconds `/proc/net/dev` will show the exact same values as last the time.
        if time_delta < 0.99:
            return None

        new_stats: Dict[str, NetworkStats] = self.get_network_bytes()

        aggr_mb_recv_ps: float = 0.0
        aggr_mb_sent_ps: float = 0.0

        # Note: iterate over last_stats instead of new_stats becase a new device
        #       could have been plugged and there won't be previous stats (baseline)
        # TODO: However, this might raise a KeyError if a device gets unplugged.
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

# `__all__` is left here for documentation purposes and as a
# reference to which interfaces are meant to be imported.
__all__ = [
    "NetworkMetrics",
]
