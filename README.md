# iometrics

[![Python](https://github.com/elgalu/iometrics/raw/main/docs/img/badges/language.svg)](https://devdocs.io/python/)

Monitor and log Network and Disks statistics in MegaBytes per second.

## Install

```sh
pip install iometrics
```

## Usage

### Pytorch-lightning integration

```py
from pytorch_lightning import Trainer
from iometrics.pytorch_lightning.callbacks import NetworkAndDiskStatsMonitor

net_disk_stats = NetworkAndDiskStatsMonitor()

trainer = Trainer(callbacks=[net_disk_stats])
```

#### Metrics generated

* **network/recv_MB_per_sec**    – Received MB/s on all relevant network interfaces as a SUM.
* **network/sent_MB_per_sec**    – Sent     MB/s on all relevant network interfaces as a SUM.
* **disk/util%**                 – Disk utilization percentage as the average of all disk devices.
* **disk/read_MB_per_sec**       – Disks read MB/s    as the sum of all disk devices.
* **disk/writ_MB_per_sec**       – Disks written MB/s as the sum of all disk devices.
* **disk/io_read_count_per_sec** – Disks read I/O operations per second    as the sum of all disk devices.
* **disk/io_writ_count_per_sec** – Disks written I/O operations per second as the sum of all disk devices.

#### Screen shot

<img id="png_recv_MB_per_sec" width="450"
 src="https://github.com/elgalu/iometrics/raw/main/docs/img/metrics/network_recv_MB_per_sec.png" />

### Pure-Python implementation (zero dependencies)

#### Quick check

```sh
python -c 'from iometrics.example import usage; usage()'
```

#### Example output

```markdown
|        Network (MBytes/s)       | Disk Util |            Disk MBytes          |           Disk I/O          |
|     Received    |     Sent      |     %     |    MB/s Read    |  MB/s Written |     I/O Read    | I/O Write |
|   val  |   avg  |  val  |  avg  | val | avg |  val   |  avg   |  val  |  avg  |   val  |   avg  | val | avg |
| ------:| ------:| -----:| -----:| ---:| ---:| ------:| ------:| -----:| -----:| ------:| ------:| ---:| ---:|
|    4.6 |    3.5 |   0.1 |   0.1 |  49 |   2 |   52.8 |    1.1 |   0.0 |   0.9 |    211 |      4 |   5 |  18 |
|    4.1 |    3.5 |   0.1 |   0.1 |  61 |   3 |   60.4 |    2.4 |  40.3 |   1.7 |    255 |     10 | 149 |  21 |
```

#### Full code

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

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)
