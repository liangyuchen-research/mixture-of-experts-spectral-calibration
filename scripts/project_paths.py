"""Configure isolated experiment outputs without changing archived measurements."""

from datetime import datetime, timezone
import importlib.util
import os
from pathlib import Path
import re
import shutil
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]


def create_output_directory(name):
    """Create a fresh directory for the standalone measurement-analysis scripts."""
    if not re.fullmatch(r"[a-z0-9_-]+", name):
        raise ValueError("Use a lowercase experiment name with letters, numbers, underscores, or hyphens.")
    output_root = Path(os.environ.get("MOE_OUTPUT_DIR", ROOT / "results")).resolve()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = output_root / f"{name}_{stamp}_{uuid4().hex[:8]}"
    path.mkdir(parents=True, exist_ok=False)
    print(f"Output directory: {path}")
    return path


def configure_run(new=False):
    """Prepare writable copies of datasets/checkpoints for a shared staged run.

    The missing runtime is checked before creating or copying any run artifacts.
    A notebook runner shares MOE_RUN_DIR with its child kernels so all stages use
    the same prepared data and preceding-stage checkpoints.
    """
    if importlib.util.find_spec("spice_moe") is None:
        raise ModuleNotFoundError(
            "The original spice_moe.py is missing from this research snapshot. "
            "Recover the matching version into src/ before running these notebooks. "
            "The standalone scripts and archived result tables remain usable."
        )
    data = Path(os.environ.get("MOE_DATA_DIR", ROOT / "data" / "local")).resolve()
    if new or "MOE_RUN_DIR" not in os.environ:
        run = create_output_directory("staged_calibration")
    else:
        run = Path(os.environ["MOE_RUN_DIR"]).resolve()
        if not run.is_dir():
            raise FileNotFoundError(f"Shared experiment directory does not exist: {run}")
    if run == data or run.is_relative_to(data):
        raise ValueError("The experiment directory must be separate from the input data directory.")
    os.environ["MOE_PROJECT_ROOT"] = str(ROOT)
    os.environ["MOE_RUN_DIR"] = str(run)
    for original, local in (("ML dataset", "prepared"), ("checkpoints_v6", "checkpoints")):
        source, target = data / original, run / local
        if target.exists():
            continue
        if source.is_dir():
            if any(p.is_symlink() or getattr(p, "is_junction", lambda: False)() for p in source.rglob("*")):
                raise ValueError(f"Links in runtime input are not copied automatically: {source}")
            shutil.copytree(source, target)
        else:
            target.mkdir(parents=True)
    os.chdir(run)
    print(f"Input measurements: {data}")
    print(f"Experiment directory: {run}")
    return data, run, run / "prepared", run / "checkpoints"
