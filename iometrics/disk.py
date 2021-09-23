#!/usr/bin/env python3
"""
## Classes to store Disk I/O Statistics.

Ground truth comes from `/proc/diskstats`, a file with stats updated by the *nix kernel.

The list of devices comes from `/sys/block` directory.

:copyright: (c) 2021 by Leo Gallucci.
:license: Apache 2.0, see LICENSE for more details.
"""
import os
import time
from dataclasses import dataclass
from typing import Dict
from typing import List

from iometrics.average_metrics import AverageMetrics


@dataclass
class DiskStats:

    """Simple data class to store disks relevant statistics."""

    kb_read: int = 0
    kb_writ: int = 0
    io_read: int = 0
    io_writ: int = 0
    io_util: int = 0


@dataclass
class AggregateDiskStats:

    """Simple data class to store disks aggregate relevant statistics."""

    mb_read_ps: float = 0.0
    mb_writ_ps: float = 0.0
    io_read_ps: float = 0.0
    io_writ_ps: float = 0.0
    io_util: float = 0.0


class DiskMetrics:

    """Tracks and computes disks read/written MBytes/s, also utilization and io counts metrics."""

    def __init__(self) -> None:
        self.mb_read = AverageMetrics()
        self.mb_writ = AverageMetrics()
        self.io_read = AverageMetrics()
        self.io_writ = AverageMetrics()
        self.io_util = AverageMetrics()

        self.non_virtual_devices = get_non_virtual_disk_devices()

        self.last_stats: Dict[str, DiskStats] = self.get_disks_stats()
        self.last_log_time: float = time.time()

    def get_disks_stats(self) -> Dict[str, DiskStats]:
        """Return number of disk reads, writes, io (since the kernel started)."""
        # Note: all counters at /proc/* are starting with zero when the kernel starts.
        with open("/proc/diskstats") as file:
            content: str = file.read()

        lines = content.splitlines()

        # Accumulate the stats of each device:
        stats: Dict[str, DiskStats] = {}

        for device_line in lines:
            fields: List[str] = device_line.strip().split()
            device_name: str = fields[2]

            if device_name not in self.non_virtual_devices:
                continue

            device_stats = DiskStats(
                io_read=int(fields[3]),
                io_writ=int(fields[7]),
                io_util=int(fields[12]),
                kb_read=int(fields[5]),
                kb_writ=int(fields[9]),
            )

            stats[device_name] = device_stats

        return stats

    def update_stats(self) -> None:
        """Compute metrics since last measurement then returns stats per second."""
        time_delta: float = time.time() - self.last_log_time

        per_device_stats: Dict[str, DiskStats] = self.get_disks_stats()

        aggr = AggregateDiskStats()

        for device_name, last_all_devices_stats in self.last_stats.items():
            new_aggr = compute_new_stats_ps(per_device_stats, last_all_devices_stats, device_name, time_delta)

            aggr.mb_read_ps += new_aggr.mb_read_ps
            aggr.mb_writ_ps += new_aggr.mb_writ_ps
            aggr.io_read_ps += new_aggr.io_read_ps
            aggr.io_writ_ps += new_aggr.io_writ_ps
            aggr.io_util += new_aggr.io_util

        avg_disks_io_util: float = aggr.io_util / len(self.last_stats)

        self.mb_read.update(aggr.mb_read_ps)
        self.mb_writ.update(aggr.mb_writ_ps)
        self.io_read.update(aggr.io_read_ps)
        self.io_writ.update(aggr.io_writ_ps)
        self.io_util.update(avg_disks_io_util)

        self.last_log_time = time.time()
        self.last_stats = per_device_stats


def get_non_virtual_disk_devices() -> List[str]:
    """Return a list of currently attached Disk names to which makes sense to measure I/O performance."""
    disks_devices_dir = "/sys/block"

    non_virtual_devices: List[str] = []

    for device_name in os.listdir(disks_devices_dir):
        abs_device_path = os.path.join(disks_devices_dir, device_name)

        if os.path.islink(abs_device_path):
            link_target = os.readlink(abs_device_path)
            if "virtual" not in link_target:
                non_virtual_devices.append(device_name)

    return non_virtual_devices


def compute_new_stats_ps(
    per_device_stats: Dict[str, DiskStats], last_all_devices_stats: DiskStats, device_name: str, time_delta: float
) -> AggregateDiskStats:
    """Compute the new stats per second based on last ones and the time delta."""
    aggr = AggregateDiskStats()

    bytes_read_delta: int = 0
    bytes_writ_delta: int = 0

    # Devices like AWS EBS or USB drives can get dynamically detached so validate key:
    if device_name in per_device_stats:
        bytes_read_delta = per_device_stats[device_name].kb_read - last_all_devices_stats.kb_read
        bytes_writ_delta = per_device_stats[device_name].kb_writ - last_all_devices_stats.kb_writ

    # There's a bug that sometimes the delta is negative messing up the average.
    bytes_read_delta = max(0, bytes_read_delta)
    bytes_read_delta = max(0, bytes_read_delta)

    aggr.mb_read_ps = bytes_read_delta * 512.0 / 1e6 / time_delta
    aggr.mb_writ_ps = bytes_writ_delta * 512.0 / 1e6 / time_delta

    io_read_delta: int = 0
    io_writ_delta: int = 0

    # Devices like AWS EBS or USB drives can get dynamically detached so validate key:
    if device_name in per_device_stats:
        io_read_delta = per_device_stats[device_name].io_read - last_all_devices_stats.io_read
        io_writ_delta = per_device_stats[device_name].io_writ - last_all_devices_stats.io_writ

    # There's a bug that sometimes the delta is negative messing up the average.
    io_read_delta = max(0, io_read_delta)
    io_writ_delta = max(0, io_writ_delta)

    aggr.io_read_ps = io_read_delta / time_delta
    aggr.io_writ_ps = io_writ_delta / time_delta

    util_delta: int = per_device_stats[device_name].io_util - last_all_devices_stats.io_util
    util_delta = max(0, util_delta)
    aggr.io_util = 100 * util_delta / (time_delta * 1000.0)
    aggr.io_util = min(100, aggr.io_util)

    return aggr


# `__all__` is left here for documentation purposes and as a
# reference to which interfaces are meant to be imported.
__all__ = [
    "DiskMetrics",
]
