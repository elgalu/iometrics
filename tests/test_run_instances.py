import time
from iometrics import NetworkMetrics, DiskMetrics, DUAL_METRICS_HEADER


def test_all_metrics() -> None:
    net  = NetworkMetrics()
    disk = DiskMetrics()
    for i in range(1):
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
            f"| {int(disk.io_read.val):4d} | {int(disk.io_read.avg):4d} "
            f"| {int(disk.io_writ.val):3d} | {int(disk.io_writ.avg):3d} "
            f"|"
        )
        assert "0.0" in row
