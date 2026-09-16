"""Copy documented artifacts from a private archive without overwriting files."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def contained(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"Artifact path escapes the selected root: {relative}")
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive-root", type=Path, required=True)
    parser.add_argument("--destination", type=Path, default=ROOT / "data" / "local")
    parser.add_argument("--verify-only", action="store_true", help="Verify archive files without copying.")
    args = parser.parse_args()
    archive = args.archive_root.resolve(strict=True)
    destination = args.destination.resolve()
    if destination == archive or destination.is_relative_to(archive):
        parser.error("Choose a destination outside the private archive.")
    manifest = json.loads((ROOT / "data" / "external_artifacts.json").read_text(encoding="utf-8"))
    copied = verified = 0
    failures = []
    for entry in manifest:
        try:
            source = contained(archive, entry["archive_relative_path"])
            target = contained(destination, entry["destination"])
            if not source.is_file() or sha256(source) != entry["sha256"]:
                raise ValueError("Source missing or SHA-256 differs from the archive inventory.")
            verified += 1
            if args.verify_only:
                continue
            if target.exists():
                if not target.is_file() or sha256(target) != entry["sha256"]:
                    raise FileExistsError("Destination exists with different content; left untouched.")
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            # Exclusive creation protects against replacing a file created by another process.
            with source.open("rb") as original, target.open("xb") as output:
                shutil.copyfileobj(original, output, 8 * 1024 * 1024)
            if sha256(target) != entry["sha256"]:
                raise ValueError("Copy checksum mismatch; partial file retained for inspection.")
            copied += 1
        except Exception as error:
            failures.append({"artifact": entry["destination"], "error": str(error)})
    print(json.dumps({"verified": verified, "copied": copied, "failures": failures}, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
