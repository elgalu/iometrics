#!/usr/bin/env python3
"""
## Network and Disk I/O Stats Monitor.

Monitor and log Network and Disk stats during a PyTorch Lightning training.

Copyright 2021 The PyTorch Lightning Team under Apache 2.0 <http://www.apache.org/licenses/LICENSE-2.0>
Copyright 2021 Leo Gallucci               under Apache 2.0 <http://www.apache.org/licenses/LICENSE-2.0>
"""
from typing import Any
from typing import Dict
from typing import Optional

import pytorch_lightning as pl
from pytorch_lightning.callbacks.base import Callback
from pytorch_lightning.utilities import rank_zero_only
from pytorch_lightning.utilities.exceptions import MisconfigurationException
from pytorch_lightning.utilities.parsing import AttributeDict
from pytorch_lightning.utilities.types import STEP_OUTPUT

from iometrics import DiskMetrics
from iometrics import NetworkMetrics


# Metrics generated:
LOG_KEY_NETW_BYTES_RECV = "network/recv_MB_per_sec"
LOG_KEY_NETW_BYTES_SENT = "network/sent_MB_per_sec"
LOG_KEY_DISK_UTIL = "disk/util%"
LOG_KEY_DISK_MB_READ = "disk/read_MB_per_sec"
LOG_KEY_DISK_MB_WRIT = "disk/writ_MB_per_sec"
LOG_KEY_DISK_IO_READ = "disk/io_read_count_per_sec"
LOG_KEY_DISK_IO_WRIT = "disk/io_writ_count_per_sec"
LOG_KEY_DISK_IO_WAIT = "disk/io_wait%"


class NetworkAndDiskStatsMonitor(Callback):

    r"""
    Automatically monitors and logs Network and Disk stats during training stage.

    ``NetworkAndDiskStatsMonitor`` is a callback and in order to use it you need to assign a logger in the ``Trainer``.

    Args:
        track_network_utilization: Set to ``True`` to monitor network bytes send and received.
            at the start and end of each step. Default: ``True``.
        track_disk_utilization: Set to ``True`` to monitor Disk read, write, IO/s and percentage of Disk utilization.
            at the start and end of each step. Default: ``True``.

    Example::

        >>> from pytorch_lightning import Trainer
        >>> from iometrics.pytorch_lightning.callbacks import NetworkAndDiskStatsMonitor
        >>> net_disk_stats = NetworkAndDiskStatsMonitor()
        >>> trainer = Trainer(callbacks=[net_disk_stats]) # doctest: +SKIP

    Metrics generated:

    - **LOG_KEY_NETW_BYTES_RECV** – Received MegaBytes per second (MB/s) on all relevant network interfaces as a SUM.
    - **LOG_KEY_NETW_BYTES_SENT** – Sent     MegaBytes per second (MB/s) on all relevant network interfaces as a SUM.
    - **LOG_KEY_DISK_UTIL**       – Disk utilization percentage as the average of all disk devices.
    - **LOG_KEY_DISK_MB_READ**    – Disks read MB/s    as the sum of all disk devices.
    - **LOG_KEY_DISK_MB_WRIT**    – Disks written MB/s as the sum of all disk devices.
    - **LOG_KEY_DISK_IO_READ**    – Disks read I/O operations per second    as the sum of all disk devices.
    - **LOG_KEY_DISK_IO_WRIT**    – Disks written I/O operations per second as the sum of all disk devices.
    - **LOG_KEY_DISK_IO_WAIT**    – Disks I/O percentage of time that the CPU is waiting.

    Raises
    ------
     MisconfigurationException
        When something prevents this utility from being set up.

    """

    def __init__(
        self,
        track_network_utilization: bool = True,
        track_disk_utilization: bool = True,
    ):
        super().__init__()

        # AttributeDict is a subclass of dict that allows to access keys as attributes using dot notation.
        self._settings = AttributeDict(
            {
                "track_network_utilization": track_network_utilization,
                "track_disk_utilization": track_disk_utilization,
            }
        )

    def setup(self, trainer: "pl.Trainer", pl_module: "pl.LightningModule", stage: Optional[str] = None) -> None:
        if not trainer.logger:
            raise MisconfigurationException(
                "Cannot use NetworkAndDiskStatsMonitor callback with Trainer that has no logger."
            )

    def on_train_epoch_start(self, trainer: "pl.Trainer", pl_module: "pl.LightningModule") -> None:
        self._net_meter: Any[NetworkMetrics, None] = None
        self._disk_meter: Any[DiskMetrics, None] = None

    def _get_new_logs(self) -> Dict[str, float]:
        new_logs: Dict[str, float] = {}

        if self._settings.track_network_utilization:
            if not hasattr(self, "_net_meter") or self._net_meter is None:
                self._net_meter = NetworkMetrics()
            self._net_meter.update_stats()
            new_logs[LOG_KEY_NETW_BYTES_RECV] = float(self._net_meter.mb_recv_ps.val)
            new_logs[LOG_KEY_NETW_BYTES_SENT] = float(self._net_meter.mb_sent_ps.val)

        if self._settings.track_disk_utilization:
            if not hasattr(self, "_disk_meter") or self._disk_meter is None:
                self._disk_meter = DiskMetrics()
            self._disk_meter.update_stats()
            new_logs[LOG_KEY_DISK_UTIL] = float(self._disk_meter.io_util.val)
            new_logs[LOG_KEY_DISK_MB_READ] = float(self._disk_meter.mb_read.val)
            new_logs[LOG_KEY_DISK_MB_WRIT] = float(self._disk_meter.mb_writ.val)
            new_logs[LOG_KEY_DISK_IO_READ] = float(self._disk_meter.io_read.val)
            new_logs[LOG_KEY_DISK_IO_WRIT] = float(self._disk_meter.io_writ.val)
            new_logs[LOG_KEY_DISK_IO_WAIT] = float(self._disk_meter.io_wait.val)

        return new_logs

    @rank_zero_only
    def on_train_batch_start(
        self,
        trainer: "pl.Trainer",
        pl_module: "pl.LightningModule",
        batch: Any,
        batch_idx: int,
        dataloader_idx: int,
    ) -> None:
        if not self._should_log(trainer):
            return

        logs: Dict[str, float] = self._get_new_logs()

        trainer.logger.log_metrics(logs, step=trainer.global_step)

    @rank_zero_only
    def on_train_batch_end(
        self,
        trainer: "pl.Trainer",
        pl_module: "pl.LightningModule",
        outputs: STEP_OUTPUT,
        batch: Any,
        batch_idx: int,
        dataloader_idx: int,
    ) -> None:
        if not self._should_log(trainer):
            return

        logs: Dict[str, float] = self._get_new_logs()

        trainer.logger.log_metrics(logs, step=trainer.global_step)

    @staticmethod
    def _should_log(trainer: "pl.Trainer") -> bool:
        modulo_result: bool = (trainer.global_step + 1) % trainer.log_every_n_steps == 0

        return modulo_result or trainer.should_stop


# `__all__` is left here for documentation purposes and as a
# reference to which interfaces are meant to be imported.
__all__ = [
    "NetworkAndDiskStatsMonitor",
    "LOG_KEY_NETW_BYTES_RECV",
    "LOG_KEY_NETW_BYTES_SENT",
    "LOG_KEY_DISK_UTIL",
    "LOG_KEY_DISK_MB_READ",
    "LOG_KEY_DISK_MB_WRIT",
    "LOG_KEY_DISK_IO_READ",
    "LOG_KEY_DISK_IO_WRIT",
]
