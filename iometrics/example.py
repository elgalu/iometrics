#!/usr/bin/env python3
import time

from iometrics import NetworkMetrics, DiskMetrics


DUAL_METRICS_HEADER = """
|        Network (MBytes/s)       | Disk Util |            Disk MBytes          |             Disk I/O            |
|     Received    |     Sent      |     %     |    MB/s Read    |  MB/s Written |     I/O Read    |   I/O Write   |
|   val  |   avg  |  val  |  avg  | val | avg |  val   |  avg   |  val  |  avg  |   val  |   avg  |  val  |  avg  |
| ------:| ------:| -----:| -----:| ---:| ---:| ------:| ------:| -----:| -----:| ------:| ------:| -----:| -----:|"""


def usage() -> None:
    """
    ## Example usage and example output:

    ```markdown
    |        Network (MBytes/s)       | Disk Util |            Disk MBytes          |           Disk I/O          |
    |     Received    |     Sent      |     %     |    MB/s Read    |  MB/s Written |     I/O Read    | I/O Write |
    |   val  |   avg  |  val  |  avg  | val | avg |  val   |  avg   |  val  |  avg  |   val  |   avg  | val | avg |
    | ------:| ------:| -----:| -----:| ---:| ---:| ------:| ------:| -----:| -----:| ------:| ------:| ---:| ---:|
    |    4.6 |    3.5 |   0.1 |   0.1 |  49 |   2 |   52.8 |    1.1 |   0.0 |   0.9 |    211 |      4 |   5 |  18 |
    |    4.1 |    3.5 |   0.1 |   0.1 |  61 |   3 |   60.4 |    2.4 |  40.3 |   1.7 |    255 |     10 | 149 |  21 |
    ```
    """
    net  = NetworkMetrics()
    disk = DiskMetrics()

    for i in range(10000):
        time.sleep(1)

        net.update_stats()
        disk.update_stats()

        print(DUAL_METRICS_HEADER) if i % 15 == 0 else None
        row = (
            f"| {net.mb_recv_ps.val:6.1f} | {net.mb_recv_ps.avg:6.1f} "
            f"| {net.mb_sent_ps.val:5.1f} | {net.mb_sent_ps.avg:5.1f} "
            f"| {int(disk.io_util.val):3d} | {int(disk.io_util.avg):3d} "
            f"| {disk.mb_read.val:6.1f} | {disk.mb_read.avg:6.1f} "
            f"| {disk.mb_writ.val:5.1f} | {disk.mb_writ.avg:5.1f} "
            f"| {int(disk.io_read.val):6d} | {int(disk.io_read.avg):6d} "
            f"| {int(disk.io_writ.val):5d} | {int(disk.io_writ.avg):5d} "
            f"|"
        )
        print(row)

# `__all__` is left here for documentation purposes and as a
# reference to which interfaces are meant to be imported.
__all__ = [
    "usage",
]
