"""Vehicle art stays within the original tile and does not change physics."""
import importlib.util
import pathlib
import sys
import types
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class VehicleArtTests(unittest.TestCase):
    def test_four_silhouettes_and_bounded_draws(self):
        fake = types.ModuleType("lcd")
        fake.LCD = object
        fake.Keys = object
        fake.color = lambda r, g, b: (r, g, b)
        old = sys.modules.get("lcd")
        sys.modules["lcd"] = fake
        sys.path.insert(0, str(ROOT))
        try:
            spec = importlib.util.spec_from_file_location(
                "crossy_vehicle_art", ROOT / "crossy.py")
            m = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)

            class Screen:
                def __init__(self):
                    self.rects = []

                def fill_rect(self, x, y, w, h, ink):
                    assert w > 0 and h > 0
                    assert 0 <= x and x + w <= 20
                    assert 0 <= y and y + h <= 20
                    self.rects.append((x, y, w, h))

            self.assertEqual(set(m.car_style(r) for r in range(0, 48, 12)),
                             {0, 1, 2, 3})
            for row in range(0, 48, 12):
                screen = Screen()
                m.draw_car(screen, 0, 0, row, 0, 123, identity_col=0)
                self.assertTrue(screen.rects)
                self.assertLessEqual(m.car_length(row), 20)
        finally:
            if old is None:
                sys.modules.pop("lcd", None)
            else:
                sys.modules["lcd"] = old
            sys.path.pop(0)


if __name__ == "__main__":
    unittest.main()
