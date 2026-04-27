#!/bin/bash
# Python execution helper - prevents terminal hanging
# Usage: ./scripts/run-python.sh <script.py> [args...]

set -e

SCRIPT="$1"
shift

# Change to backend directory if script is in backend
if [[ "$SCRIPT" == backend/* ]] || [[ "$SCRIPT" == *services/* ]]; then
    cd backend
    SCRIPT="${SCRIPT#backend/}"
fi

# Activate virtual environment
if [ -d "venv/bin" ]; then
    source venv/bin/activate
fi

# Run with unbuffered output
python3 -u "$SCRIPT" "$@"
exit $?
