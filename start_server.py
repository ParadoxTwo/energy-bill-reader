#!/usr/bin/env python3
"""Startup script for Railway deployment."""
import sys
import os
from pathlib import Path

# Find project root - try multiple possible locations
script_path = Path(__file__).resolve()
possible_roots = [
    script_path.parent,  # Same directory as this script
    Path("/app"),        # Railway's default
    Path(os.getcwd()),   # Current working directory
]

project_root = None
for root in possible_roots:
    if (root / "backend" / "main.py").exists():
        project_root = root
        break

if project_root is None:
    # Fallback: use script's parent directory
    project_root = script_path.parent

# Add project root to Python path
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Debug output
print(f"[start_server.py] Project root: {project_root}", file=sys.stderr, flush=True)
print(f"[start_server.py] Python path: {sys.path[:3]}...", file=sys.stderr, flush=True)
print(f"[start_server.py] Backend exists: {(project_root / 'backend').exists()}", file=sys.stderr, flush=True)

# Now we can import and run uvicorn
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"[start_server.py] Starting uvicorn on port {port}", file=sys.stderr, flush=True)
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

