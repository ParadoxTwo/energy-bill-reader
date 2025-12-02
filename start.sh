#!/bin/bash
# Railway typically uses /app as the working directory
# Add it to PYTHONPATH so Python can find the backend module
export PYTHONPATH="/app:${PYTHONPATH}"

# Try multiple possible working directories
for dir in /app /workspace "$(pwd)"; do
  if [ -d "$dir/backend" ]; then
    cd "$dir" || exit 1
    break
  fi
done

# Run uvicorn
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port "${PORT:-8000}"

