import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
const root = new URL('../', import.meta.url);
test('keeps six stable private-use codepoints and a small CSS-only consumer', async () => {
  const codepoints = JSON.parse(await readFile(new URL('dist/swu-symbols.json', root), 'utf8'));
  assert.deepEqual(codepoints, JSON.parse(await readFile(new URL('codepoints.json', root), 'utf8')));
  assert.equal(new Set(Object.values(codepoints)).size, 6);
  assert.ok((await readFile(new URL('dist/swu-symbols.css', root))).length < 1536);
});
