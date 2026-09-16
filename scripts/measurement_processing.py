"""Background subtraction and replicate aggregation for spectrometer exports."""

from pathlib import Path

import numpy as np
import pandas as pd

CONDITIONS = [
    "Voltage",
    "Ontime",
    "Offtime",
    "Cycle",
    "Conductivity",
    "Cu",
    "Ni",
    "Zn",
    "Na",
    "Ca",
    "K",
    "Mg",
]
PEAKS = {
    "Pb-368nm": ("368.972", "367.942", "369.659"),
    "Pb-406nm": ("406.410", "405.240", "407.245"),
    "Zn-214nm": ("214.547", "212.501", "216.777"),
    "Ni-232nm": ("232.704", "230.857", "234.180"),
    "Cu-327nm": ("328.079", "326.669", "328.784"),
}


def subtract_linear_background(frame):
    """Add the original two-point baseline and net-intensity columns."""
    result = frame.copy()
    for name, (peak, left, right) in PEAKS.items():
        missing = {peak, left, right}.difference(result.columns)
        if missing:
            raise ValueError(f"Missing wavelength columns for {name}: {sorted(missing)}")
        slope = (result[left] - result[right]) / (float(left) - float(right))
        intercept = result[right] - slope * float(right)
        result[name + "_slope"] = slope
        result[name + "_intercept"] = intercept
        result[name + "_background"] = slope * float(peak) + intercept
        result[name + "_predict"] = result[peak] - result[name + "_background"]
    return result


def read_record(path, pixels=1948):
    """Read detector rows and reject malformed or nonfinite records."""
    lines = Path(path).read_text(encoding="utf-8-sig").splitlines()
    if len(lines) < pixels:
        raise ValueError(f"{Path(path).name}: expected at least {pixels} detector rows")
    fields = [line.split("\t") for line in lines[:pixels]]
    if any(len(row) < 2 for row in fields):
        raise ValueError(f"{Path(path).name}: expected tab-separated wavelength and intensity")
    wavelength = [row[0].strip() for row in fields]
    values = np.array([float(row[1]) for row in fields])
    grid = np.array([float(value) for value in wavelength])
    if not np.isfinite(values).all() or not np.isfinite(grid).all() or np.any(np.diff(grid) <= 0):
        raise ValueError(f"{Path(path).name}: invalid intensity or wavelength grid")
    return wavelength, values


def parse_conditions(path):
    parts = Path(path).stem.split("_")
    if len(parts) != 11:
        raise ValueError(f"{Path(path).name}: expected 11 underscore-separated acquisition fields")
    values = [float(value) for value in parts[1:6]]
    concentrations = [float(value.split("-", 1)[1]) for value in parts[6:11]]
    values += [concentrations[0]] * 3 + concentrations[1:]
    if not np.isfinite(values).all():
        raise ValueError(f"{Path(path).name}: nonfinite acquisition condition")
    return [parts[0], *values]


def read_measurements(directory):
    """Read sorted groups of one background and ten signal files."""
    paths = sorted(Path(directory).glob("*.txt"))
    if not paths or len(paths) % 11:
        raise ValueError(
            "Raw input must contain complete groups of one background and ten signal files."
        )
    wavelength, _ = read_record(paths[0])
    conditions, spectra = [], []
    for start in range(0, len(paths), 11):
        background_grid, background = read_record(paths[start])
        if background_grid != wavelength:
            raise ValueError(f"Wavelength grid differs in {paths[start].name}")
        for path in paths[start + 1 : start + 11]:
            grid, intensity = read_record(path)
            if grid != wavelength:
                raise ValueError(f"Wavelength grid differs in {path.name}")
            conditions.append(parse_conditions(path))
            spectra.append(intensity - background)
    metadata = pd.DataFrame(conditions, columns=["Time", *CONDITIONS])
    metadata["Total_on_time"] = metadata["Ontime"] * metadata["Cycle"]
    signals = pd.DataFrame(spectra, columns=wavelength)
    return pd.concat([metadata, subtract_linear_background(signals)], axis=1), wavelength


def aggregate_measurements(frame, wavelength):
    """Group observed conditions directly and retain sample standard deviations."""
    missing = set(CONDITIONS + wavelength).difference(frame.columns)
    if missing:
        raise ValueError(f"Missing acquisition columns: {sorted(missing)}")
    values = frame[CONDITIONS + wavelength].to_numpy(dtype=float)
    if not len(frame) or not np.isfinite(values).all():
        raise ValueError("Measurements must contain finite conditions and spectra.")
    grouped = frame.groupby(CONDITIONS, sort=True, dropna=False)[wavelength]
    mean = grouped.mean()
    std = grouped.std(ddof=1)
    rsd = std.divide(mean.where(mean != 0)).multiply(100)
    triples = []
    for condition, rows in frame.groupby(CONDITIONS, sort=True, dropna=False):
        for start in range(0, len(rows) - 2, 3):
            triples.append([*condition, *rows.iloc[start : start + 3][wavelength].mean()])
    mean3 = pd.DataFrame(triples, columns=CONDITIONS + wavelength)
    return {
        "Mean.csv": subtract_linear_background(mean.reset_index()),
        "STD.csv": std.reset_index(),
        "RSD.csv": rsd.reset_index(),
        "Mean_3.csv": subtract_linear_background(mean3),
    }


def process_directory(source, destination):
    """Write derived tables to a new directory, never into the source folder."""
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if source == destination or destination.is_relative_to(source):
        raise ValueError("Choose an output directory outside the measurement directory.")
    frame, wavelength = read_measurements(source)
    tables = {"Concat.csv": frame, **aggregate_measurements(frame, wavelength)}
    destination.mkdir(parents=True, exist_ok=False)
    for name, table in tables.items():
        table.to_csv(destination / name)
    return {name: len(table) for name, table in tables.items()}
