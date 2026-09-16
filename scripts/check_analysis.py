"""Exercise detector processing and calibration on analytically known examples."""

import hashlib
from pathlib import Path
import tempfile
import unittest

import numpy as np
import pandas as pd

from measurement_processing import process_directory
from calibrate_matrix_condition import calibrate, corrected_intensity

ROOT = Path(__file__).resolve().parents[1]


class AnalysisChecks(unittest.TestCase):
    def test_replicates_and_source_preservation(self):
        columns = pd.read_csv(
            ROOT / "data/examples/sodium_matrix_mean_spectra.csv", nrows=0
        ).columns
        wavelengths = []
        for value in columns:
            try:
                float(value)
                wavelengths.append(value)
            except ValueError:
                continue
        self.assertEqual(len(wavelengths), 1948)
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source = base / "raw"
            source.mkdir()
            for index in range(11):
                path = source / f"{index:04d}_1000_10_20_5_3000_Conc-3_Na-0_Ca-0_K-0_Mg-0.txt"
                path.write_text(
                    "\n".join(f"{w}\t{10 + index}" for w in wavelengths), encoding="utf-8"
                )
            before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in source.iterdir()}
            result = process_directory(source, base / "output")
            self.assertEqual(
                result,
                {"Concat.csv": 10, "Mean.csv": 1, "STD.csv": 1, "RSD.csv": 1, "Mean_3.csv": 3},
            )
            mean = pd.read_csv(base / "output/Mean.csv")
            std = pd.read_csv(base / "output/STD.csv")
            triples = pd.read_csv(base / "output/Mean_3.csv")
            self.assertAlmostEqual(mean[wavelengths[0]].iloc[0], 5.5)
            self.assertAlmostEqual(std[wavelengths[0]].iloc[0], np.std(np.arange(1, 11), ddof=1))
            np.testing.assert_allclose(triples[wavelengths[0]], [2, 5, 8])
            self.assertEqual(
                before,
                {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in source.iterdir()},
            )
            with self.assertRaises(FileExistsError):
                process_directory(source, base / "output")
            with self.assertRaises(ValueError):
                process_directory(source, source / "output")
            (source / "extra.txt").write_text("", encoding="utf-8")
            with self.assertRaises(ValueError):
                process_directory(source, base / "incomplete-output")

    def test_calibration_and_invalid_references(self):
        def frame(concentration):
            concentration = np.asarray(concentration, dtype=float)
            return pd.DataFrame(
                {
                    "Cu": concentration,
                    "Na": 0,
                    "Ca": 0,
                    "K": 0,
                    "Mg": 0,
                    "327.239": 10,
                    "327.591": 13 + 2 * concentration,
                    "328.469": 10,
                }
            )

        training = frame([0, 1, 2, 3])
        testing = frame([3, 5])
        testing["Cu"] *= 10
        summary, predictions = calibrate(training, "Cu", [0, 0, 0, 0], testing=testing)
        self.assertAlmostEqual(summary["slope"], 2)
        self.assertAlmostEqual(summary["intercept"], 3)
        np.testing.assert_allclose(predictions["predicted_ppm"], [3, 5])
        np.testing.assert_allclose(predictions["nominal_ppm"], [3, 5])
        with self.assertRaises(ValueError):
            calibrate(training, "Cu", [999, 0, 0, 0])
        training["327.591"] = 10
        with self.assertRaises(ValueError):
            calibrate(training, "Cu", [0, 0, 0, 0])
        training["327.239"] = 0
        with self.assertRaises(ValueError):
            corrected_intensity(training, "Cu", normalization="cu")


if __name__ == "__main__":
    unittest.main()
