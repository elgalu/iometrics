# CHANGELOG

## 0.0.5 - [2021-09-24]

### Added

* Add support for Python 3.7  [#py37]

### Fixed

* Devices like AWS EBS or USB drives can get dynamically detached so validate key  [#detach]

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
