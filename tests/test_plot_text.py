"""Check the bundled Chinese font and labels that used to overflow diagrams."""
from pathlib import Path
import re
import unittest
import warnings

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.ft2font import FT2Font
from matplotlib.backend_bases import FigureCanvasBase
from io import BytesIO

import schematics as S


class PlotTextTests(unittest.TestCase):
    def test_base_canvas_after_hot_reload_can_measure_and_export_png(self):
        fig = S.fig_two_waves(150)
        try:
            FigureCanvasBase(fig)
            S.prepare_figure(fig)
            output = BytesIO()
            fig.savefig(output, format='png')
            self.assertTrue(output.getvalue().startswith(b'\x89PNG'))
        finally:
            plt.close(fig)

    def test_all_chinese_characters_have_glyphs_in_bundled_font(self):
        root = Path(__file__).resolve().parents[1]
        source = "".join((root / name).read_text() for name in ["app.py", "app_common.py", "schematics.py", "optics.py"])
        characters = set(re.findall(r"[\u3400-\u9fff]", source))
        glyphs = FT2Font(str(S.FONT_PATH)).get_charmap()
        self.assertEqual(sorted(char for char in characters if ord(char) not in glyphs), [])
        resolved = font_manager.findfont(font_manager.FontProperties(family=S.FONT_FAMILY))
        self.assertEqual(Path(resolved).resolve(), S.FONT_PATH.resolve())
        self.assertEqual(S.FONT_FAMILY, "Noto Serif CJK SC")

    def test_long_chinese_titles_fit_and_render_without_missing_glyphs(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            for make in [S.fig_contrast_cartoon, S.fig_bracewell_setup, S.fig_xarray_combiner, S.fig_single_telescope_blur]:
                with self.subTest(figure=make.__name__):
                    fig = make()
                    try:
                        S.prepare_figure(fig)
                        fig.canvas.draw()
                        renderer = fig.canvas.get_renderer()
                        for ax in fig.axes:
                            if ax.title.get_text():
                                self.assertLessEqual(ax.title.get_window_extent(renderer).width,
                                                     ax.get_window_extent(renderer).width + 2)
                    finally:
                        plt.close(fig)
            self.assertEqual([str(w.message) for w in caught if "Glyph" in str(w.message)], [])


if __name__ == "__main__":
    unittest.main()
