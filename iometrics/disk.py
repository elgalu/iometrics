#!/usr/bin/env python3
import os
import re
import time
from typing import List, Dict
from dataclasses import dataclass

from iometrics.common import AverageMetrics


@dataclass
class DiskStats:
    """Stores Disk I/O statistics."""
    kb_read: int = 0
    kb_writ: int = 0
    io_read: int = 0
    io_writ: int = 0
    io_util: int = 0

class DiskMetrics:
    def __init__(self) -> None:
        self.mb_read = AverageMetrics()
        self.mb_writ = AverageMetrics()
        self.io_read = AverageMetrics()
        self.io_writ = AverageMetrics()
        self.io_util = AverageMetrics()

        self.non_virtual_devices = self.get_non_virtual_disk_devices()

        self.last_stats: Dict[str, DiskStats] = self.get_disks_stats()
        self.last_log_time: float = time.time()

    def get_non_virtual_disk_devices(self) -> List[str]:
        """Returns a list of currently attached Disk devices names to which it makes sense to measure I/O performance."""
        DISKS_DEVICES_DIR = "/sys/block"

        non_virtual_devices: List[str] = []

        for device_name in os.listdir(DISKS_DEVICES_DIR):
            abs_device_path = os.path.join(DISKS_DEVICES_DIR, device_name)

            if os.path.islink(abs_device_path):
                link_target = os.readlink(abs_device_path)
                if 'virtual' not in link_target:
                    non_virtual_devices.append(device_name)

        return non_virtual_devices

    def get_disks_stats(self) -> Dict[str, DiskStats]:
        """Returns number of disk reads, writes, io (since the kernel started)."""

        # Note: all counters at /proc/* are starting with zero when the kernel starts.
        with open('/proc/diskstats') as f1:
            content: str = f1.read()

        lines = content.splitlines()

        # Accumulate the stats of each device:
        stats: Dict[str, DiskStats] = {}

        for device_line in lines:
            fields: list = device_line.strip().split()
            device_name: str = fields[2]

            if device_name not in self.non_virtual_devices:
                continue

            device_stats = DiskStats(
                io_read = int(fields[3]),
                io_writ = int(fields[7]),
                io_util = int(fields[12]),
                kb_read = int(fields[5]),
                kb_writ = int(fields[9]),
            )

            stats[device_name] = device_stats

        return stats

    def update_stats(self) -> None:
        """Computes metrics since last measurement then returns stats per second."""
        time_delta: float = time.time() - self.last_log_time

        new_stats: Dict[str, DiskStats] = self.get_disks_stats()

        aggr_mb_read_ps: float = 0.0
        aggr_mb_writ_ps: float = 0.0
        aggr_io_read_ps: float = 0.0
        aggr_io_writ_ps: float = 0.0
        aggr_io_util:    float = 0.0

        for device_name, last_stats in self.last_stats.items():
            bytes_read_delta: int = new_stats[device_name].kb_read - last_stats.kb_read
            bytes_writ_delta: int = new_stats[device_name].kb_writ - last_stats.kb_writ

            # There's a bug that sometimes the delta is negative messing up the average.
            bytes_read_delta = max(0, bytes_read_delta)
            bytes_read_delta = max(0, bytes_read_delta)

            mb_read_ps: float = bytes_read_delta * 512.0 / 1e6 / time_delta
            mb_writ_ps: float = bytes_writ_delta * 512.0 / 1e6 / time_delta

            io_read_delta: int = new_stats[device_name].io_read - last_stats.io_read
            io_writ_delta: int = new_stats[device_name].io_writ - last_stats.io_writ

            # There's a bug that sometimes the delta is negative messing up the average.
            io_read_delta = max(0, io_read_delta)
            io_writ_delta = max(0, io_writ_delta)

            io_read_ps = io_read_delta / time_delta
            io_writ_ps = io_writ_delta / time_delta

            util_delta: int = new_stats[device_name].io_util - last_stats.io_util
            util_delta = max(0, util_delta)
            util = 100 * util_delta / (time_delta * 1000.0)

            aggr_mb_read_ps += mb_read_ps
            aggr_mb_writ_ps += mb_writ_ps
            aggr_io_read_ps += io_read_ps
            aggr_io_writ_ps += io_writ_ps
            aggr_io_util    += min(100, util)

        avg_disks_io_util: float = aggr_io_util / len(self.last_stats)

        self.mb_read.update(aggr_mb_read_ps)
        self.mb_writ.update(aggr_mb_writ_ps)
        self.io_read.update(aggr_io_read_ps)
        self.io_writ.update(aggr_io_writ_ps)
        self.io_util.update(avg_disks_io_util)

        self.last_log_time = time.time()
        self.last_stats = new_stats

# `__all__` is left here for documentation purposes and as a
# reference to which interfaces are meant to be imported.
__all__ = [
    "DiskMetrics",
]
