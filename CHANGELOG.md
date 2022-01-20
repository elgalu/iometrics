# CHANGELOG

## 0.0.8 - [2022-01-20]

### Added

* Add dummy CLI with `iometrics start` and `iometrics replicate proc`  [#cli]

## 0.0.7 - [2021-09-26]

### Added in 0.0.7

* Add TRACK_METRICS_INTERVAL_SECS=10 to track metrics less often  [#TRACK_METRICS_INTERVAL_SECS]

## 0.0.6 - [2021-09-26]

### Added in 0.0.6

* Add "disk/io_wait%" for Disks I/O percentage of time that the CPU is waiting.  [#io_wait]
* Add support for Python 3.7  [#py37]

## 0.0.5 - [2021-09-24]

### Fixed in 0.0.5

* Devices like AWS EBS or USB drives can get dynamically detached so validate key  [#detach]

### Added in 0.0.5

* Add support for Python 3.7  [#py37]

## 0.0.4 - [2021-08-18]

### Fixed in 0.0.4

* Fix bug in PyTorch-Lightning integration  [#PyTorch-Lightning]

## 0.0.3 - [2021-08-17]

### Fixed in 0.0.3

* Fix PyTorch-Lightning integration.  [#PyTorch-Lightning]

## 0.0.2 - [2021-08-15]

### Added on 0.0.2

* Add PyTorch-Lightning support via
`from iometrics.pytorch_lightning.callbacks import NetworkAndDiskStatsMonitor` [#PyTorch-Lightning]

## 0.0.1 - [2021-08-14]

### Added on 0.0.1

* Initial setup release that also tests [tbump](https://github.com/dmerejkowsky/tbump)
  and [towncrier](https://github.com/twisted/towncrier)  [#initial_setup]
