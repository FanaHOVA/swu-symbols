import { mkdir, readFile, writeFile } from 'node:fs/promises';
const root = new URL('../', import.meta.url);
const codepoints = JSON.parse(await readFile(new URL('codepoints.json', root), 'utf8'));
await mkdir(new URL('dist/', root), { recursive: true });
await writeFile(new URL('dist/swu-symbols.json', root), JSON.stringify(codepoints, null, 2) + '\n');
await writeFile(new URL('dist/swu-symbols.css', root), `/* MIT CSS. Embedded artwork is NOT MIT/OFL licensed; see NOTICE.md. */
@font-face{font-family:"SWU Symbols Color";src:url("swu-symbols.woff2") format("woff2");font-display:block;font-style:normal;font-weight:400;unicode-range:U+E900-E905}
.swu-symbol{display:inline-block;width:1em;height:1em;font-family:"SWU Symbols Color";font-style:normal;font-weight:400;font-synthesis:none;line-height:1;vertical-align:middle;flex-shrink:0}
${Object.entries(codepoints).map(([name, cp]) => `.swu-${name}::before{content:"\\${cp.toString(16)}"}`).join('\n')}
`);
const rows = Object.keys(codepoints).map(name => `<tr><th scope="row">${name}</th>${[16,24,48].map(size => `<td><span class="swu-symbol swu-${name}" role="img" aria-label="${name}" style="font-size:${size}px"></span></td>`).join('')}</tr>`).join('');
await writeFile(new URL('dist/index.html', root), `<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SWU Symbols — original-image color font</title><link rel="stylesheet" href="swu-symbols.css">
<style>body{font:16px system-ui;margin:0;background:#f8fafc;color:#172033}main{max-width:760px;margin:40px auto;padding:24px}h1{font-size:28px}p{line-height:1.5}table{width:100%;border-collapse:collapse;margin:24px 0}th,td{text-align:left;padding:12px;border-bottom:1px solid #cbd5e1}tbody th{text-transform:capitalize;font-weight:500}.dark{background:#101827;color:#f8fafc;padding:16px;border-radius:12px}.dark th,.dark td{border-color:#334155}a{color:#2563eb}</style>
<main><h1>Original artwork in a color font</h1><p>Six original Star Wars: Unlimited aspect symbols in one color WOFF2. No redrawing or tracing. <a href="https://github.com/FanaHOVA/swu-symbols">Usage and downloads</a>. Artwork retains publisher rights; see NOTICE.md.</p>
<table><thead><tr><th>Aspect</th><th>16px</th><th>24px</th><th>48px</th></tr></thead><tbody>${rows}</tbody></table>
<section class="dark"><table><tbody>${rows}</tbody></table></section></main></html>`);
console.log('Built font classes, codepoints, and specimen. Prebuilt fonts are included in dist/.');
