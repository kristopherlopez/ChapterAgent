"""Launch MLflow UI on Windows.

Usage:
    python -u run_mlflow_ui.py
"""

import os
import sys
from pathlib import Path

sys.stdout.reconfigure(line_buffering=True)

# Find the project root (contains pyproject.toml) — all MLflow data lives there
project_root = Path(__file__).parent
for _ in range(10):
    if (project_root / "pyproject.toml").exists():
        break
    project_root = project_root.parent

db_path = project_root / "mlflow.db"

if not db_path.exists():
    print(f"ERROR: mlflow.db not found at {db_path}")
    print("Run the ablation study first: python src/ablation.py")
    sys.exit(1)

backend_uri = f"sqlite:///{db_path.resolve().as_posix()}"
artifact_root = str((project_root / "mlartifacts").resolve())

HOST = "127.0.0.1"
PORT = 5000

print(f"MLflow UI starting on http://{HOST}:{PORT}", flush=True)
print(f"Backend: {backend_uri}", flush=True)
print(f"Press Ctrl+C to stop.\n", flush=True)

from mlflow.server import _run_server

_run_server(
    file_store_path=backend_uri,
    registry_store_uri=backend_uri,
    default_artifact_root=artifact_root,
    serve_artifacts=False,
    artifacts_only=False,
    artifacts_destination=None,
    host=HOST,
    port=PORT,
)
