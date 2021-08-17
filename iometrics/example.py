#!/usr/bin/env python3
"""
## Show example usage and example output.

```py
from iometrics.example import usage
usage()
```

Example output

```markdown
|        Network (MBytes/s)       | Disk Util |            Disk MBytes          |           Disk I/O          |
|     Received    |     Sent      |     %     |    MB/s Read    |  MB/s Written |     I/O Read    | I/O Write |
|   val  |   avg  |  val  |  avg  | val | avg |  val   |  avg   |  val  |  avg  |   val  |   avg  | val | avg |
| ------:| ------:| -----:| -----:| ---:| ---:| ------:| ------:| -----:| -----:| ------:| ------:| ---:| ---:|
|    4.6 |    3.5 |   0.1 |   0.1 |  49 |   2 |   52.8 |    1.1 |   0.0 |   0.9 |    211 |      4 |   5 |  18 |
|    4.1 |    3.5 |   0.1 |   0.1 |  61 |   3 |   60.4 |    2.4 |  40.3 |   1.7 |    255 |     10 | 149 |  21 |
```

:copyright: (c) 2021 by Leo Gallucci.
:license: Apache 2.0, see LICENSE for more details.
"""
import time

from iometrics import DiskMetrics
from iometrics import NetworkMetrics


DUAL_METRICS_HEADER = """
|        Network (MBytes/s)       | Disk Util |            Disk MBytes          |             Disk I/O            |
|     Received    |     Sent      |     %     |    MB/s Read    |  MB/s Written |     I/O Read    |   I/O Write   |
|   val  |   avg  |  val  |  avg  | val | avg |  val   |  avg   |  val  |  avg  |   val  |   avg  |  val  |  avg  |
| ------:| ------:| -----:| -----:| ---:| ---:| ------:| ------:| -----:| -----:| ------:| ------:| -----:| -----:|"""


def usage(iterations: int = 10000) -> str:
    """Compute a live metric report of network and disk statistics."""
    net = NetworkMetrics()
    disk = DiskMetrics()

    for i in range(iterations):
        time.sleep(1)

        net.update_stats()
        disk.update_stats()

        if i % 15 == 0:
            print(DUAL_METRICS_HEADER)
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

    return row


# `__all__` is left here for documentation purposes and as a
# reference to which interfaces are meant to be imported.
__all__ = [
    "usage",
]
