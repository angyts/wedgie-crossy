"""Shared camera parity vectors used by the no_std Rust crate."""
import csv
from pathlib import Path
import unittest
from crossy_core.camera import Camera

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "camera_parity.csv"

class CameraParityTests(unittest.TestCase):
    def test_shared_camera_vectors(self):
        with FIXTURE.open(newline="") as stream:
            cases = [row for row in csv.reader(stream)
                     if row and not row[0].startswith("#")]
        self.assertEqual(len(cases), 4)
        for grace, interval, initial, rows, deaths, boundaries in cases:
            cam = Camera(int(grace), int(interval), int(initial))
            actual_deaths = []
            actual_boundaries = []
            for tick, row in enumerate(map(int, rows.split(":")), 1):
                actual_deaths.append(int(cam.update(row, tick)))
                actual_boundaries.append(cam.boundary)
            self.assertEqual(actual_deaths, list(map(int, deaths.split(":"))))
            self.assertEqual(actual_boundaries, list(map(int, boundaries.split(":"))))

if __name__ == "__main__":
    unittest.main()
