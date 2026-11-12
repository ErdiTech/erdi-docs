// ERDI laser rangefinder frame codec (JavaScript port of the erdi-lrf Python package, MIT).
//
// Family A: 8-byte "55 AA" frames. Reply checksum covers the header; the transmit checksum does not.
// Family B: free-running "5C" data frames, little-endian distance, checksum = ~sum(bytes[1..-2]).
// Units differ by model (H series = cm, VB series = mm, family A = metres x10): the unit
// always comes from the model table (models.generated.json), never from the family.
//
// Pure functions, no I/O, so they run unchanged in the browser and under `node --test`.
import MODELS from './models.generated.mjs';

export { MODELS };
export const MODEL_NAMES = Object.keys(MODELS);

export const A_BAUD_RATES = [9600, 14400, 19200, 38400, 56000, 57600, 115200, 128000, 230400];
export const B_BAUD_RATES = [9600, 19200, 38400, 115200, 230400, 256000, 460800];

const A_HEADER = [0x55, 0xaa];
const B_DATA_HEADER = 0x5c;

export function hex(bytes) {
  return Array.from(bytes, (b) => b.toString(16).padStart(2, '0')).join(' ');
}

export function getModel(name) {
  const m = MODELS[String(name).trim().toUpperCase()];
  if (!m) throw new Error(`unknown model ${name}`);
  return m;
}

// ---- family A -------------------------------------------------------------
export function rxChecksumA(bytesWithoutChecksum) {
  let s = 0;
  for (const b of bytesWithoutChecksum) s = (s + b) & 0xff;
  return s;
}
export function txChecksumA(fn, data) {
  let s = fn;
  for (const b of data) s = (s + b) & 0xff;
  return s & 0xff;
}
export function buildCommandA(fn, data = [0xff, 0xff, 0xff, 0xff]) {
  return Uint8Array.from([...A_HEADER, fn, ...data, txChecksumA(fn, data)]);
}
export const A_SINGLE = () => buildCommandA(0x88);
export const A_CONTINUOUS = () => buildCommandA(0x89);
export const A_STOP = () => buildCommandA(0x8e);

// ---- family B -------------------------------------------------------------
export function checkSumB(payload) {
  let s = 0;
  for (const b of payload) s = (s + b) & 0xff;
  return ~s & 0xff;
}
export function buildCommandB(cmd, data) {
  const body = [cmd, data.length, ...data];
  return Uint8Array.from([0x5a, ...body, checkSumB(body)]);
}
export const B_START = () => buildCommandB(0x0a, [0x02, 0x00]); // 5A 0A 02 02 00 F1
export const B_STOP = () => buildCommandB(0x0a, [0x00, 0x00]); // 5A 0A 02 00 00 F3

// ---- parsing --------------------------------------------------------------
function metresFromRaw(model, raw) {
  const mpc = model.metres_per_count;
  return mpc == null ? null : raw * mpc;
}

/** Parse one family-B data frame. Returns null when the frame is not valid for the model. */
export function parseFrameB(frame, modelName) {
  const model = typeof modelName === 'string' ? getModel(modelName) : modelName;
  if (frame.length !== model.frame_len || frame[0] !== B_DATA_HEADER) return null;
  if (frame[frame.length - 1] !== checkSumB(frame.slice(1, -1))) return null;
  let raw = 0;
  for (let i = model.distance_bytes - 1; i >= 0; i--) raw = raw * 256 + frame[1 + i];
  const oor = model.out_of_range_raw != null && raw >= model.out_of_range_raw;
  return { family: 'B', raw, metres: metresFromRaw(model, raw), outOfRange: oor, ok: true, frame: Uint8Array.from(frame) };
}

/** Parse one family-A reply frame (single-shot / continuous ranging reply). */
export function parseFrameA(frame, modelName) {
  const model = typeof modelName === 'string' ? getModel(modelName) : modelName;
  if (frame.length !== 8 || frame[0] !== 0x55 || frame[1] !== 0xaa) return null;
  if (frame[7] !== rxChecksumA(frame.slice(0, 7))) return null;
  if (frame[2] !== 0x88 && frame[2] !== 0x89) return null; // only ranging replies
  const raw = (frame[5] << 8) | frame[6];
  const status = frame[3];
  return { family: 'A', raw, metres: metresFromRaw(model, raw), status, ok: status === 1, outOfRange: false, frame: Uint8Array.from(frame) };
}

/**
 * Incremental stream parser. push() accepts any chunking of the byte stream and returns the
 * measurements that completed. A frame that fails its checksum is skipped and the scan
 * resynchronises one byte later; counters record what was dropped.
 */
export class FrameParser {
  constructor(modelName) {
    this.model = getModel(modelName);
    this.name = String(modelName).toUpperCase();
    this.buf = [];
    this.stats = { valid: 0, rejected: 0, bytes: 0 };
  }
  push(chunk) {
    const out = [];
    for (const b of chunk) this.buf.push(b);
    this.stats.bytes += chunk.length;
    const n = this.model.frame_len;
    const isA = this.model.family === 'A';
    let i = 0;
    while (this.buf.length - i >= n) {
      const head = isA ? this.buf[i] === 0x55 && this.buf[i + 1] === 0xaa : this.buf[i] === B_DATA_HEADER;
      if (!head) { i++; continue; }
      const cand = this.buf.slice(i, i + n);
      const m = isA ? parseFrameA(cand, this.model) : parseFrameB(cand, this.model);
      if (m) { out.push(m); this.stats.valid++; i += n; } else { this.stats.rejected++; i++; }
    }
    if (i > 0) this.buf.splice(0, i);
    if (this.buf.length > 4096) this.buf.splice(0, this.buf.length - n);
    return out;
  }
}

/** Baud rates worth offering for a model (documented sets) with its default first. */
export function baudChoices(modelName) {
  const m = getModel(modelName);
  const set = m.family === 'A' ? A_BAUD_RATES : B_BAUD_RATES;
  return [m.default_baud, ...set.filter((b) => b !== m.default_baud)];
}

export const UNIT_LABEL = { m: 'm (x10 counts)', cm: 'cm', mm: 'mm' };
