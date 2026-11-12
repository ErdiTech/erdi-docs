import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import BrowserOnly from '@docusaurus/BrowserOnly';
import styles from './styles.module.css';
import {
  MODELS, MODEL_NAMES, FrameParser, baudChoices, hex, A_SINGLE, B_START, B_STOP, checkSumB, rxChecksumA,
} from '../../lib/erdi-protocol.mjs';

const MAX_SAMPLES = 100000;
const CHART_POINTS = 600;

function fmt(v, d = 3) {
  return v == null || Number.isNaN(v) ? 'n/a' : v.toFixed(d);
}

// Build a synthetic frame for the demo mode (no hardware).
function demoFrame(name, metres) {
  const m = MODELS[name];
  if (m.family === 'B') {
    const raw = Math.max(0, Math.round(metres / m.metres_per_count));
    const body = [];
    for (let i = 0; i < m.distance_bytes; i++) body.push((raw >> (8 * i)) & 0xff);
    return Uint8Array.from([0x5c, ...body, checkSumB(body)]);
  }
  const raw = Math.round(metres * 10);
  const f = [0x55, 0xaa, 0x88, 0x01, 0xff, (raw >> 8) & 0xff, raw & 0xff];
  return Uint8Array.from([...f, rxChecksumA(f)]);
}

