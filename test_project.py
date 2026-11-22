import unittest
from project import analyze


def sheet(x):
    return {"width": 10, "height": 10, "frames": [{"name": "a", "x": 0, "y": 0, "w": 5, "h": 10}, {"name": "b", "x": x, "y": 0, "w": 5, "h": 10}]}


class AtlasTests(unittest.TestCase):
    def test_edges_are_safe(self):
        self.assertEqual(analyze(sheet(5))["metrics"]["Overlap pairs"], 0)

    def test_union_and_clipping(self):
        self.assertEqual(analyze(sheet(4))["metrics"]["Sheet occupancy"], "90.0%")
        self.assertIn("clipped", analyze(sheet(8))["rows"][1]["Finding"])

    def test_duplicate(self):
        data = sheet(5)
        data["frames"][1]["name"] = "a"
        with self.assertRaises(ValueError):
            analyze(data)
