#!/usr/bin/env python3
import time
import iometrics
from iometrics.pytorch_lightning.callbacks import NetworkAndDiskStatsMonitor
from iometrics.pytorch_lightning.callbacks import LOG_KEY_DISK_UTIL


def test_all_metrics() -> None:
    last_row = iometrics.usage(1)
    assert "0.0" in last_row

def test_pytorch_lightning() -> None:

    net_disk_stats = NetworkAndDiskStatsMonitor()

    first_logs: Dict[str, float] = net_disk_stats._get_new_logs()

    assert LOG_KEY_DISK_UTIL in first_logs
    assert 0.0 in first_logs.values()
