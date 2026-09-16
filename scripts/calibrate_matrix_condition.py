"""Fit and evaluate a metal calibration at a specified Na/Ca/K/Mg condition."""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

PEAKS = {
    "Cu": (327.591, 327.239, 328.469),
    "Ni": (232.280, 230.621, 233.201),
    "Zn": (214.158, 212.859, 215.642),
}
REFERENCES = {"cu": 327.396, "ni236": 236.330, "ni323": 323.546, "zn": 213.856, "hydrogen": 434.331}
ZERO_RANGES = [
    (240.007, 329.873),
    (360.102, 375.499),
    (400.609, 410.415),
    (323.017, 340.015),
    (230.621, 240.007),
    (335.476, 360.102),
    (468.907, 500.126),
]
MATRIX_COLUMNS = ["Na", "Ca", "K", "Mg"]


def spectral_columns(frame):
    columns = []
    for column in frame.columns:
        try:
            float(column)
            columns.append(column)
        except ValueError:
            continue
    wavelength = np.array(columns, dtype=float)
    if len(wavelength) < 3 or not np.isfinite(wavelength).all() or np.any(np.diff(wavelength) <= 0):
        raise ValueError("Expected an increasing numeric wavelength grid.")
    return columns, wavelength


def corrected_intensity(frame, metal, normalization="none", test=False):
    columns, wavelength = spectral_columns(frame)
    data = frame[columns].to_numpy(dtype=float)
    if not len(data) or not np.isfinite(data).all():
        raise ValueError("Spectral intensities must be finite and nonempty.")

    def nearest(value):
        if not wavelength[0] <= value <= wavelength[-1]:
            raise ValueError(f"Required wavelength {value} is outside the measurement grid.")
        return int(np.abs(wavelength - value).argmin())

    if normalization == "area":
        block = data.copy()
        if test:
            limit = min(400, data.shape[1])
            divisor = np.trapz(block[:, :limit], wavelength[:limit], axis=1)
        else:
            for left, right in ZERO_RANGES:
                if wavelength[0] <= left and right <= wavelength[-1]:
                    block[:, nearest(left) : nearest(right) + 1] = 0
            divisor = np.trapz(block, wavelength, axis=1)
    elif normalization in REFERENCES:
        divisor = data[:, nearest(REFERENCES[normalization])]
    elif normalization == "none":
        divisor = np.ones(len(data))
    else:
        raise ValueError(f"Unknown normalization: {normalization}")
    if not np.isfinite(divisor).all() or np.any(divisor == 0):
        raise ValueError("Normalization requires finite, nonzero reference values.")
    data = data / divisor[:, None]
    peak, left, right = PEAKS[metal]
    p, a, b = nearest(peak), nearest(left), nearest(right)
    if a == b:
        raise ValueError("Wavelength resolution cannot resolve both background positions.")
    slope = (data[:, a] - data[:, b]) / (wavelength[a] - wavelength[b])
    intercept = data[:, b] - slope * wavelength[b]
    return data[:, p] - (slope * peak + intercept)


def matrix_rows(frame, condition):
    missing = set(MATRIX_COLUMNS).difference(frame.columns)
    if missing:
        raise ValueError(f"Missing matrix columns: {sorted(missing)}")
    selected = frame.loc[
        (frame[MATRIX_COLUMNS].to_numpy(dtype=float) == np.array(condition)).all(axis=1)
    ]
    if selected.empty:
        raise ValueError("No observations match the requested Na/Ca/K/Mg condition.")
    return selected


def calibrate(training, metal, condition, normalization="none", testing=None, test_scale=10.0):
    train = matrix_rows(training, condition)
    concentration = train[metal].to_numpy(dtype=float)
    if not np.isfinite(concentration).all() or np.unique(concentration).size < 2:
        raise ValueError("Calibration requires finite concentrations at two or more levels.")
    intensity = corrected_intensity(train, metal, normalization)
    model = LinearRegression().fit(concentration[:, None], intensity)
    slope, intercept = float(model.coef_[0]), float(model.intercept_)
    if not np.isfinite(slope) or slope == 0:
        raise ValueError("Cannot invert a zero or nonfinite calibration slope.")
    summary = {
        "metal": metal,
        "matrix": dict(zip(MATRIX_COLUMNS, condition)),
        "normalization": normalization,
        "n_training": len(train),
        "slope": slope,
        "intercept": intercept,
        "training_r2": float(r2_score(intensity, model.predict(concentration[:, None]))),
    }
    predictions = None
    if testing is not None:
        if not np.isfinite(test_scale) or test_scale <= 0:
            raise ValueError("Test concentration divisor must be finite and positive.")
        test = matrix_rows(testing, condition)
        observed = corrected_intensity(test, metal, normalization, test=True)
        predictions = pd.DataFrame(
            {
                "nominal_ppm": test[metal].to_numpy(dtype=float) / test_scale,
                "predicted_ppm": (observed - intercept) / slope,
                "corrected_intensity": observed,
            }
        )
        summary["test_concentration_divisor"] = test_scale
    return summary, predictions


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("training_csv", type=Path)
    parser.add_argument("--metal", choices=PEAKS, required=True)
    parser.add_argument(
        "--matrix", nargs=4, type=float, required=True, metavar=("NA", "CA", "K", "MG")
    )
    parser.add_argument("--normalization", choices=["none", "area", *REFERENCES], default="none")
    parser.add_argument("--testing-csv", type=Path)
    parser.add_argument(
        "--test-concentration-divisor",
        type=float,
        default=10.0,
        help="Original test-label convention divides by 10. Use 1 for labels already in ppm.",
    )
    parser.add_argument("--output", type=Path, required=True, help="New output directory")
    args = parser.parse_args()
    summary, predictions = calibrate(
        pd.read_csv(args.training_csv),
        args.metal,
        args.matrix,
        args.normalization,
        pd.read_csv(args.testing_csv) if args.testing_csv else None,
        args.test_concentration_divisor,
    )
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / "calibration.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    if predictions is not None:
        predictions.to_csv(args.output / "predictions.csv", index=False)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
