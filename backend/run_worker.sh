#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

"$SCRIPT_DIR/.venv/bin/python" -m backend.worker


