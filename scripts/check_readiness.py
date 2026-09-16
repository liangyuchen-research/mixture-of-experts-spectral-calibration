"""Report runtime availability without importing TensorFlow or starting training."""

import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    sys.path.insert(0, str(ROOT / "src"))
    modules = ["spice_moe", "numpy", "pandas", "h5py", "tensorflow", "nbformat", "nbclient"]
    result = {name: importlib.util.find_spec(name) is not None for name in modules}
    print(json.dumps({"modules": result, "training_ready": all(result.values())}, indent=2))
    if not all(result.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
