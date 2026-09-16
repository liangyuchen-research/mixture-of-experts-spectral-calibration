"""Convert spectrometer records into background-corrected replicate tables."""

import argparse
import json
from pathlib import Path

from measurement_processing import process_directory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_directory", type=Path, help="Folder of raw .txt detector records")
    parser.add_argument(
        "--output", type=Path, required=True, help="New output folder outside the input folder"
    )
    args = parser.parse_args()
    summary = process_directory(args.input_directory, args.output)
    print(json.dumps({"rows_written": summary}, indent=2))


if __name__ == "__main__":
    main()
