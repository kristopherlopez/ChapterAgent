"""Launch MLflow UI on Windows.

Usage:
    python -u run_mlflow_ui.py
"""

import os
import sys
from pathlib import Path

sys.stdout.reconfigure(line_buffering=True)

solution_dir = Path(__file__).parent
db_path = solution_dir / "mlflow.db"

if not db_path.exists():
    print(f"ERROR: mlflow.db not found at {db_path}")
    print("Run the ablation study first: python src/ablation.py")
    sys.exit(1)

backend_uri = f"sqlite:///{db_path.resolve().as_posix()}"
artifact_root = str((solution_dir / "mlartifacts").resolve())

HOST = "127.0.0.1"
PORT = 5001

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
