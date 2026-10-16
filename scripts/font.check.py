"""Test the converter with synthetic artwork; no publisher assets are needed."""
import io
import base64
import xml.etree.ElementTree as ET
import tempfile
import unittest
from pathlib import Path
from PIL import Image, ImageDraw
from fontTools.ttLib import TTFont
import importlib.util
import json

spec = importlib.util.spec_from_file_location("font_builder", Path(__file__).with_name("build-font.py"))
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

class FontTests(unittest.TestCase):
    def test_color_pixels_codepoints_rights_and_reproducible_font(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            inputs = root / "input"
            inputs.mkdir()
            codepoints = json.loads((builder.ROOT / "codepoints.json").read_text())
            expected = {}
            for i, name in enumerate(codepoints):
                image = Image.new("RGBA", (80, 96), (0, 0, 0, 0))
                ImageDraw.Draw(image).rectangle((8, 8, 72, 88), fill=(25 + i * 40, 140, 200, 255))
                image.save(inputs / f"{name}.png")
                image.thumbnail((builder.PPEM, builder.PPEM), Image.Resampling.LANCZOS)
                expected[name] = image
            builder.build_font(inputs, root / "first")
            builder.build_font(inputs, root / "second")
            first = (root / "first/swu-symbols.woff2").read_bytes()
            self.assertEqual(first[:4], b"wOF2")
            self.assertEqual(first, (root / "second/swu-symbols.woff2").read_bytes())
            font = TTFont(root / "first/swu-symbols.woff2")
            self.assertEqual({cp: font.getBestCmap()[cp] for cp in codepoints.values()}, {cp: name for name, cp in codepoints.items()})
            for name, original in expected.items():
                sbix = font["sbix"].strikes[builder.PPEM].glyphs[name].imageData
                cbdt = font["CBDT"].strikeData[0][name].imageData
                svg = font["SVG "].docList[list(codepoints).index(name)].data
                embedded_image = ET.fromstring(svg).find(".//{http://www.w3.org/2000/svg}image")
                svg_png = base64.b64decode(embedded_image.attrib["{http://www.w3.org/1999/xlink}href"].split(",", 1)[1])
                self.assertEqual(sbix, svg_png)
                self.assertEqual(sbix, cbdt)
                embedded = Image.open(io.BytesIO(sbix)).convert("RGBA")
                self.assertEqual(embedded.size, original.size)
                self.assertEqual(embedded.tobytes(), original.tobytes())
            self.assertIn("No artwork license is granted", font["name"].getDebugName(13))

    def test_release_font_version_glyph_coverage_and_size_budget(self):
        package = json.loads((builder.ROOT / "package.json").read_text())
        codepoints = json.loads((builder.ROOT / "codepoints.json").read_text())
        path = builder.ROOT / "dist/swu-symbols.woff2"
        self.assertLess(path.stat().st_size, 100 * 1024)
        font = TTFont(path)
        self.assertEqual(font["name"].getDebugName(5), f"Version {package['version']}")
        self.assertEqual({cp: font.getBestCmap()[cp] for cp in codepoints.values()}, {cp: name for name, cp in codepoints.items()})
        self.assertIn("No artwork license is granted", font["name"].getDebugName(13))
        for name in codepoints:
            self.assertGreater(len(font["sbix"].strikes[builder.PPEM].glyphs[name].imageData), 0)
        self.assertTrue((builder.ROOT / "dist/swu-symbols.ttf").is_file())

if __name__ == "__main__":
    unittest.main()
