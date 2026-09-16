"""Create isolated output folders for optional analysis scripts."""

from datetime import datetime, timezone
import os
from pathlib import Path
import re
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]


def create_output_directory(name):
    if not re.fullmatch(r"[a-z0-9_-]+", name):
        raise ValueError(
            "Use a lowercase experiment name containing letters, numbers, underscores, or hyphens."
        )
    output_root = Path(os.environ.get("MOE_OUTPUT_DIR", ROOT / "results")).expanduser().resolve()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = output_root / f"{name}_{stamp}_{uuid4().hex[:8]}"
    path.mkdir(parents=True, exist_ok=False)
    return path
