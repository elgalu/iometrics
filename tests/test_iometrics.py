#!/usr/bin/env python3
import time
import iometrics


def test_all_metrics() -> None:
    last_row = iometrics.usage(1)
    assert "0.0" in last_row

def test_pytorch_lightning() -> None:
    from iometrics.pytorch_lightning.callbacks import NetworkAndDiskStatsMonitor
    net_disk_stats = NetworkAndDiskStatsMonitor()