function Monitor() {
  const supported = typeof navigator !== 'undefined' && 'serial' in navigator;
  const [model, setModel] = useState('LRF22VB');
  const [baud, setBaud] = useState(MODELS['LRF22VB'].default_baud);
  const [state, setState] = useState('disconnected'); // disconnected | connected | demo
  const [error, setError] = useState('');
  const [latest, setLatest] = useState(null);
  const [stats, setStats] = useState({ valid: 0, rejected: 0, oor: 0, bytes: 0, hz: 0, min: null, max: null, mean: null });
  const [lines, setLines] = useState([]);
  const [pollHz, setPollHz] = useState(5);

  const portRef = useRef(null);
  const readerRef = useRef(null);
  const writerRef = useRef(null);
  const parserRef = useRef(null);
  const samplesRef = useRef([]);
  const chartRef = useRef(null);
  const plotRef = useRef(null);
  const uplotRef = useRef(null);
  const timersRef = useRef([]);
  const runRef = useRef(false);
  const winRef = useRef([]);

  const mdl = MODELS[model];
  const bauds = useMemo(() => baudChoices(model), [model]);

  useEffect(() => { setBaud(MODELS[model].default_baud); }, [model]);

  // uPlot is loaded on demand (client only).
  useEffect(() => {
    let dead = false;
    (async () => {
      const [{ default: uPlot }] = await Promise.all([import('uplot'), import('uplot/dist/uPlot.min.css')]);
      if (dead || !chartRef.current) return;
      uplotRef.current = uPlot;
      const w = chartRef.current.clientWidth || 600;
      plotRef.current = new uPlot({
        width: w, height: 240, legend: { show: false },
        scales: { x: { time: false } },
        axes: [{ label: 'seconds', stroke: '#888' }, { label: 'metres', stroke: '#888' }],
        series: [{}, { stroke: '#e0551c', width: 2, spanGaps: false }],
      }, [[0], [null]], chartRef.current);
    })();
    return () => { dead = true; if (plotRef.current) plotRef.current.destroy(); plotRef.current = null; };
  }, []);

  const redraw = useCallback(() => {
    const s = samplesRef.current;
    const tail = s.slice(-CHART_POINTS);
    if (plotRef.current && tail.length) {
      const t0 = tail[0].t;
      plotRef.current.setData([tail.map((p) => (p.t - t0) / 1000), tail.map((p) => (p.oor ? null : p.metres))]);
    }
  }, []);

  const handle = useCallback((ms) => {
    const now = performance.now();
    for (const m of ms) {
      const rec = { t: now, iso: new Date().toISOString(), raw: m.raw, metres: m.metres, oor: !!m.outOfRange, ok: m.ok, hex: hex(m.frame) };
      samplesRef.current.push(rec);
      winRef.current.push(now);
      setLatest(rec);
    }
    if (samplesRef.current.length > MAX_SAMPLES) samplesRef.current.splice(0, samplesRef.current.length - MAX_SAMPLES);
    const w = winRef.current;
    while (w.length && now - w[0] > 2000) w.shift();
  }, []);

  // Periodic UI refresh (stats, chart, hex log), decoupled from the byte rate.
  useEffect(() => {
    const id = setInterval(() => {
      const p = parserRef.current;
      if (!p) return;
      const s = samplesRef.current;
      const win = s.slice(-200).filter((x) => !x.oor && x.metres != null);
      const vals = win.map((x) => x.metres);
      const span = winRef.current.length > 1 ? (winRef.current[winRef.current.length - 1] - winRef.current[0]) / 1000 : 0;
      setStats({
        valid: p.stats.valid, rejected: p.stats.rejected, bytes: p.stats.bytes,
        oor: s.filter((x) => x.oor).length,
        hz: span > 0 ? (winRef.current.length - 1) / span : 0,
        min: vals.length ? Math.min(...vals) : null, max: vals.length ? Math.max(...vals) : null,
        mean: vals.length ? vals.reduce((a, b) => a + b, 0) / vals.length : null,
      });
      setLines(s.slice(-12).reverse().map((x) => x.hex));
      redraw();
    }, 250);
    return () => clearInterval(id);
  }, [redraw]);

  const stopAll = useCallback(async () => {
    runRef.current = false;
    timersRef.current.forEach(clearInterval);
    timersRef.current = [];
    try { if (readerRef.current) { await readerRef.current.cancel(); } } catch (e) { /* closing */ }
    try { if (writerRef.current) { writerRef.current.releaseLock(); } } catch (e) { /* closing */ }
    try { if (portRef.current) { await portRef.current.close(); } } catch (e) { /* closing */ }
    readerRef.current = null; writerRef.current = null; portRef.current = null;
    setState('disconnected');
  }, []);

  useEffect(() => () => { runRef.current = false; timersRef.current.forEach(clearInterval); }, []);

  const reset = () => {
    samplesRef.current = []; winRef.current = [];
    parserRef.current = new FrameParser(model);
    setLatest(null); setLines([]);
  };

  const send = async (bytes) => {
    if (!writerRef.current) return;
    await writerRef.current.write(bytes);
  };

  const connect = async () => {
    setError('');
    try {
      const port = await navigator.serial.requestPort();
      await port.open({ baudRate: Number(baud), dataBits: 8, stopBits: 1, parity: 'none', bufferSize: 4096 });
      portRef.current = port;
      writerRef.current = port.writable.getWriter();
      reset();
      runRef.current = true;
      setState('connected');
      if (mdl.family === 'A') {
        const id = setInterval(() => { send(A_SINGLE()).catch(() => {}); }, Math.max(50, 1000 / pollHz));
        timersRef.current.push(id);
      }
      while (port.readable && runRef.current) {
        const reader = port.readable.getReader();
        readerRef.current = reader;
        try {
          for (;;) {
            const { value, done } = await reader.read();
            if (done) break;
            if (value) handle(parserRef.current.push(value));
          }
        } finally { reader.releaseLock(); }
      }
    } catch (e) {
      if (e && e.name !== 'NotFoundError') setError(String(e.message || e));
    } finally {
      await stopAll();
    }
  };

  const demo = () => {
    setError('');
    reset();
    runRef.current = true;
    setState('demo');
    let t = 0;
    const id = setInterval(() => {
      t += 0.05;
      const span = Math.min(mdl.max_range_m * 0.5, 50);
      const metres = Math.max(mdl.min_range_m || 0.1, (span / 2) * (1 + Math.sin(t)) + 0.3);
      const f = demoFrame(model, metres);
      // deliver in awkward chunks to exercise the resync path
      handle(parserRef.current.push(f.slice(0, 2)));
      handle(parserRef.current.push(f.slice(2)));
    }, mdl.family === 'A' ? 200 : 50);
    timersRef.current.push(id);
  };

  const exportCsv = () => {
    const unit = mdl.unit;
    const rows = ['timestamp_iso,model,raw,raw_unit,metres,out_of_range,status_ok,frame_hex'];
    for (const s of samplesRef.current) {
      rows.push([s.iso, model, s.raw, unit === 'm' ? 'm_x10' : unit, s.metres == null ? '' : s.metres.toFixed(4), s.oor ? 1 : 0, s.ok ? 1 : 0, s.hex].join(','));
    }
    const blob = new Blob([rows.join('\n') + '\n'], { type: 'text/csv' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `erdi-${model}-${new Date().toISOString().replace(/[:.]/g, '-')}.csv`;
    a.click();
    URL.revokeObjectURL(a.href);
  };

  const connected = state !== 'disconnected';
  return (
    <div className={styles.wrap}>
      {!supported && (
        <div className="alert alert--warning" role="alert" data-testid="no-webserial">
          This browser does not support the Web Serial API. Open this page in Chrome or Edge on a desktop computer
          (version 89 or later, HTTPS or localhost). Firefox, Safari and mobile browsers cannot open serial ports.
          You can still try the monitor with simulated frames using <strong>Run demo</strong>.
        </div>
      )}
      <div className={styles.controls}>
        <label>Model
          <select value={model} disabled={connected} onChange={(e) => setModel(e.target.value)} data-testid="model">
            {MODEL_NAMES.map((n) => <option key={n} value={n}>{n} (family {MODELS[n].family})</option>)}
          </select>
        </label>
        <label>Baud rate
          <select value={baud} disabled={connected} onChange={(e) => setBaud(Number(e.target.value))} data-testid="baud">
            {bauds.map((b, i) => <option key={b} value={b}>{b}{i === 0 ? ' (model default)' : ''}</option>)}
          </select>
        </label>
        {mdl.family === 'A' && (
          <label>Poll rate (Hz)
            <input type="number" min="1" max="20" value={pollHz} disabled={connected} onChange={(e) => setPollHz(Number(e.target.value) || 1)} />
          </label>
        )}
        <div className={styles.buttons}>
          {!connected && <button className="button button--primary" disabled={!supported} onClick={connect} data-testid="connect">Connect serial port</button>}
          {!connected && <button className="button button--secondary" onClick={demo} data-testid="demo">Run demo</button>}
          {connected && <button className="button button--danger" onClick={stopAll} data-testid="disconnect">Disconnect</button>}
          {state === 'connected' && mdl.start_stop && (
            <>
              <button className="button button--outline button--primary" onClick={() => send(B_START())}>Send start ranging</button>
              <button className="button button--outline button--primary" onClick={() => send(B_STOP())}>Send stop ranging</button>
            </>
          )}
          <button className="button button--outline button--secondary" onClick={exportCsv} disabled={!samplesRef.current.length && !latest} data-testid="csv">Export CSV</button>
        </div>
      </div>
      {mdl.a1_continuous_hold && (
        <div className="alert alert--info margin-bottom--md">This model is polled with single-shot requests. Continuous ranging is not used here because the manual leaves the reply function byte unresolved.</div>
      )}
      {error && <div className="alert alert--danger" role="alert">{error}</div>}
      <div className={styles.readout}>
        <div>
          <div className={styles.big} data-testid="latest">{latest ? (latest.oor ? 'out of range' : (latest.metres == null ? `raw ${latest.raw}` : `${fmt(latest.metres)} m`)) : 'no data yet'}</div>
          <div className={styles.sub}>{latest ? `raw ${latest.raw} (${mdl.unit === 'm' ? 'metres x10' : mdl.unit})${latest.ok ? '' : ', status: measurement failed'}` : state === 'disconnected' ? 'not connected' : 'waiting for frames'}</div>
        </div>
        <table className={styles.stats}>
          <tbody>
            <tr><th>State</th><td data-testid="state">{state}</td><th>Frames</th><td data-testid="valid">{stats.valid}</td></tr>
            <tr><th>Rate</th><td>{fmt(stats.hz, 1)} Hz</td><th>Rejected</th><td data-testid="rejected">{stats.rejected}</td></tr>
            <tr><th>Mean</th><td>{fmt(stats.mean)} m</td><th>Out of range</th><td>{stats.oor}</td></tr>
            <tr><th>Min / max</th><td>{fmt(stats.min)} / {fmt(stats.max)} m</td><th>Bytes</th><td>{stats.bytes}</td></tr>
          </tbody>
        </table>
      </div>
      <div ref={chartRef} className={styles.chart} />
      <details>
        <summary>Last frames (hex)</summary>
        <pre className={styles.hex}>{lines.join('\n') || 'none'}</pre>
      </details>
    </div>
  );
}

export default function SerialMonitor() {
  return <BrowserOnly fallback={<div>Loading the serial monitor...</div>}>{() => <Monitor />}</BrowserOnly>;
}
