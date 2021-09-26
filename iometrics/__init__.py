#!/usr/bin/env python3
"""
## Network and Disk I/O Stats Monitor.

Monitor and log Network and Disks statistics in MegaBytes per second.

### Pytorch-lightning integration

```py
from pytorch_lightning import Trainer
from iometrics.pytorch_lightning.callbacks import NetworkAndDiskStatsMonitor

net_disk_stats = NetworkAndDiskStatsMonitor()

trainer = Trainer(callbacks=[net_disk_stats])
```

### Pure-Python implementation (zero dependencies)

```py
import time
from iometrics import NetworkMetrics, DiskMetrics
from iometrics.example import DUAL_METRICS_HEADER
net  = NetworkMetrics()
disk = DiskMetrics()
for i in range(100):
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
        f"| {int(disk.io_read.val):4d} | {int(disk.io_read.avg):4d} "
        f"| {int(disk.io_writ.val):3d} | {int(disk.io_writ.avg):3d} "
        f"|"
    )
    print(row)
```

#### Example output

```md
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
# Do not change the version here but rather `tbump "0.0.5" --only-patch`
__version__ = "0.0.7"

from iometrics.network import NetworkMetrics
from iometrics.disk import DiskMetrics

# `__all__` is left here for documentation purposes and as a
# reference to which interfaces are meant to be imported.
__all__ = [
    "__version__",
    "NetworkMetrics",
    "DiskMetrics",
]
