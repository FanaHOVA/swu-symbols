"""Build a bitmap color WOFF2 from locally supplied aspect PNGs. MIT code only.

Input artwork is never downloaded by this tool. Supply files you have rights to
use; conversion does not grant permission to redistribute the resulting font.
"""
import argparse
import base64
import io
import json
from pathlib import Path

from PIL import Image
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import newTable
from fontTools.ttLib.tables.BitmapGlyphMetrics import SmallGlyphMetrics
from fontTools.ttLib.tables.C_B_D_T_ import cbdt_bitmap_format_17
from fontTools.ttLib.tables.E_B_L_C_ import Strike as BitmapStrike, SbitLineMetrics, eblc_index_sub_table_1
from fontTools.ttLib.tables.sbixGlyph import Glyph
from fontTools.ttLib.tables.sbixStrike import Strike

ROOT = Path(__file__).resolve().parent.parent
PPEM = 64  # Supports 16px at 4x density and 32px at 2x; signed metrics fit int8.
UNITS = 1024
TIMESTAMP = 3853958400  # Fixed OpenType timestamp, for reproducible output.


def build_font(input_dir: Path, output_dir: Path):
    codepoints = json.loads((ROOT / "codepoints.json").read_text())
    version = json.loads((ROOT / "package.json").read_text())["version"]
    order = [".notdef", "space", *codepoints]
    builder = FontBuilder(UNITS, isTTF=True)
    builder.setupGlyphOrder(order)
    builder.setupCharacterMap({32: "space", **{cp: name for name, cp in codepoints.items()}})
    outlines = {name: TTGlyphPen(None).glyph() for name in order}
    # A non-empty .notdef keeps the TrueType glyf table valid for browser OTS.
    missing = TTGlyphPen(None)
    missing.moveTo((128, 0))
    missing.lineTo((896, 0))
    missing.lineTo((896, UNITS))
    missing.lineTo((128, UNITS))
    missing.closePath()
    outlines[".notdef"] = missing.glyph()
    builder.setupGlyf(outlines)
    builder.setupHorizontalMetrics({name: (UNITS, 0) for name in order})
    builder.setupHorizontalHeader(ascent=UNITS, descent=0)
    builder.setupOS2(sTypoAscender=UNITS, sTypoDescender=0, sTypoLineGap=0,
                     usWinAscent=UNITS, usWinDescent=0, fsType=2, fsSelection=0xC0, version=4)
    builder.setupNameTable({
        "familyName": "SWU Symbols Color", "styleName": "Regular",
        "uniqueFontIdentifier": f"SWU Symbols Color {version}", "fullName": "SWU Symbols Color",
        "psName": "SWUSymbolsColor-Regular", "version": f"Version {version}",
        "copyright": "Original artwork: Lucasfilm Ltd. / Fantasy Flight Games; all artwork rights reserved to their respective owners. Unofficial font packaging.",
        "licenseDescription": "Conversion code is MIT. No artwork license is granted by this font. Publisher terms and any separately obtained permission govern use and redistribution of the artwork.",
        "licenseInfoURL": "https://starwarsunlimited.com/media-kit",
    })
    builder.setupPost()
    font = builder.font
    font.recalcTimestamp = False
    font["head"].created = font["head"].modified = TIMESTAMP
    font["head"].xMin = font["head"].yMin = 0
    font["head"].xMax = font["head"].yMax = UNITS

    # Bitmap encodings for Apple/Chromium; the OpenType-SVG fallback below
    # covers Firefox. All embed identical resized pixels; nothing is traced.
    sbix = newTable("sbix")
    strike = Strike(ppem=PPEM, resolution=72)
    bitmap_data = {}
    for name in codepoints:
        with Image.open(input_dir / f"{name}.png") as original:
            image = original.convert("RGBA")
            image.thumbnail((PPEM, PPEM), Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        image.save(buffer, format="PNG", optimize=True)
        data = buffer.getvalue()
        x = (PPEM - image.width) // 2
        y = (PPEM - image.height) // 2
        strike.glyphs[name] = Glyph(glyphName=name, graphicType="png ",
                                   originOffsetX=x, originOffsetY=y, imageData=data)
        glyph = cbdt_bitmap_format_17(None, font)
        glyph.imageData = data
        glyph.metrics = SmallGlyphMetrics()
        glyph.metrics.height, glyph.metrics.width = image.height, image.width
        glyph.metrics.BearingX, glyph.metrics.BearingY = x, y + image.height
        glyph.metrics.Advance = PPEM
        bitmap_data[name] = glyph
    sbix.strikes[PPEM] = strike
    font["sbix"] = sbix

    cbdt, cblc = newTable("CBDT"), newTable("CBLC")
    cbdt.version = cblc.version = 3.0
    cbdt.strikeData = [bitmap_data]
    location = BitmapStrike()
    size = location.bitmapSizeTable
    size.colorRef, size.ppemX, size.ppemY, size.bitDepth, size.flags = 0, PPEM, PPEM, 32, 1
    for direction in ("hori", "vert"):
        metrics = SbitLineMetrics()
        for field in ("ascender", "descender", "widthMax", "caretSlopeNumerator",
                      "caretSlopeDenominator", "caretOffset", "minOriginSB", "minAdvanceSB",
                      "maxBeforeBL", "minAfterBL", "pad1", "pad2"):
            setattr(metrics, field, 0)
        metrics.ascender, metrics.widthMax, metrics.caretSlopeNumerator = PPEM, PPEM, 1
        setattr(size, direction, metrics)
    index = eblc_index_sub_table_1(None, font)
    index.indexFormat, index.imageFormat, index.imageDataOffset = 1, 17, 0
    index.names = list(codepoints)
    location.indexSubTables = [index]
    cblc.strikes = [location]
    font["CBDT"], font["CBLC"] = cbdt, cblc

    # Firefox on macOS does not render sbix webfonts. Its OpenType-SVG path
    # embeds the same bitmap in a self-contained SVG; no paths are redrawn.
    from fontTools.ttLib.tables.S_V_G_ import SVGDocument
    svg = newTable("SVG ")
    svg.docList = []
    for name, glyph in bitmap_data.items():
        gid = font.getGlyphID(name)
        png = base64.b64encode(glyph.imageData).decode("ascii")
        width, height = glyph.metrics.width, glyph.metrics.height
        x, y = glyph.metrics.BearingX, PPEM - glyph.metrics.BearingY
        doc = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">'
               f'<g id="glyph{gid}" transform="translate(0,-{UNITS}) scale({UNITS / PPEM})">'
               f'<image x="{x}" y="{y}" width="{width}" height="{height}" '
               f'xlink:href="data:image/png;base64,{png}"/></g></svg>')
        svg.docList.append(SVGDocument(doc, gid, gid, compressed=False))
    font["SVG "] = svg
    output_dir.mkdir(parents=True, exist_ok=True)
    font.save(output_dir / "swu-symbols.ttf")
    font.flavor = "woff2"
    font.save(output_dir / "swu-symbols.woff2")
    print(f"Built {len(codepoints)} original-image color glyphs: {(output_dir / 'swu-symbols.woff2').stat().st_size:,} bytes WOFF2")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", required=True, type=Path, help="Directory of six aspect-name.png files you may use")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    build_font(args.input_dir, args.output_dir)
