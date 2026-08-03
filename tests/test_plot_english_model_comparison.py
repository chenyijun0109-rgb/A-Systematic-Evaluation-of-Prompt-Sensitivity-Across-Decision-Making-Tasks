import tempfile
import unittest
from pathlib import Path

import matplotlib.pyplot as plt

from src.plot_english_model_comparison import save_figure


class PlotEnglishModelComparisonTests(unittest.TestCase):
    def test_save_figure_writes_png_and_pdf(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fig, ax = plt.subplots()
            ax.plot([0, 1], [0, 1])
            paths = save_figure(fig, Path(tmpdir), "test_figure")
            self.assertEqual(len(paths), 2)
            self.assertTrue((Path(tmpdir) / "test_figure.png").exists())
            self.assertTrue((Path(tmpdir) / "test_figure.pdf").exists())


if __name__ == "__main__":
    unittest.main()
