// node --test test/
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { FrameParser, parseFrameA, parseFrameB, hex, MODELS, B_START, B_STOP, A_SINGLE, A_CONTINUOUS, A_STOP, checkSumB, rxChecksumA, baudChoices } from '../src/lib/erdi-protocol.mjs';

const fx = JSON.parse(readFileSync(new URL('../fixtures/frames.json', import.meta.url)));
const bytes = (h) => Uint8Array.from(h.split(' ').map((x) => parseInt(x, 16)));
const close = (a, b) => (a == null && b == null) || Math.abs(a - b) < 1e-9;

test('model table has the 22 public-protocol models', () => {
  assert.equal(Object.keys(MODELS).length, 22);
  assert.equal(Object.values(MODELS).filter((m) => m.family === 'A').length, 13);
  assert.equal(Object.values(MODELS).filter((m) => m.family === 'B').length, 9);
});

test('golden frames from the Python package decode identically', () => {
  assert.ok(fx.frames.length > 100);
  for (const f of fx.frames) {
    const fr = bytes(f.hex);
    const m = f.family === 'A' ? parseFrameA(fr, f.model) : parseFrameB(fr, f.model);
    assert.ok(m, `${f.model} ${f.hex} did not parse`);
    assert.equal(m.raw, f.expect.raw, `${f.model} ${f.hex}`);
    assert.ok(close(m.metres, f.expect.metres), `${f.model} ${f.hex}: ${m.metres} vs ${f.expect.metres}`);
    if (f.family === 'B') assert.equal(m.outOfRange, f.expect.oor);
    else assert.equal(m.status, f.expect.status);
  }
});

test('units differ by series: VB is mm, H is cm (10x trap)', () => {
  assert.ok(close(parseFrameB(bytes('5c 02 11 ec'), 'LRF22VB').metres, 4.354)); // 4354 mm
  assert.ok(close(parseFrameB(bytes('5c 02 11 ec'), 'LRF100H').metres, 43.54)); // 4354 cm
});

test('LRF1500H uses a 5-byte frame with a 3-byte distance', () => {
  const body = [0x02, 0x11, 0x03];
  const f = Uint8Array.from([0x5c, ...body, checkSumB(body)]);
  const m = parseFrameB(f, 'LRF1500H');
  assert.equal(m.raw, 0x031102);
  assert.ok(close(m.metres, 0x031102 / 100));
});

test('real factory captures: LRF22VB about 1.709 m, LRF50H about 1.96 m, spikes pass the checksum', () => {
  for (const f of fx.frames.filter((x) => x.note.startsWith('capture'))) {
    const m = parseFrameB(bytes(f.hex), f.model);
    if (f.model === 'LRF22VB') assert.ok(m.metres > 1.7 && m.metres < 1.72);
    else if (m.raw < 300) assert.ok(m.metres > 1.8 && m.metres < 2.1);
    else assert.ok(m.metres > 300); // spike frames pass the checksum (see erdi-lrf-drivers evidence)
  }
  assert.equal(fx.captures.LRF22VB.frames, 3000);
  assert.equal(fx.captures.LRF50H.frames, 2000);
});

test('bad checksum is rejected', () => {
  assert.equal(parseFrameB(bytes(fx.bad_checksum), 'LRF22VB'), null);
  assert.equal(parseFrameA(bytes('55 aa 88 01 ff 00 7b 00'), 'LRF3000A1'), null);
});

test('out-of-range marker per model', () => {
  for (const name of ['LRF22VB', 'LRF50H', 'LRF1500H']) {
    const f = fx.frames.find((x) => x.model === name && x.note === 'out-of-range marker');
    assert.equal(parseFrameB(bytes(f.hex), name).outOfRange, true, name);
  }
});

test('stream parser resyncs on noise, bad checksums and partial frames (B)', () => {
  const p = new FrameParser(fx.resync.model);
  const all = bytes(fx.resync.stream);
  const got = [];
  for (let i = 0; i < all.length; i += 3) got.push(...p.push(all.slice(i, i + 3))); // awkward chunking
  assert.deepEqual(got.map((m) => hex(m.frame)), fx.resync.valid);
  assert.ok(p.stats.rejected >= 1);
});

test('stream parser (A) matches Python find_frames', () => {
  const p = new FrameParser(fx.a_stream.model);
  const got = p.push(bytes(fx.a_stream.stream));
  assert.deepEqual(got.map((m) => hex(m.frame)), fx.a_stream.valid);
});

test('command builders match the manual examples', () => {
  assert.equal(hex(A_SINGLE()), '55 aa 88 ff ff ff ff 84');
  assert.equal(hex(A_CONTINUOUS()), '55 aa 89 ff ff ff ff 85');
  assert.equal(hex(A_STOP()), '55 aa 8e ff ff ff ff 8a');
  assert.equal(hex(B_START()), '5a 0a 02 02 00 f1');
  assert.equal(hex(B_STOP()), '5a 0a 02 00 00 f3');
  assert.equal(rxChecksumA([0x55, 0xaa, 0x88, 0xff, 0xff, 0xff, 0xff]), (0x55 + 0xaa + 0x88 + 4 * 0xff) & 0xff);
});

test('baud choices start with the documented default', () => {
  assert.equal(baudChoices('LRF22VB')[0], 460800);
  assert.equal(baudChoices('LRF3000A1')[0], 115200);
});
