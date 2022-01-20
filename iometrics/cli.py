#!/usr/bin/env python3
"""
## Command Line Interface.

:license: Apache 2.0, see LICENSE for more details.
"""
import os
import sys
from time import sleep

from iometrics.example import usage as print_metrics_live


def show_help() -> None:
    """Show CLI help and capabilities."""
    print("Available commands:")
    print("iometrics start")
    print("iometrics replicate proc")


def iometrics_cli_entrypoint() -> None:
    """Entrypoint for the `iometrics` executable."""
    if len(sys.argv) < 2:
        show_help()
        sys.exit()

    if sys.argv[1] == "start" and len(sys.argv) == 2:
        cmd_print_metrics_live()
    elif sys.argv[1] == "replicate" and sys.argv[2] == "proc" and len(sys.argv) == 3:
        cmd_replicate_proc_net_dev()


def cmd_replicate_proc_net_dev() -> None:
    """Replicate the host dev file to another place in order to read it from a container."""
    while True:
        os.system("cat /proc/net/dev > /tmp/proc_net_dev")
        sleep(0.5)


def cmd_print_metrics_live() -> None:
    """Show CLI help and capabilities."""
    print_metrics_live()
