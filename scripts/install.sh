#!/usr/bin/env bash


# set -e: exit asap if a command exits with a non-zero status
set -e

# set -o pipefail: Don't mask errors from a command piped into another command
set -o pipefail

# set -u: treat unset variables as an error and exit immediately
set -u

# set -x: prints all lines before running debug (debugging)
set -x

pip install poetry
