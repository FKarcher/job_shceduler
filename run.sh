#!/usr/bin/env bash

ENV=$1

CURRENT_DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

exec nohup python3 $CURRENT_DIR/app.py ${ENV}&
