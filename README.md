# SWU Symbols

The six original **Star Wars: Unlimited** aspect symbols in one color font.
No redrawing or tracing. **About 82 KB WOFF2**, less than 1 KB CSS, and no runtime
JavaScript. Ready-to-use WOFF2 and TTF files are included in [`dist/`](dist/).

Unofficial fan project. Build code and CSS are MIT; original artwork and the
embedded glyph images retain their publisher's rights. See [Rights](#rights).

## Quick start with the free CDN

[jsDelivr](https://www.jsdelivr.com/documentation) serves the tagged GitHub files
for free. No account, package installation, or npm publication is required:

```html
<link rel="stylesheet"
      href="https://cdn.jsdelivr.net/gh/FanaHOVA/swu-symbols@v1.0.0/dist/swu-symbols.css">

<span class="swu-symbol swu-command" role="img" aria-label="Command"></span>
```

The stylesheet loads `swu-symbols.woff2` from the same versioned CDN directory.
Pin an exact release, as above, to keep CSS, glyph mappings, and font bytes in
sync. Publish a new tag for updates; exact-version CDN URLs are immutable.
For a content security policy, allow `https://cdn.jsdelivr.net` in `style-src`
and `font-src`.

## Self-host or download

Download the font and stylesheet from the [v1.0.0 release](https://github.com/FanaHOVA/swu-symbols/releases/tag/v1.0.0),
or copy [`dist/swu-symbols.woff2`](dist/swu-symbols.woff2) and
[`dist/swu-symbols.css`](dist/swu-symbols.css) into the same public directory:

```html
<link rel="stylesheet" href="/fonts/swu-symbols.css">
<span class="swu-symbol swu-vigilance" role="img" aria-label="Vigilance"></span>
```

The browser uses WOFF2. [`dist/swu-symbols.ttf`](dist/swu-symbols.ttf) is available
for compatible desktop applications. No Python or font build is needed to use
the prebuilt files. The project is hosted on GitHub; it is not published to npm.

## Symbols and sizing

| Aspect | Class | Codepoint |
| --- | --- | --- |
| Vigilance | `swu-vigilance` | `U+E900` |
| Command | `swu-command` | `U+E901` |
| Aggression | `swu-aggression` | `U+E902` |
| Cunning | `swu-cunning` | `U+E903` |
| Heroism | `swu-heroism` | `U+E904` |
| Villainy | `swu-villainy` | `U+E905` |

Always include the base `swu-symbol` class. Size with `font-size`; each symbol
reserves a 1em square and preserves the original image proportions and colors:

```html
<span class="swu-symbol swu-aggression" role="img" aria-label="Aggression"
      style="font-size:24px"></span>
```

For a repeated aspect cost, supply one accessible group name and hide the
individual decorative glyphs from assistive technology:

```html
<span role="img" aria-label="Command, Command, Heroism">
  <span class="swu-symbol swu-command" aria-hidden="true"></span>
  <span class="swu-symbol swu-command" aria-hidden="true"></span>
  <span class="swu-symbol swu-heroism" aria-hidden="true"></span>
</span>
```

## Implementation and performance

The original PNGs are fitted proportionally into 64px squares. A single WOFF2
contains sbix, CBDT/CBLC, and OpenType-SVG encodings of the same bitmap pixels.
All six glyphs were verified to paint in color in Chromium, Firefox, and WebKit
on macOS. The different encodings support those browsers' font rendering paths.

64px supports 16px symbols at 4x pixel density and 32px symbols at 2x. Larger
sizes upscale the embedded bitmap; this is not vector artwork. Open
[`dist/index.html`](dist/index.html) through a static server to review all six
symbols at 16, 24, and 48px on light and dark backgrounds.

The font downloads only when an aspect glyph is rendered. One approximately
82 KB font download replaces up to six original PNG downloads totaling about
214 KB. Both fonts and images are browser-cacheable. The font reduces transfer
size when several aspects are used; an individual PNG can be smaller on a page
that uses only one aspect. Repeated symbols require no additional font requests.

## Regenerate from original images

Requires Node 22+ and Python 3.10+. Source PNGs are not bundled. `aspects.json`
records the six official source URLs; provide locally held images with rights
appropriate to your intended use. The build does not download artwork.

```sh
npm ci
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
npm run build
.venv/bin/python scripts/build-font.py --input-dir /path/to/aspect-pngs
```

The input folder must contain `vigilance.png`, `command.png`, `aggression.png`,
`cunning.png`, `heroism.png`, and `villainy.png`. Font outputs are written to
`dist/swu-symbols.woff2` and `dist/swu-symbols.ttf`. The checked-in fonts let
normal consumers use the package without installing build tools.

## Checks

```sh
npm test
.venv/bin/python scripts/font.check.py
```

The converter check builds from synthetic images and verifies unchanged RGBA
pixels across all three encodings, stable codepoints, rights metadata, and
byte-identical output from repeated builds. The release check validates the
included font's version, glyph coverage, and size budget. CI performs no source
artwork downloads. Node checks cover the generated CSS and codepoint manifest.

## Rights

The code and CSS are MIT licensed. The original artwork and embedded glyph
images remain the property of their respective owners, including Lucasfilm Ltd.
and Fantasy Flight Games. This project's license does not grant artwork rights
or imply publisher endorsement.

The [official media-kit policy](https://starwarsunlimited.com/media-kit) restricts
redistribution and modification. Inclusion here, CDN availability, and credit
notices do not override that policy or grant new permissions. Review
[NOTICE.md](NOTICE.md) and the publisher's terms for your intended use.
