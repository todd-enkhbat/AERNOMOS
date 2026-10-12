// @ts-nocheck — imperative canvas + DOM engine ported from prototypes/nomos-console.html.
// The React wrapper (NomosConsole.tsx) mounts it once and calls the returned cleanup on unmount.
import * as d3 from "d3-geo";
import { feature } from "topojson-client";

export type ConsoleDeps = {
  /** Creates a real private mission; resolves to its id. */
  createMission: (spec: Record<string, unknown>) => Promise<string>;
  /** Lists this browser session's private missions (empty on failure). */
  listMissions: () => Promise<Array<{ id: string; title: string }>>;
  navigate: (href: string) => void;
};

export function mountConsole(root: HTMLElement, deps: ConsoleDeps): () => void {
const $ = (s, r = root) => r.querySelector(s);
const $$ = (s, r = root) => [...r.querySelectorAll(s)];
const IMG = '/images/';
let alive = true, rafId = 0;
const cleanups = [];
const onWin = (type, fn) => { addEventListener(type, fn); cleanups.push(() => removeEventListener(type, fn)); };
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const PI = Math.PI, D2R = PI / 180, R2D = 180 / PI;
const EARTH = 2 * PI / 1436, SPEED = 4;                 // sim-minutes per real second
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const ease = t => 1 - Math.pow(1 - clamp(t), 3);
const chip = k => `<span class="chip chip-${k.toLowerCase()}">${k}</span>`;
const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const RECORD = (sz, cls = 'spin') => `<span class="record av ${cls}" style="width:${sz}px;height:${sz}px"><img src="${IMG}nomos-golden-record-disc.png" alt=""></span>`;

/* ================= registry (illustrative positions of real public sites) ================= */
const GROUND = [
  { id: 'svalbard', name: 'Svalbard', ll: [15.4, 78.2] }, { id: 'fairbanks', name: 'Fairbanks', ll: [-147.7, 64.8] },
  { id: 'wallops', name: 'Wallops', ll: [-75.5, 37.9] }, { id: 'matera', name: 'Matera', ll: [16.7, 40.6] },
  { id: 'hbk', name: 'Hartebeesthoek', ll: [27.7, -25.9] }, { id: 'alice', name: 'Alice Springs', ll: [133.9, -23.7] },
  { id: 'santiago', name: 'Santiago', ll: [-70.7, -33.4] },
];
const CLOUD = [
  { id: 'weu', name: 'West Europe', ll: [4.9, 52.4] }, { id: 'use1', name: 'US East', ll: [-77.5, 39.0] },
  { id: 'usw2', name: 'US West', ll: [-119.7, 45.6] }, { id: 'apse', name: 'Asia Pacific SE', ll: [103.8, 1.35] },
];
const SATS = [
  { id: 's1a', name: 'Sentinel-1A', kind: 'sar', inc: 98.18, raan: -40, phase: .2, period: 98.6, h: .13 },
  { id: 's1c', name: 'Sentinel-1C', kind: 'sar', inc: 98.18, raan: 140, phase: 3.3, period: 98.6, h: .13 },
  { id: 's2a', name: 'Sentinel-2A', kind: 'optical', inc: 98.57, raan: 25, phase: 2.1, period: 100.6, h: .145 },
  { id: 's2b', name: 'Sentinel-2B', kind: 'optical', inc: 98.57, raan: 205, phase: 4.0, period: 100.6, h: .145 },
  { id: 'l9', name: 'Landsat 9', kind: 'optical', inc: 98.2, raan: 115, phase: 1.0, period: 98.9, h: .137 },
];
const satById = id => SATS.find(s => s.id === id);
const byId = id => GROUND.find(g => g.id === id) || CLOUD.find(c => c.id === id);
$('#nSats').textContent = `${SATS.length} public missions · REFERENCE`;
$('#nGround').textContent = `${GROUND.length} sites · REFERENCE`;
$('#nCloud').textContent = `${CLOUD.length} regions · illustrative`;

const PLACES = {
  nyh: { name: 'New York Harbor', bbox: [-74.3, 40.3, -73.5, 41.0], re: /new york|ny harbou?r|nyc|manhattan/i },
  rtm: { name: 'Port of Rotterdam', bbox: [3.8, 51.8, 4.5, 52.1], re: /rotterdam/i },
  sgp: { name: 'Singapore Strait', bbox: [103.6, 1.1, 104.3, 1.5], re: /singapore/i },
  butte: { name: 'Butte County, California', bbox: [-122.1, 39.4, -121.3, 40.1], re: /butte|paradise|california|norcal/i },
  attica: { name: 'Attica, Greece', bbox: [23.5, 37.8, 24.2, 38.3], re: /attica|athens|greece/i },
  hou: { name: 'Houston, Texas', bbox: [-95.6, 29.5, -95.0, 30.1], re: /houston|texas/i },
  dhaka: { name: 'Dhaka, Bangladesh', bbox: [90.1, 23.5, 90.7, 24.0], re: /dhaka|bangladesh/i },
};
const TARGETS = {
  vessels: { label: 'Vessel activity', intent: 'monitor', sensor: 'sar', places: ['nyh', 'rtm', 'sgp'], objective: 'Detect and count vessel activity' },
  change: { label: 'Land & construction change', intent: 'monitor', sensor: 'optical', places: ['rtm', 'hou', 'sgp'], objective: 'Detect land-surface change' },
  wildfire: { label: 'Wildfire', intent: 'respond', sensor: 'optical', places: ['butte', 'attica'], objective: 'Map the active fire front and burn scar' },
  flood: { label: 'Flood', intent: 'respond', sensor: 'sar', places: ['hou', 'dhaka'], objective: 'Delineate flood extent for responders' },
};
const SENSORS = {
  sar: { label: 'C-band SAR', sats: ['s1a', 's1c'], coll: 'sentinel-1-grd', why: 'sees through cloud and smoke, day or night' },
  optical: { label: 'Multispectral optical', sats: ['s2a', 's2b', 'l9'], coll: 'sentinel-2-l2a · landsat-c2-l2', why: 'gives true-colour and thermal context' },
  both: { label: 'SAR + optical', sats: ['s1a', 's2a', 'l9'], coll: 'sentinel-1-grd · sentinel-2-l2a', why: 'pairs all-weather radar with visual context' },
};
const FRESH = { archive: 'Latest archive (last 72 h)', next24: 'Within the next 24 h', asap: 'As soon as possible' };
const INTENTS = {
  monitor: { label: 'Monitor a place', sub: 'Recurring watch — vessels, change, activity', img: 'network/cloud-nodes.png' },
  respond: { label: 'Respond to an event', sub: 'Fire, flood or disaster imagery, fast', img: 'irosa-solar-array-hero.jpg' },
  explore: { label: 'Explore the network', sub: 'Satellites, stations and regions Nomos models', img: 'network/ground-stations.png' },
  free: { label: 'Describe it myself', sub: 'Type the outcome in your own words', img: 'nomos-lithograph-hero.jpg' },
};
const EXAMPLES = [
  { title: 'Maritime watch · New York Harbor', meta: 'SAR · monitor', slots: { intent: 'monitor', target: 'vessels', aoi: 'nyh', sensor: 'sar', freshness: 'next24', priority: 'Fastest', delivery: 'Cloud bucket' } },
  { title: 'Wildfire response · Butte County', meta: 'Optical · respond', slots: { intent: 'respond', target: 'wildfire', aoi: 'butte', sensor: 'optical', freshness: 'asap', priority: 'Fastest', delivery: 'Webhook' } },
  { title: 'Flood extent · Houston', meta: 'SAR · respond', slots: { intent: 'respond', target: 'flood', aoi: 'hou', sensor: 'sar', freshness: 'archive', priority: 'Most reliable', delivery: 'Email brief' } },
];

/* ================= mission model ================= */
const S = { slots: {}, mission: null, step: null, stage: 0, at: {}, done: false, windows: null, t0: 0, log: [], token: 0, noted: {},
  layers: { sats: true, ground: true, cloud: true }, lens: 'orbit', picking: false, mine: [], current: null, hover: null, running: false };
const aoiOf = sl => typeof sl.aoi === 'string' ? { key: sl.aoi, ...PLACES[sl.aoi] } : sl.aoi;
const centerOf = a => [(a.bbox[0] + a.bbox[2]) / 2, (a.bbox[1] + a.bbox[3]) / 2];
const nearest = (ll, list, n = 1) => list.slice().sort((a, b) => d3.geoDistance(ll, a.ll) - d3.geoDistance(ll, b.ll)).slice(0, n);

function buildMission(sl) {
  const aoi = aoiOf(sl), c = centerOf(aoi), tgt = TARGETS[sl.target], sen = SENSORS[sl.sensor];
  const stations = nearest(c, GROUND, 3).map(g => g.id), region = nearest(c, CLOUD)[0];
  const polar = nearest(c, GROUND.filter(g => Math.abs(g.ll[1]) > 60))[0];
  const deliv = sl.delivery === 'Webhook' ? 'Webhook endpoint' : sl.delivery === 'Email brief' ? 'Emailed technical brief' : `Customer bucket · ${region.name}`;
  const why = sl.freshness === 'asap'
    ? 'Fastest path available today: the latest archive scene now, then the next natural pass — no tasking needed.'
    : sl.freshness === 'next24' ? 'Uses the next natural passes of public missions plus the latest archive baseline; no tasking or reservation required.'
    : 'The public archive already covers this area, so no tasking or reservation is required.';
  return {
    key: 'msn_' + Math.random().toString(36).slice(2, 8), title: `${tgt.label} · ${aoi.name}`, aoi, c, tgt, sen, sats: sen.sats, primary: sen.sats[0], stations, region,
    cover: tgt.intent === 'respond' ? 'irosa-solar-array-hero.jpg' : 'network/cloud-nodes.png',
    paths: [
      { id: 'A', rec: true, name: 'Archive + natural passes → near-data compute → delivery', way: ['aoi', polar.id, region.id],
        nodes: [`${sen.label} scenes (public)`, 'Operator downlink → public archive', `Process near data · ${region.name}`, deliv],
        truth: ['REFERENCE', 'REFERENCE', 'ESTIMATED', 'SIMULATED'], why },
      { id: 'B', name: 'New tasking pass → reserved downlink → cloud', way: ['aoi', stations[0], region.id],
        nodes: ['Commercial tasking pass', `Reserved downlink · ${byId(stations[0]).name}`, `Process · ${region.name}`, deliv],
        truth: ['PLANNED', 'PLANNED', 'ESTIMATED', 'PLANNED'], why: 'Fresher capture, but needs a provider tasking integration Nomos does not have yet.' },
      { id: 'C', name: 'Onboard detection → alert-only downlink', way: ['aoi', region.id],
        nodes: ['Onboard inference', 'Alert relay', '—', 'Alert webhook'],
        truth: ['PLANNED', 'PLANNED', 'UNAVAILABLE', 'PLANNED'], why: 'Lowest latency in principle; no onboard execution partner is connected.' },
    ],
  };
}

/* ================= orbit math (toy circular orbits) ================= */
function satLL(s, t) {
  const i = s.inc * D2R, u = s.phase + 2 * PI * t / s.period;
  const lat = Math.asin(Math.sin(i) * Math.sin(u));
  const lon = s.raan * D2R + Math.atan2(Math.cos(i) * Math.sin(u), Math.cos(u)) - EARTH * t;
  return [((lon * R2D + 540) % 360) - 180, lat * R2D];
}
function ringLL(s, t, n = 160) {
  const out = [], i = s.inc * D2R;
  for (let k = 0; k <= n; k++) {
    const u = 2 * PI * k / n, lat = Math.asin(Math.sin(i) * Math.sin(u));
    const lon = s.raan * D2R + Math.atan2(Math.cos(i) * Math.sin(u), Math.cos(u)) - EARTH * t;
    out.push([((lon * R2D + 540) % 360) - 180, lat * R2D]);
  }
  return out;
}
function contactWindows(m, t0, span = 720) {
  const st = m.stations.map(byId);
  return m.sats.map(id => {
    const sat = satById(id), img = [], dl = []; let a0 = null, d0 = null;
    for (let k = 0; k <= span; k++) {
      const ll = satLL(sat, t0 + k);
      const a = d3.geoDistance(ll, m.c) < 0.17, g = st.some(s => d3.geoDistance(ll, s.ll) < 0.38);
      if (a && a0 === null) a0 = k; if (!a && a0 !== null) { img.push([a0, k]); a0 = null; }
      if (g && d0 === null) d0 = k; if (!g && d0 !== null) { dl.push([d0, k]); d0 = null; }
    }
    if (a0 !== null) img.push([a0, span]); if (d0 !== null) dl.push([d0, span]);
    return { sat, img, dl };
  });
}

/* ================= globe renderer ================= */
const cv = $('#globe'), ctx = cv.getContext('2d'), slot = $('#slot'), stage = $('#stage');
const proj = d3.geoOrthographic().clipAngle(90).precision(.5), gpath = d3.geoPath(proj, ctx);
const grat = d3.geoGraticule().step([15, 15])();
const LIGHT = (() => { const v = [-.48, .5, .72], n = Math.hypot(...v); return v.map(x => x / n); })();
let dots = null, W = 0, H = 0, DPR = 1, cx = 0, cy = 0, R = 200, curR = 0;
let rot = [80, -18], target = [80, -18], dragging = false, lastUser = 0, moved = 0;
let simT = 0, playing = !reduce, lastFrame = performance.now(), V = {};
const baseUTC = (() => { const d = new Date(); return d.getUTCHours() * 60 + d.getUTCMinutes(); })();
const utcAt = k => (baseUTC + S.t0 + k) % 1440;

import('world-atlas/land-110m.json').then(mod => {
  if (!alive) return;
  const topo = mod.default || mod;
  const land = feature(topo, topo.objects.land), w = 1440, h = 720;
  const oc = document.createElement('canvas'); oc.width = w; oc.height = h; const c = oc.getContext('2d');
  c.fillStyle = '#fff'; c.beginPath(); d3.geoPath(d3.geoEquirectangular().scale(w / (2 * PI)).translate([w / 2, h / 2]), c)(land); c.fill();
  const px = c.getImageData(0, 0, w, h).data, pts = [], step = 1.25;
  for (let lat = -84; lat <= 84; lat += step) {
    const n = Math.max(1, Math.round(360 * Math.cos(lat * D2R) / step));
    for (let i = 0; i < n; i++) {
      const lon = -180 + (i + .5) * 360 / n, x = Math.floor((lon + 180) / 360 * w) % w, y = Math.floor((90 - lat) / 180 * h);
      if (px[(y * w + x) * 4 + 3] > 120) pts.push(lon * D2R, lat * D2R);
    }
  }
  dots = new Float32Array(pts);
}).catch(() => {});

function resize() {
  const b = cv.getBoundingClientRect(); DPR = Math.min(2, devicePixelRatio || 1);
  W = b.width; H = b.height; cv.width = Math.round(W * DPR); cv.height = Math.round(H * DPR);
}
const ro = new ResizeObserver(resize); ro.observe(cv); resize(); cleanups.push(() => ro.disconnect());

function layout() {
  const sb = slot.getBoundingClientRect(), cb = cv.getBoundingClientRect();
  cx = sb.left - cb.left + sb.width / 2; cy = sb.top - cb.top + sb.height / 2;
  const tR = clamp((Math.min(sb.width, sb.height) / 2 - 22) / 1.27, 70, 380);
  curR = curR ? curR + (tR - curR) * .12 : tR; R = curR;
  V = { lc: -rot[0] * D2R, sp: Math.sin(-rot[1] * D2R), cp: Math.cos(-rot[1] * D2R) };
}
function P(ll, h = 0) {
  const l = ll[0] * D2R, p = ll[1] * D2R, c = Math.cos(p), s = Math.sin(p), dl = l - V.lc, cd = Math.cos(dl);
  const X = c * Math.sin(dl), Y = V.cp * s - V.sp * c * cd, Z = V.sp * s + V.cp * c * cd, k = R * (1 + h);
  return { x: cx + X * k, y: cy - Y * k, z: Z, front: Z > 0, vis: Z > 0 || Math.hypot(X, Y) * (1 + h) > 1 };
}
function stroke(pts, h, front, back) {
  for (const pass of [true, false]) {
    const st = pass ? front : back; if (!st) continue;
    ctx.beginPath(); let pen = false;
    for (const ll of pts) {
      const q = P(ll, h);
      if (!q.vis || q.front !== pass) { pen = false; continue; }
      pen ? ctx.lineTo(q.x, q.y) : ctx.moveTo(q.x, q.y); pen = true;
    }
    Object.assign(ctx, st); ctx.stroke();
  }
}
function rectLL(b, n = 10) {
  const [x0, y0, x1, y1] = b, o = [];
  for (let i = 0; i <= n; i++) o.push([x0 + (x1 - x0) * i / n, y0]);
  for (let i = 0; i <= n; i++) o.push([x1, y0 + (y1 - y0) * i / n]);
  for (let i = 0; i <= n; i++) o.push([x1 - (x1 - x0) * i / n, y1]);
  for (let i = 0; i <= n; i++) o.push([x0, y1 - (y1 - y0) * i / n]);
  return o;
}
function footprints(c) {
  let seed = 11; const rnd = () => (seed = (seed * 9301 + 49297) % 233280) / 233280;
  return Array.from({ length: 5 }, () => {
    const o = [c[0] + (rnd() - .5) * 2.2, c[1] + (rnd() - .5) * 1.6], a = -12 * D2R;
    return [[-1.5, -1.1], [1.5, -1.1], [1.5, 1.1], [-1.5, 1.1], [-1.5, -1.1]].map(([dx, dy]) =>
      [o[0] + (dx * Math.cos(a) - dy * Math.sin(a)) / Math.cos(o[1] * D2R), o[1] + dx * Math.sin(a) + dy * Math.cos(a)]);
  });
}
function arcPts(a, b, lift, n = 56) {
  const ip = d3.geoInterpolate(a, b); return Array.from({ length: n + 1 }, (_, i) => ({ ll: ip(i / n), h: lift * Math.sin(PI * i / n) }));
}
function drawLabel(t, x, y, col = 'rgba(242,238,228,.85)', align = 'left') {
  ctx.font = '500 10.5px "IBM Plex Mono", monospace'; ctx.textAlign = align; ctx.textBaseline = 'middle';
  ctx.lineWidth = 3; ctx.strokeStyle = 'rgba(0,10,45,.75)'; ctx.strokeText(t, x, y); ctx.fillStyle = col; ctx.fillText(t, x, y);
}
// labels are queued, then placed by priority so they never collide
let LQ = [];
const label = (t, x, y, col, align = 'left', prio = 3) => LQ.push({ t, x, y, col, align, prio });
function flushLabels() {
  ctx.font = '500 10.5px "IBM Plex Mono", monospace'; const placed = [];
  LQ.sort((a, b) => b.prio - a.prio).forEach(l => {
    const w = ctx.measureText(l.t).width, x0 = l.align === 'center' ? l.x - w / 2 : l.x, r = [x0 - 3, l.y - 8, x0 + w + 3, l.y + 8];
    if (placed.some(o => r[0] < o[2] && r[2] > o[0] && r[1] < o[3] && r[3] > o[1])) return;
    placed.push(r); drawLabel(l.t, l.x, l.y, l.col, l.align);
  });
  LQ = [];
}
const since = (n, now, dur = 900) => S.stage >= n && S.at[n] ? ease((now - S.at[n]) / dur) : 0;

function draw(now) {
  layout();
  ctx.setTransform(DPR, 0, 0, DPR, 0, 0); ctx.clearRect(0, 0, W, H);
  proj.scale(R).translate([cx, cy]).rotate([rot[0], rot[1], 0]);
  const m = S.mission, sl = S.slots, aoi = sl.aoi ? aoiOf(sl) : null, markers = [];

  // atmosphere
  let g = ctx.createRadialGradient(cx, cy, R * .96, cx, cy, R * 1.18);
  g.addColorStop(0, 'rgba(110,150,255,.32)'); g.addColorStop(.35, 'rgba(70,110,255,.10)'); g.addColorStop(1, 'rgba(60,100,255,0)');
  ctx.fillStyle = g; ctx.beginPath(); ctx.arc(cx, cy, R * 1.18, 0, 2 * PI); ctx.fill();
  // body lit from upper-left
  g = ctx.createRadialGradient(cx + LIGHT[0] * R * .55, cy - LIGHT[1] * R * .55, R * .05, cx, cy, R * 1.02);
  g.addColorStop(0, '#1d4fd6'); g.addColorStop(.45, '#0a2d9a'); g.addColorStop(.85, '#03155a'); g.addColorStop(1, '#010a33');
  ctx.beginPath(); ctx.arc(cx, cy, R, 0, 2 * PI); ctx.fillStyle = g; ctx.fill();
  // engraved graticule + brass equator
  ctx.beginPath(); gpath(grat); ctx.strokeStyle = 'rgba(242,238,228,.06)'; ctx.lineWidth = .6; ctx.stroke();
  ctx.beginPath(); gpath({ type: 'LineString', coordinates: Array.from({ length: 73 }, (_, i) => [-180 + i * 5, 0]) });
  ctx.strokeStyle = 'rgba(227,192,92,.22)'; ctx.lineWidth = .8; ctx.stroke();

  // halftone land, shaded by the same light
  if (dots) {
    const buckets = Array.from({ length: 7 }, () => []), base = Math.max(1, R / 210);
    for (let i = 0; i < dots.length; i += 2) {
      const l = dots[i], p = dots[i + 1], c = Math.cos(p), s = Math.sin(p), dl = l - V.lc, cd = Math.cos(dl);
      const Z = V.sp * s + V.cp * c * cd; if (Z <= 0.02) continue;
      const X = c * Math.sin(dl), Y = V.cp * s - V.sp * c * cd;
      const lit = Math.max(0, X * LIGHT[0] + Y * LIGHT[1] + Z * LIGHT[2]);
      const b = Math.min(6, Math.floor((0.12 + 0.88 * lit) * Math.min(1, Z * 2.2) * 7));
      buckets[b].push(cx + X * R, cy - Y * R, base * (.55 + .5 * Z));
    }
    buckets.forEach((arr, b) => {
      if (!arr.length) return; ctx.fillStyle = `rgba(242,238,228,${.1 + b * .12})`;
      for (let k = 0; k < arr.length; k += 3) { const sz = arr[k + 2]; ctx.fillRect(arr[k] - sz / 2, arr[k + 1] - sz / 2, sz, sz); }
    });
  }
  // terminator shade + rim
  g = ctx.createLinearGradient(cx + LIGHT[0] * R, cy - LIGHT[1] * R, cx - LIGHT[0] * R, cy + LIGHT[1] * R);
  g.addColorStop(0, 'rgba(1,8,40,0)'); g.addColorStop(.55, 'rgba(1,8,40,0)'); g.addColorStop(1, 'rgba(1,6,30,.55)');
  ctx.beginPath(); ctx.arc(cx, cy, R, 0, 2 * PI); ctx.fillStyle = g; ctx.fill();
  ctx.lineWidth = 1.2; ctx.strokeStyle = 'rgba(170,195,255,.35)'; ctx.stroke();

  // mission dial: 24 h UTC ring; contact windows are plotted on it
  const RD = R * 1.25, utc = (baseUTC + simT) % 1440, ang = mn => (mn / 1440) * 2 * PI - PI / 2;
  ctx.beginPath(); ctx.arc(cx, cy, RD, 0, 2 * PI); ctx.strokeStyle = 'rgba(227,192,92,.2)'; ctx.lineWidth = 1; ctx.stroke();
  for (let k = 0; k < 96; k++) {
    const a = ang(k * 15), len = k % 24 === 0 ? 9 : k % 4 === 0 ? 5 : 2.5;
    ctx.beginPath(); ctx.moveTo(cx + Math.cos(a) * RD, cy + Math.sin(a) * RD); ctx.lineTo(cx + Math.cos(a) * (RD + len), cy + Math.sin(a) * (RD + len));
    ctx.strokeStyle = `rgba(227,192,92,${k % 24 === 0 ? .55 : .25})`; ctx.lineWidth = 1; ctx.stroke();
  }
  if (R > 110) ['00', '06', '12', '18'].forEach((t, i) => { const a = ang(i * 360); label(t, cx + Math.cos(a) * (RD + 20), cy + Math.sin(a) * (RD + 20), 'rgba(227,192,92,.6)', 'center', 6); });
  if (S.windows) {
    const f = since(4, now, 1400) * 720;
    S.windows.forEach(w => {
      const arcs = (list, r, col, lw) => list.forEach(([a, b]) => {
        if (a > f) return; const s = ang(utcAt(a)), e = ang(utcAt(Math.min(b, f)));
        ctx.beginPath(); ctx.arc(cx, cy, r, s, e < s ? e + 2 * PI : Math.max(e, s + .015)); ctx.strokeStyle = col; ctx.lineWidth = lw; ctx.stroke();
      });
      arcs(w.dl, RD - 6, 'rgba(138,134,168,.9)', 2);
      arcs(w.img, RD, w.sat.id === m.primary ? '#e3c05c' : 'rgba(242,238,228,.75)', 3.5);
    });
  }
  { const a = ang(utc), x = cx + Math.cos(a) * (RD + 12), y = cy + Math.sin(a) * (RD + 12);
    ctx.save(); ctx.translate(x, y); ctx.rotate(a + PI / 2); ctx.beginPath(); ctx.moveTo(0, 6); ctx.lineTo(-4, -2); ctx.lineTo(4, -2); ctx.closePath(); ctx.fillStyle = '#e3c05c'; ctx.fill(); ctx.restore(); }

  // candidate places while choosing an area
  if (S.step === 'aoi' && sl.target && !sl.aoi) TARGETS[sl.target].places.forEach(k => {
    const q = P(centerOf(PLACES[k])); if (!q.front) return;
    const pr = (now / 1600) % 1;
    ctx.beginPath(); ctx.arc(q.x, q.y, 4 + pr * 12, 0, 2 * PI); ctx.strokeStyle = `rgba(227,192,92,${.7 * (1 - pr)})`; ctx.lineWidth = 1; ctx.stroke();
    ctx.beginPath(); ctx.arc(q.x, q.y, 3, 0, 2 * PI); ctx.fillStyle = '#e3c05c'; ctx.fill();
    label(PLACES[k].name, q.x + 10, q.y, '#e3c05c', 'left', 8); markers.push({ x: q.x, y: q.y, place: k, name: PLACES[k].name, sub: 'Click to choose this area' });
  });

  // footprints (catalog search)
  if (m && S.stage >= 2) footprints(m.c).forEach((poly, i) => {
    const a = clamp(since(2, now) * 5 - i); if (a) stroke(poly, 0, { strokeStyle: `rgba(205,201,234,${.6 * a})`, lineWidth: 1 }, null);
  });
  // AOI
  if (aoi) {
    const f = S.at.aoi ? ease((now - S.at.aoi) / 900) : 1, pts = rectLL(aoi.bbox);
    stroke(pts.slice(0, Math.ceil(pts.length * f)), 0, { strokeStyle: '#e3c05c', lineWidth: 1.6 }, null);
    const q = P(centerOf(aoi));
    if (q.front) {
      const pr = (now / 1500) % 1;
      ctx.beginPath(); ctx.arc(q.x, q.y, 6 + pr * 22, 0, 2 * PI); ctx.strokeStyle = `rgba(227,192,92,${.5 * (1 - pr)})`; ctx.lineWidth = 1; ctx.stroke();
      label(aoi.name.toUpperCase(), q.x + 16, q.y - 16, '#e3c05c', 'left', 10);
    }
  }

  // ground + cloud markers (labels only when relevant or hovered)
  const recWay = m && S.stage >= 6 ? m.paths[0].way : [];
  if (S.layers.ground) GROUND.forEach(gs => {
    const q = P(gs.ll); if (!q.front) return;
    const hot = recWay.includes(gs.id), near = m && S.stage >= 4 && m.stations.includes(gs.id);
    ctx.beginPath(); ctx.moveTo(q.x, q.y - 4.5); ctx.lineTo(q.x + 4, q.y); ctx.lineTo(q.x, q.y + 4.5); ctx.lineTo(q.x - 4, q.y); ctx.closePath();
    ctx.fillStyle = hot || near ? '#f2eee4' : 'rgba(205,201,234,.75)'; ctx.fill();
    if (hot || S.hover === gs.id) label(gs.name, q.x + 9, q.y, 'rgba(242,238,228,.9)', 'left', S.hover === gs.id ? 11 : 5);
    markers.push({ x: q.x, y: q.y, id: gs.id, name: gs.name, sub: 'Ground station · REFERENCE site' });
  });
  if (S.layers.cloud) CLOUD.forEach(c => {
    const q = P(c.ll); if (!q.front) return; const hot = recWay.includes(c.id);
    ctx.lineWidth = 1.2; ctx.strokeStyle = hot ? '#e3c05c' : 'rgba(242,238,228,.7)'; ctx.strokeRect(q.x - 4, q.y - 4, 8, 8);
    if (hot || S.hover === c.id) label(c.name, q.x + 9, q.y, hot ? '#e3c05c' : 'rgba(242,238,228,.9)', 'left', S.hover === c.id ? 11 : 5);
    markers.push({ x: q.x, y: q.y, id: c.id, name: c.name, sub: 'Cloud region · illustrative' });
  });

  // satellites
  const focus = m ? m.sats : sl.sensor ? SENSORS[sl.sensor].sats : sl._preview ? SENSORS[sl._preview].sats : null;
  if (S.layers.sats) SATS.forEach(sat => {
    const inF = focus && focus.includes(sat.id), pri = m && m.primary === sat.id;
    if (inF) {
      const f = m && S.stage >= 3 ? since(3, now) : S.at.sensor ? ease((now - S.at.sensor) / 900) : 1, ring = ringLL(sat, simT);
      stroke(ring.slice(0, Math.ceil(ring.length * f)), sat.h, { strokeStyle: pri ? 'rgba(227,192,92,.75)' : 'rgba(242,238,228,.38)', lineWidth: pri ? 1.2 : .8 }, { strokeStyle: 'rgba(242,238,228,.07)', lineWidth: .6 });
    }
    for (let k = 14; k > 0; k--) {   // short trail
      const a = P(satLL(sat, simT - k * .9), sat.h), b = P(satLL(sat, simT - (k - 1) * .9), sat.h);
      if (!a.vis || !b.vis) continue; ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y);
      ctx.strokeStyle = `rgba(${pri ? '227,192,92' : '242,238,228'},${(1 - k / 14) * (focus && !inF ? .2 : .6)})`; ctx.lineWidth = 1.4; ctx.stroke();
    }
    const ll = satLL(sat, simT), q = P(ll, sat.h); if (!q.vis) return;
    if (m && inF && S.stage >= 4 && q.front) {   // access rays
      const a = since(4, now), aq = P(m.c);
      if (aq.front && d3.geoDistance(ll, m.c) < .5) { ctx.beginPath(); ctx.moveTo(q.x, q.y); ctx.lineTo(aq.x, aq.y); ctx.strokeStyle = pri ? `rgba(227,192,92,${.85 * a})` : `rgba(242,238,228,${.5 * a})`; ctx.lineWidth = 1; ctx.stroke(); }
      m.stations.map(byId).forEach(gs => { const gq = P(gs.ll); if (!gq.front || d3.geoDistance(ll, gs.ll) > .38) return;
        ctx.setLineDash([3, 3]); ctx.beginPath(); ctx.moveTo(q.x, q.y); ctx.lineTo(gq.x, gq.y); ctx.strokeStyle = `rgba(205,201,234,${.9 * a})`; ctx.lineWidth = 1; ctx.stroke(); ctx.setLineDash([]); });
    }
    const glow = ctx.createRadialGradient(q.x, q.y, 0, q.x, q.y, 9);
    glow.addColorStop(0, pri ? 'rgba(227,192,92,.55)' : 'rgba(242,238,228,.4)'); glow.addColorStop(1, 'rgba(242,238,228,0)');
    ctx.globalAlpha = q.front ? (focus && !inF ? .45 : 1) : .35;
    ctx.fillStyle = glow; ctx.beginPath(); ctx.arc(q.x, q.y, 9, 0, 2 * PI); ctx.fill();
    ctx.fillStyle = pri ? '#e3c05c' : '#f2eee4'; ctx.beginPath(); ctx.arc(q.x, q.y, pri ? 2.8 : 2.2, 0, 2 * PI); ctx.fill(); ctx.globalAlpha = 1;
    if (q.front && (pri || S.hover === sat.id)) label(sat.name, q.x + 10, q.y - 8, pri ? '#e3c05c' : 'rgba(242,238,228,.9)', 'left', S.hover === sat.id ? 11 : 7);
    markers.push({ x: q.x, y: q.y, id: sat.id, name: sat.name, sub: `${sat.kind === 'sar' ? 'SAR' : 'Optical'} · public mission · REFERENCE` });
  });

  // candidate execution paths
  if (m && S.stage >= 5) {
    const f5 = since(5, now, 1200), rec = S.stage >= 6, f6 = since(6, now);
    m.paths.slice().reverse().forEach((p, idx) => {
      const legs = p.way.slice(0, -1).map((w, i) => [w === 'aoi' ? m.c : byId(w).ll, byId(p.way[i + 1]).ll]).filter(([a, b]) => d3.geoDistance(a, b) > .01);
      const gold = p.rec && rec, lift = p.rec ? .1 : .05 + idx * .025;
      legs.forEach((leg, li) => {
        const pts = arcPts(leg[0], leg[1], lift), k = Math.max(1, Math.floor(pts.length * clamp(f5 * legs.length - li)));
        ctx.beginPath(); let pen = false;
        for (let i = 0; i < k; i++) { const q = P(pts[i].ll, pts[i].h); if (!q.vis) { pen = false; continue; } pen ? ctx.lineTo(q.x, q.y) : ctx.moveTo(q.x, q.y); pen = true; }
        if (!gold) ctx.setLineDash([4, 5]);
        ctx.strokeStyle = gold ? '#e3c05c' : `rgba(242,238,228,${rec ? .18 : .5})`; ctx.lineWidth = gold ? 2 : 1; ctx.stroke(); ctx.setLineDash([]);
        if (gold && f6 > .5) {
          const ph = reduce || !playing ? .5 : ((now / 2400) + li * .4) % 1, pt = pts[Math.floor(ph * (pts.length - 1))], q = P(pt.ll, pt.h);
          if (q.vis) { ctx.beginPath(); ctx.arc(q.x, q.y, 3, 0, 2 * PI); ctx.fillStyle = '#fff6da'; ctx.fill(); }
          if (li === 0) { const mid = pts[Math.floor(pts.length * .55)], q2 = P(mid.ll, mid.h); if (q2.vis) label('A · RECOMMENDED', q2.x + 10, q2.y - 10, '#e3c05c', 'left', 9); }
        }
      });
    });
  }

  // pick ghost
  if (S.picking && S.pointer) {
    const ll = proj.invert(S.pointer);
    if (ll && d3.geoDistance(ll, [-rot[0], -rot[1]]) < PI / 2) stroke(rectLL([ll[0] - .5, ll[1] - .35, ll[0] + .5, ll[1] + .35]), 0, { strokeStyle: 'rgba(227,192,92,.8)', lineWidth: 1.2 }, null);
  }
  flushLabels();
  S.markers = markers;
}

function frame(now) {
  const dt = Math.min(64, now - lastFrame); lastFrame = now;
  if (playing) simT += dt / 1000 * SPEED;
  if (!dragging) {
    if (!S.slots.aoi && S.step !== 'aoi' && playing && now - lastUser > 3000) target[0] += dt * .005;
    rot[0] += (((target[0] - rot[0] + 540) % 360) - 180) * .06; rot[1] += (target[1] - rot[1]) * .06;
  }
  draw(now);
  const u = (baseUTC + simT) % 1440;
  $('#clock').textContent = `${String(Math.floor(u / 60)).padStart(2, '0')}:${String(Math.floor(u % 60)).padStart(2, '0')} UTC`;
  if (S.windows) { const hd = $('#tlHead'), tr = $('.tl-track'); if (hd && tr) hd.style.left = `${tr.offsetLeft + clamp((simT - S.t0) / 720) * tr.offsetWidth}px`; }
  if (alive) rafId = requestAnimationFrame(frame);
}

/* pointer: drag to rotate, hover tooltips, click to pick */
const tip = $('#tip');
cv.addEventListener('pointerdown', e => { dragging = true; moved = 0; cv.setPointerCapture(e.pointerId); cv._p = [e.clientX, e.clientY]; });
cv.addEventListener('pointermove', e => {
  const b = cv.getBoundingClientRect(), x = e.clientX - b.left, y = e.clientY - b.top; S.pointer = [x, y];
  if (dragging) {
    const dx = e.clientX - cv._p[0], dy = e.clientY - cv._p[1]; moved += Math.abs(dx) + Math.abs(dy);
    rot[0] += dx * 80 / R * .5; rot[1] = clamp(rot[1] - dy * 80 / R * .5, -75, 75); target = [rot[0], rot[1]]; cv._p = [e.clientX, e.clientY]; return;
  }
  const hit = (S.markers || []).find(mk => Math.hypot(mk.x - x, mk.y - y) < 10);
  S.hover = hit ? hit.id || hit.place : null;
  cv.style.cursor = S.picking ? 'crosshair' : hit ? 'pointer' : 'grab';
  if (hit) { tip.innerHTML = `${esc(hit.name)}<small>${esc(hit.sub)}</small>`; tip.style.left = `${Math.min(x + 14, W - 220)}px`; tip.style.top = `${y + 12}px`; tip.classList.add('on'); }
  else tip.classList.remove('on');
});
cv.addEventListener('pointerleave', () => { tip.classList.remove('on'); S.hover = null; S.pointer = null; });
['pointerup', 'pointercancel'].forEach(t => cv.addEventListener(t, e => {
  if (!dragging) return; dragging = false; lastUser = performance.now();
  if (moved > 5 || t === 'pointercancel') return;
  const b = cv.getBoundingClientRect(), x = e.clientX - b.left, y = e.clientY - b.top;
  const hit = (S.markers || []).find(mk => mk.place && Math.hypot(mk.x - x, mk.y - y) < 12);
  if (hit) return userPick('aoi', hit.place, PLACES[hit.place].name);
  if (S.picking) {
    const ll = proj.invert([x, y]);
    if (!ll || d3.geoDistance(ll, [-rot[0], -rot[1]]) > PI / 2) return;
    const name = `Custom area · ${Math.abs(ll[1]).toFixed(1)}°${ll[1] >= 0 ? 'N' : 'S'} ${Math.abs(ll[0]).toFixed(1)}°${ll[0] >= 0 ? 'E' : 'W'}`;
    setPicking(false);
    if (!S.slots.target) S.slots.target = 'change';
    userPick('aoi', { key: 'custom', name, bbox: [ll[0] - .5, ll[1] - .35, ll[0] + .5, ll[1] + .35] }, name);
  }
}));
function setPicking(on) { S.picking = on; stage.classList.toggle('picking', on); $('#pickBtn').setAttribute('aria-pressed', on); }
$('#pickBtn').addEventListener('click', () => setPicking(!S.picking));
onWin('keydown', e => { if (e.key === 'Escape') setPicking(false); });
$('#pauseBtn').addEventListener('click', () => {
  playing = !playing; $('#pauseBtn').setAttribute('aria-label', playing ? 'Pause motion' : 'Resume motion');
  $('#pauseIcon').innerHTML = playing ? '<path d="M2 1v8M8 1v8" stroke="currentColor" stroke-width="1.6"/>' : '<path d="M2 1l7 4-7 4z" fill="currentColor"/>';
});
function focusOn(ll, dx = 0) { target = [-ll[0] + dx, clamp(-ll[1] * .8, -60, 60)]; }

/* ================= rail ================= */
const STEPS = ['Understand', 'Search', 'Propagate', 'Contacts', 'Compare', 'Recommend'];
$('#rail').innerHTML = STEPS.map((s, i) => `<li data-i="${i + 1}"><span>${s}</span></li>`).join('');
function setStage(n) {
  S.stage = n; S.at[n] = performance.now(); $('#rail').classList.toggle('on', n > 0);
  $$('#rail li').forEach(li => { const i = +li.dataset.i; li.className = i < n || (S.done && i <= n) ? 'done' : i === n ? 'active' : ''; });
}

/* ================= stack lens ================= */
function renderStack() {
  const m = S.mission, svg = $('#stack');
  if (!m || S.stage < 5) { svg.innerHTML = `<text x="470" y="170" text-anchor="middle" fill="rgba(226,222,212,.7)" font-family="Inter Tight" font-size="15">The infrastructure stack appears once Nomos compares execution paths.</text>`; return; }
  const cols = ['Request', 'Space segment', 'Ground segment', 'Compute', 'Delivery'], X = [86, 278, 470, 662, 854], Y = [100, 190, 280], rec = S.stage >= 6;
  let g = cols.map((c, i) => `<text x="${X[i]}" y="30" text-anchor="middle" fill="rgba(216,212,203,.55)" font-family="IBM Plex Mono" font-size="10" letter-spacing="1.4">${c.toUpperCase()}</text><line x1="${X[i]}" y1="46" x2="${X[i]}" y2="320" stroke="rgba(255,255,255,.05)"/>`).join('');
  const node = (x, y, t, tr, hot) => `<rect x="${x - 86}" y="${y - 25}" width="172" height="50" rx="8" fill="rgba(0,16,69,.88)" stroke="${hot ? '#e3c05c' : 'rgba(255,255,255,.16)'}" ${tr === 'PLANNED' ? 'stroke-dasharray="3 3"' : ''}/>
    <text x="${x}" y="${tr ? y - 3 : y + 4}" text-anchor="middle" fill="${hot ? '#f2eee4' : 'rgba(226,222,212,.82)'}" font-family="Inter Tight" font-size="11.5">${esc(t.length > 27 ? t.slice(0, 26) + '…' : t)}</text>
    ${tr ? `<text x="${x}" y="${y + 14}" text-anchor="middle" fill="${hot ? '#e3c05c' : 'rgba(216,212,203,.5)'}" font-family="IBM Plex Mono" font-size="8.5" letter-spacing="1">${tr}</text>` : ''}`;
  const link = (x1, y1, x2, y2, hot, d) => `<path d="M${x1} ${y1} C ${(x1 + x2) / 2} ${y1}, ${(x1 + x2) / 2} ${y2}, ${x2} ${y2}" fill="none" stroke="${hot ? '#e3c05c' : 'rgba(255,255,255,.28)'}" stroke-width="${hot ? 1.8 : 1}" ${d ? 'stroke-dasharray="4 4"' : ''}/>`;
  m.paths.forEach((p, r) => {
    const hot = p.rec && rec, y = Y[r];
    g += link(X[0] + 86, Y[1], X[1] - 86, y, hot, !p.rec);
    for (let i = 1; i < 4; i++) g += link(X[i] + 86, y, X[i + 1] - 86, y, hot, !p.rec);
    p.nodes.forEach((n, i) => g += node(X[i + 1], y, n, p.truth[i], hot));
  });
  g += node(X[0], Y[1], m.tgt.objective, '', true);
  svg.innerHTML = g;
}
$$('.seg button').forEach(b => b.addEventListener('click', () => {
  $$('.seg button').forEach(x => x.setAttribute('aria-selected', x === b)); S.lens = b.dataset.lens; stage.dataset.lens = S.lens; renderStack();
}));

/* ================= brief ================= */
const fmtIn = mn => { mn = Math.max(0, Math.round(mn)); return `${Math.floor(mn / 60)}h ${String(mn % 60).padStart(2, '0')}m`; };
function renderBrief(fresh) {
  const sl = S.slots, m = S.mission, n = S.stage, aoi = sl.aoi ? aoiOf(sl) : null;
  const tgt = sl.target && TARGETS[sl.target];
  const title = m ? m.title : tgt && aoi ? `${tgt.label} · ${aoi.name}` : tgt ? tgt.label : 'New mission';
  const cover = m ? m.cover : sl.intent === 'respond' ? 'irosa-solar-array-hero.jpg' : 'network/cloud-nodes.png';
  const row = (k, lbl, val) => `<dt>${lbl}</dt><dd class="${val ? (fresh === k ? 'fresh' : '') : 'pend'}">${val || ''}</dd>`;
  const sec = (h, ready, body, extra = '') => `<section class="b-sec"><h3><span class="eyebrow">${h}</span>${extra}</h3>${ready ? body : '<div class="ph-lines"><div style="width:82%"></div><div style="width:56%"></div></div>'}</section>`;
  let feas = '';
  if (m && n >= 6 && S.windows) {
    const nowK = simT - S.t0, pri = S.windows.find(w => w.sat.id === m.primary);
    const ni = pri.img.find(([a]) => a > nowK), nd = S.windows.flatMap(w => w.dl).filter(([a]) => a > nowK).sort((a, b) => a[0] - b[0])[0];
    feas = `<div class="feas">
      <div><span>Next ${satById(m.primary).name} pass</span><b>${ni ? 'in ' + fmtIn(ni[0] - nowK) : '> 12 h'}</b>${chip('SIMULATED')}</div>
      <div><span>Next downlink contact</span><b>${nd ? 'in ' + fmtIn(nd[0] - nowK) : '> 12 h'}</b>${chip('SIMULATED')}</div>
      <div><span>Catalog</span><b style="font-size:12px">${esc(m.sen.coll)}</b>${chip('REFERENCE')}</div>
      <div><span>Cost</span><b>—</b>${chip('UNAVAILABLE')}</div></div>
      <div class="tl"><div class="tl-legend"><span><i style="background:var(--gold)"></i>imaging pass</span><span><i style="border:1px solid var(--silver)"></i>downlink</span></div>
      <div class="tl-rows">${S.windows.map(w => `<div class="tl-row"><span class="lab">${w.sat.name}</span><div class="tl-track">
        ${w.dl.map(([a, b]) => `<i class="tl-bar dl" style="left:${a / 7.2}%;width:${Math.max(.8, (b - a) / 7.2)}%"></i>`).join('')}
        ${w.img.map(([a, b]) => `<i class="tl-bar ${w.sat.id === m.primary ? 'pri' : ''}" style="left:${a / 7.2}%;width:${Math.max(.8, (b - a) / 7.2)}%"></i>`).join('')}
      </div></div>`).join('')}<div class="tl-head" id="tlHead"></div></div>
      <div class="tl-axis"><span></span><div><span>now</span><span>+3 h</span><span>+6 h</span><span>+9 h</span><span>+12 h</span></div></div></div>
      <p class="why">Preview windows use illustrative orbits. The full brief calculates real contact windows with SGP4 from CelesTrak elements.</p>`;
  }
  $('#tab-brief').innerHTML = `
    <div class="cover" style="background-image:url('${IMG}${cover}')"><div class="cover-in">
      <span class="id">${m ? m.key : 'msn_draft'} · private</span><h2>${esc(title)}</h2>
      ${S.realId ? '<span class="chip chip-live">SAVED · PRIVATE</span> ' : ''}${m && S.done ? '<span class="chip chip-simulated">PREVIEW</span>' : `<span class="chip chip-estimated">${m ? 'PLANNING' : 'DRAFTING WITH YOU'}</span>`}
    </div></div>
    ${sec('Mission spec', true, `<dl class="kv">
      ${row('target', 'Objective', tgt && tgt.objective)}
      ${row('aoi', 'Area', aoi && `${esc(aoi.name)}<br><span class="mono" style="font-size:10.5px;color:var(--text-3)">bbox ${aoi.bbox.map(v => v.toFixed(2)).join(', ')}</span>`)}
      ${row('sensor', 'Sensor', sl.sensor && SENSORS[sl.sensor].label)}
      ${row('freshness', 'Freshness', sl.freshness && FRESH[sl.freshness])}
      ${row('priority', 'Priority', sl.priority)}
      ${row('delivery', 'Deliver to', sl.delivery)}</dl>`)}
    ${sec('Recommended execution path', m && n >= 6, m && `<ol class="route">${m.paths[0].nodes.map((x, i) => `<li>${esc(x)}<br>${chip(m.paths[0].truth[i])}</li>`).join('')}</ol><p class="why">${m.paths[0].why}</p>`, m && n >= 6 ? '<span class="eyebrow" style="color:var(--gold)">Path A</span>' : '')}
    ${sec('Alternatives', m && n >= 5, m && m.paths.slice(1).map(p => `<div class="alt"><header><span>Path ${p.id} · ${p.name}</span>${chip('PLANNED')}</header><span class="r">${p.why}</span></div>`).join(''))}
    ${sec('Feasibility', m && n >= 6, feas)}
    ${sec('Assumptions & unavailable integrations', m && n >= 6, `<ul class="bul">
      <li><span>Uses public archive scenes and natural passes; no new capture is requested.</span>${chip('REFERENCE')}</li>
      <li><span>Satellite tasking requires a provider integration.</span>${chip('PLANNED')}</li>
      <li><span>Ground-station reservation is not performed.</span>${chip('PLANNED')}</li>
      <li><span>Processing time is modelled from scene size.</span>${chip('ESTIMATED')}</li>
      <li><span>Pricing has no real source yet.</span>${chip('UNAVAILABLE')}</li>
      ${sl.sensor === 'optical' ? `<li><span>Optical scenes may be obscured by cloud or smoke.</span>${chip('ESTIMATED')}</li>` : ''}</ul>`)}
    ${m && S.done && S.realId ? `<div class="b-acts"><a class="btn primary" href="/missions/${encodeURIComponent(S.realId)}" data-nav>Open source-backed brief</a></div>` : ''}
    ${m && S.done && S.realError ? `<div class="pending">${esc(S.realError)}</div>` : ''}`;
  $('#tab-evidence').innerHTML = !m || n < 2 ? `<div class="pending">Sources, catalog queries and orbital elements appear here as Nomos plans.</div>` : `<ul class="ev">
    <li><span class="src">Microsoft Planetary Computer · STAC</span><span class="d">${m.sen.coll} · queried by the full brief</span>${chip('REFERENCE')}</li>
    ${n >= 3 ? `<li><span class="src">CelesTrak GP elements</span><span class="d">${m.sats.map(id => satById(id).name).join(' · ')}</span>${chip('REFERENCE')}</li>
    <li><span class="src">Orbit propagation</span><span class="d">Preview: illustrative circular orbits · full brief: SGP4</span>${chip('SIMULATED')}</li>` : ''}
    ${n >= 4 ? `<li><span class="src">Ground station registry</span><span class="d">${m.stations.map(id => byId(id).name).join(' · ')}</span>${chip('REFERENCE')}</li>` : ''}
    ${n >= 5 ? `<li><span class="src">Provider registry</span><span class="d">tasking + onboard compute: no connected integration</span>${chip('UNAVAILABLE')}</li>` : ''}</ul>`;
  $('#tab-trace').innerHTML = S.log.length ? `<ul class="log">${S.log.map(l => `<li><time>${l.t}</time>${esc(l.m)}</li>`).join('')}</ul><p style="font-size:12px;color:var(--text-3)">Preview steps. The saved mission keeps its own append-only event trail.</p>` : `<div class="pending">Every decision Nomos makes is recorded here.</div>`;
}
const log = m => { S.log.push({ t: new Date().toTimeString().slice(0, 8), m }); };
$$('.tabs button').forEach(b => b.addEventListener('click', () => {
  $$('.tabs button').forEach(x => x.setAttribute('aria-selected', x === b)); $$('.tabpane').forEach(p => p.classList.toggle('on', p.id === 'tab-' + b.dataset.tab));
}));

/* ================= chat primitives ================= */
const thread = $('#thread');
const scrollDown = el => {
  const top = el && el.offsetHeight > thread.clientHeight - 24 ? el.offsetTop - 12 : thread.scrollHeight;
  thread.scrollTo({ top, behavior: reduce ? 'auto' : 'smooth' });
};
const wait = ms => new Promise(r => setTimeout(r, reduce ? Math.min(ms, 80) : ms));
function userMsg(text) {
  const el = document.createElement('div'); el.className = 'msg user'; el.innerHTML = `<div class="body">${esc(text)}</div>`;
  thread.appendChild(el); scrollDown();
}
async function bot(html, { delay = 650 } = {}) {
  const tok = S.token, el = document.createElement('div'); el.className = 'msg bot';
  el.innerHTML = `${RECORD(30, 'spin-fast')}<div class="body"><div class="typing"><i></i><i></i><i></i></div></div>`;
  thread.appendChild(el); scrollDown(); await wait(delay);
  if (tok !== S.token) { el.remove(); throw new Error('cancelled'); }
  $('.record', el).className = 'record av spin'; $('.body', el).innerHTML = html; scrollDown(el); return el;
}
function choices(el, list, onPick) {
  const box = document.createElement('div'); box.className = 'choices';
  box.innerHTML = list.map((c, i) => `<button class="choice ${c.rec ? 'rec' : ''} ${c.ghost ? 'ghost' : ''}" data-i="${i}">${esc(c.label)}</button>`).join('');
  $('.body', el).appendChild(box); scrollDown(el);
  $$('button', box).forEach(b => b.addEventListener('click', () => { if (S.running) return; box.classList.add('locked'); b.classList.add('picked'); onPick(list[+b.dataset.i], box); }));
  return box;
}
const lockAll = () => $$('.choices:not(.locked), .cards:not(.locked)', thread).forEach(b => b.classList.add('locked'));
const safe = p => p && p.catch && p.catch(() => {});

/* ================= the conversation ================= */
const ORDER = ['intent', 'target', 'aoi', 'sensor', 'freshness', 'priority', 'delivery'];
const nextMissing = () => ORDER.find(k => !S.slots[k]);
function setSlot(k, v) {
  S.slots[k] = v;
  if (k === 'target') S.slots.intent = TARGETS[v].intent;
  if (k === 'aoi') { S.at.aoi = performance.now(); focusOn(centerOf(aoiOf(S.slots))); }
  if (k === 'sensor') S.at.sensor = performance.now();
  renderBrief(k);
}
function userPick(k, v, text) { if (S.running) return; lockAll(); userMsg(text); S.step = k; setSlot(k, v); safe(proceed()); }

async function ask(k) {
  S.step = k; const sl = S.slots;
  if (k === 'intent') {
    const el = await bot(`<div class="txt">Hi, I'm Nomos. Tell me what you need from space and I'll work out how satellites, ground stations and cloud compute can deliver it — and show you every assumption along the way.</div><div class="txt">What are we planning?</div>`);
    const box = document.createElement('div'); box.className = 'cards';
    box.innerHTML = Object.entries(INTENTS).map(([key, it]) => `<button class="card" data-k="${key}"><div class="ph"><img src="${IMG}${it.img}" alt=""></div><div class="cb"><div class="ct">${it.label}</div><div class="cs">${it.sub}</div></div></button>`).join('');
    $('.body', el).appendChild(box); scrollDown(el);
    $$('.card', box).forEach(b => b.addEventListener('click', () => {
      if (S.running) return; box.classList.add('locked'); b.classList.add('picked'); const key = b.dataset.k; userMsg(INTENTS[key].label);
      if (key === 'explore') return safe(exploreNetwork());
      if (key === 'free') { $('#input').focus(); return safe(bot(`<div class="txt">Go ahead — describe the outcome, the place and how soon you need it. I'll fill in what I can and ask about the rest.</div>`)); }
      setSlot('intent', key); safe(proceed());
    }));
  } else if (k === 'target') {
    const opts = Object.entries(TARGETS).filter(([, t]) => t.intent === sl.intent);
    const el = await bot(`<div class="txt">${sl.intent === 'respond' ? 'What kind of event are we responding to?' : 'What should I watch for?'}</div>`);
    choices(el, opts.map(([key, t]) => ({ label: t.label, key })), c => userPick('target', c.key, c.label));
  } else if (k === 'aoi') {
    const t = TARGETS[sl.target], c0 = centerOf(PLACES[t.places[0]]);
    focusOn(c0, 20);
    const el = await bot(`<div class="txt">Where? Pick a place below, tap a gold marker on the globe, or click anywhere on it to drop your own area of interest.</div>`);
    choices(el, [...t.places.map(p => ({ label: PLACES[p].name, key: p })), { label: 'Pick on globe', key: '_pick', ghost: true }], (c, box) => {
      if (c.key === '_pick') { setPicking(true); box.classList.remove('locked'); $$('.choice', box).forEach(b => b.classList.remove('picked')); return; }
      userPick('aoi', c.key, c.label);
    });
  } else if (k === 'sensor') {
    const t = TARGETS[sl.target], r = SENSORS[t.sensor], other = t.sensor === 'sar' ? 'optical' : 'sar';
    S.slots._preview = t.sensor; S.at.sensor = performance.now();
    const el = await bot(`<div class="txt">For ${t.label.toLowerCase()} I'd use <strong>${r.label}</strong> — it ${r.why}. Those satellites' orbits are now drawn on the globe. Use that?</div>`);
    choices(el, [{ label: r.label, key: t.sensor, rec: true }, { label: SENSORS[other].label, key: other }, { label: 'Both', key: 'both' }], c => userPick('sensor', c.key, c.label));
  } else if (k === 'freshness') {
    const el = await bot(`<div class="txt">How fresh does the imagery need to be?</div>`);
    choices(el, Object.entries(FRESH).map(([key, label]) => ({ label, key })), c => userPick('freshness', c.key, c.label));
  } else if (k === 'priority') {
    const el = await bot(`<div class="txt">What matters most for this mission?</div>`);
    choices(el, ['Fastest', 'Cheapest', 'Most reliable'].map(label => ({ label, key: label })), c => userPick('priority', c.key, c.label));
  } else if (k === 'delivery') {
    const el = await bot(`<div class="txt">Last one — where should results go?</div>`);
    choices(el, ['Cloud bucket', 'Webhook', 'Email brief'].map(label => ({ label, key: label })), c => userPick('delivery', c.key, c.label));
  }
}

async function proceed() {
  const sl = S.slots, last = S.step;
  if (last === 'freshness' && sl.freshness === 'asap' && !S.noted.asap) { S.noted.asap = 1;
    await bot(`<div class="txt note">Heads-up: a brand-new capture needs satellite tasking, which is <strong>PLANNED</strong> — Nomos has no tasking integration yet. I'll plan from the latest archive scene plus the next natural pass instead.</div>`, { delay: 500 }); }
  if (last === 'priority' && sl.priority === 'Cheapest' && !S.noted.cheap) { S.noted.cheap = 1;
    await bot(`<div class="txt note">Pricing has no real source yet, so cost will show <strong>UNAVAILABLE</strong>. I'll favour openly available data, which is the cheapest path today.</div>`, { delay: 500 }); }
  const k = nextMissing();
  return k ? ask(k) : confirmSpec();
}

async function confirmSpec() {
  S.step = 'confirm'; const sl = S.slots, a = aoiOf(sl);
  const rows = [['target', 'Objective', TARGETS[sl.target].objective], ['aoi', 'Area', a.name], ['sensor', 'Sensor', SENSORS[sl.sensor].label], ['freshness', 'Freshness', FRESH[sl.freshness]], ['priority', 'Priority', sl.priority], ['delivery', 'Deliver to', sl.delivery]];
  const el = await bot(`<div class="txt">Here's the mission as I understand it. Change anything, or let me plan it.</div>
    <div class="spec"><div class="spec-h"><span class="eyebrow">Mission spec</span><span class="eyebrow">${a.key === 'custom' ? 'custom area' : 'draft'}</span></div><dl>
    ${rows.map(([k, l, v]) => `<dt>${l}</dt><dd>${esc(v)}</dd><span class="chg"><button data-k="${k}" data-l="${l}">Change</button></span>`).join('')}
    </dl><div class="spec-f"><button class="btn primary" data-go>Plan this mission</button><button class="btn" data-reset>Start over</button></div></div>`);
  $$('.chg button', el).forEach(b => b.addEventListener('click', () => {
    if (S.running) return; $$('button', el).forEach(x => x.disabled = true); const k = b.dataset.k;
    userMsg(`Change ${b.dataset.l.toLowerCase()}`);
    delete S.slots[k]; if (k === 'target') delete S.slots.aoi; renderBrief(); safe(ask(k));
  }));
  $('[data-go]', el).addEventListener('click', () => { $$('button', el).forEach(x => x.disabled = true); userMsg('Plan this mission'); safe(plan()); });
  $('[data-reset]', el).addEventListener('click', () => reset());
}

async function exploreNetwork() {
  S.layers = { sats: true, ground: true, cloud: true }; $$('.layer').forEach(b => b.setAttribute('aria-pressed', 'true'));
  target = [rot[0] + 60, -20];
  const el = await bot(`<div class="txt">This is the network Nomos reasons over today. Hover any marker on the globe to see its source. Satellites and ground sites are real public infrastructure; compute regions stay illustrative until provider records are connected.</div>
    <div class="strip">
      <figure><img src="${IMG}network/cloud-nodes.png" alt="Two Earth-observation satellites above cloud cover"><figcaption>Satellites<span>${SATS.length} · REFERENCE</span></figcaption></figure>
      <figure><img src="${IMG}network/ground-stations.png" alt="Ground-station antenna field"><figcaption>Ground stations<span>${GROUND.length} · REFERENCE</span></figcaption></figure>
      <figure><img src="${IMG}control-room-tunnel.png" alt="Archival control-room imagery"><figcaption>Compute<span>${CLOUD.length} · illustrative</span></figcaption></figure>
    </div><div class="txt" style="margin-top:12px">Want to plan something on it?</div>`);
  choices(el, [{ label: 'Monitor a place', key: 'monitor' }, { label: 'Respond to an event', key: 'respond' }], c => userPick('intent', c.key, c.label));
}

/* ================= planning run ================= */
async function plan({ fast = false } = {}) {
  S.running = true; const tok = S.token, w = ms => wait(fast ? ms * .3 : ms);
  const m = S.mission = buildMission(S.slots); S.done = false; S.windows = null; S.log = []; S.realId = null; S.realError = null;
  const real = fast ? null : deps.createMission(missionPayload(S.slots, m)).then(id => ({ id }), err => ({ err }));
  let el;
  try { el = await bot(`<ul class="trace"></ul>`, { delay: 400 }); } catch (e) { S.running = false; throw e; }
  const tr = $('.trace', el);
  const lines = [
    ['Understand', `${m.tgt.objective} · ${m.aoi.name} · ${S.slots.priority.toLowerCase()}`],
    ['Search', `Catalog · Planetary Computer STAC · ${m.sen.coll}`],
    ['Propagate', `${m.sats.length} public missions · illustrative orbits in this preview`],
    ['Contacts', `Preview imaging passes and downlink contacts, next 12 h`],
    ['Compare', `${m.paths.length} execution paths vs. priority and available integrations`],
    ['Recommend', `Path A · ${m.paths[0].name.toLowerCase()}`],
  ];
  for (let i = 0; i < lines.length; i++) {
    if (tok !== S.token) return;
    const li = document.createElement('li'); li.className = 'run'; li.innerHTML = `<span class="s">${lines[i][0]}</span><span>${esc(lines[i][1])}</span>`;
    tr.appendChild(li); scrollDown(); setStage(i + 1); log(`${lines[i][0].toLowerCase()} · ${lines[i][1]}`);
    if (i === 0) focusOn(m.c);
    if (i === 3) { S.t0 = simT; S.windows = contactWindows(m, simT); }
    if (i === 4) focusOn(m.c, 28);
    if (i === 5) focusOn(m.c, 16);
    renderBrief(); renderStack();
    await w(i === 0 ? 800 : 1300); li.className = '';
  }
  if (tok !== S.token) return;
  const res = real ? await real : null;
  if (tok !== S.token) return;
  if (res && res.id) { S.realId = res.id; S.mine.unshift({ id: res.id, title: m.title }); S.current = 'mine:' + res.id; renderLists(); log(`saved private mission ${res.id}`); }
  if (res && res.err) S.realError = 'The planning API could not save this mission right now, so only the preview is shown. Try again in a moment.';
  S.done = true; S.running = false; setStage(6); renderBrief(); renderStack();
  const saved = S.realId
    ? `<div class="txt">I saved this as a <strong>private mission</strong>. Its full brief searches the public catalog, calculates real contact windows and compares infrastructure with every source cited.</div>`
    : fast ? `<div class="txt note">This guided example is a preview only. Plan your own mission to get a saved, source-backed brief.</div>`
    : `<div class="txt note">${esc(S.realError || '')}</div>`;
  const done = await bot(`<div class="txt"><strong>Preview recommendation — ${esc(m.paths[0].name)}.</strong> ${m.paths[0].why}</div>
    <div class="txt">Paths B and C stay labelled <strong>PLANNED</strong>: they need provider integrations Nomos does not pretend to have.</div>${saved}
    ${S.realId ? `<div class="acts" style="margin-top:12px"><a class="btn primary" href="/missions/${encodeURIComponent(S.realId)}" data-nav>Open source-backed brief</a></div>` : ''}`, { delay: 500 });
  followUps(done);
}
function followUps(el) {
  choices(el, [{ label: 'Why path A?', key: 'why' }, { label: 'When is the next pass?', key: 'pass' }, { label: 'Compare alternatives', key: 'alt' }, { label: 'New mission', key: 'new', ghost: true }], c => {
    if (c.key === 'new') return reset(); userMsg(c.label); safe(answerFollow(c.key));
  });
}
async function answerFollow(k) {
  const m = S.mission; let el;
  if (k === 'why') el = await bot(`<div class="txt">${m.paths[0].why} It is also the only path that runs entirely on what Nomos can reach today — public catalogs, public orbital elements and modelled compute.</div>`);
  if (k === 'pass') {
    const nowK = simT - S.t0, pri = S.windows.find(w => w.sat.id === m.primary), ni = pri.img.find(([a]) => a > nowK);
    el = await bot(`<div class="txt">${ni ? `${satById(m.primary).name} next passes over ${esc(m.aoi.name)} in about <strong>${fmtIn(ni[0] - nowK)}</strong>` : `No ${satById(m.primary).name} pass falls in the next 12 h`} — it's the gold arc on the UTC dial. This preview uses illustrative orbits; the full brief has the real SGP4 window. ${chip('SIMULATED')}</div>`);
  }
  if (k === 'alt') { $$('.seg button')[1].click(); el = await bot(`<div class="txt">Switched to the stack view. ${m.paths.slice(1).map(p => `<strong>Path ${p.id}</strong> — ${p.why}`).join(' ')}</div>`); }
  followUps(el);
}

/* ================= free text ================= */
function parse(t) {
  const o = {};
  if (/ship|vessel|maritime|boat|shipping|tanker|fleet/i.test(t)) o.target = 'vessels';
  else if (/fire|burn|smoke|blaze/i.test(t)) o.target = 'wildfire';
  else if (/flood|inundat|hurricane|storm surge/i.test(t)) o.target = 'flood';
  else if (/change|construction|deforest|land use|urban/i.test(t)) o.target = 'change';
  if (!o.target) { if (/monitor|watch|track/i.test(t)) o.intent = 'monitor'; else if (/respond|disaster|emergency|event/i.test(t)) o.intent = 'respond'; }
  for (const [k, p] of Object.entries(PLACES)) if (p.re.test(t)) { o.aoi = k; break; }
  const ll = t.match(/(-?\d{1,2}(?:\.\d+)?)\s*°?\s*,\s*(-?\d{1,3}(?:\.\d+)?)/);
  if (!o.aoi && ll) { const lat = +ll[1], lon = +ll[2]; o.aoi = { key: 'custom', name: `Custom area · ${lat.toFixed(1)}, ${lon.toFixed(1)}`, bbox: [lon - .5, lat - .35, lon + .5, lat + .35] }; }
  if (/\bsar\b|radar/i.test(t)) o.sensor = 'sar'; else if (/optical|true.?colou?r|thermal|photo/i.test(t)) o.sensor = 'optical';
  if (/asap|urgent|immediately|as soon|right now/i.test(t)) o.freshness = 'asap'; else if (/24\s*h|today|tomorrow|next day|next 24/i.test(t)) o.freshness = 'next24'; else if (/archive|last week|historical|past/i.test(t)) o.freshness = 'archive';
  if (/cheap|budget|low.?cost/i.test(t)) o.priority = 'Cheapest'; else if (/reliab|robust/i.test(t)) o.priority = 'Most reliable'; else if (/fast|quick|urgent|asap/i.test(t)) o.priority = 'Fastest';
  if (/bucket|s3|storage/i.test(t)) o.delivery = 'Cloud bucket'; else if (/webhook|\bapi\b/i.test(t)) o.delivery = 'Webhook'; else if (/e-?mail/i.test(t)) o.delivery = 'Email brief';
  return o;
}
async function onText(text) {
  if (S.running) return bot(`<div class="txt">One moment — I'm still planning. You can follow each step on the globe.</div>`);
  lockAll(); userMsg(text);
  if (S.done) {
    if (/why/i.test(text)) return answerFollow('why');
    if (/pass|when/i.test(text)) return answerFollow('pass');
    if (/alternative|compare|other/i.test(text)) return answerFollow('alt');
    if (/^(new|start over|another)/i.test(text)) return reset();
  }
  const o = parse(text), keys = Object.keys(o);
  if (keys.length) {
    if (S.done) { S.mission = null; S.done = false; S.stage = 0; S.windows = null; $('#rail').classList.remove('on'); }
    if (o.target && S.slots.target && o.target !== S.slots.target && !o.aoi) delete S.slots.aoi;
    if (o.aoi && !o.target && !S.slots.target && typeof o.aoi !== 'string') o.target = 'change';
    keys.forEach(k => setSlot(k, o[k])); if (o.target && !keys.includes('target')) setSlot('target', o.target);
    const got = [o.target && TARGETS[o.target].label.toLowerCase(), o.aoi && aoiOf(o).name, o.sensor && SENSORS[o.sensor].label, o.freshness && FRESH[o.freshness].toLowerCase(), o.priority && o.priority.toLowerCase(), o.delivery && o.delivery.toLowerCase()].filter(Boolean);
    if (got.length) await bot(`<div class="txt">Got it — ${got.map(g => `<strong>${esc(g)}</strong>`).join(', ')}. I've added that to the brief.</div>`, { delay: 450 });
    S.step = keys.includes('freshness') ? 'freshness' : keys.includes('priority') ? 'priority' : S.step;
    return proceed();
  }
  if (S.step === 'aoi') return bot(`<div class="txt">I can't look up place names yet. Pick one of the places above, type coordinates like <span class="mono">40.6, -74.0</span>, or click the globe.</div>`);
  await bot(`<div class="txt">I didn't catch an objective there. Right now I can plan vessel monitoring, land change, wildfire and flood missions.${S.step && S.step !== 'confirm' ? ' Let me ask again:' : ''}</div>`);
  if (!S.step) return ask('intent');
  if (S.step !== 'confirm') return ask(S.step);
}

/* ================= composer ================= */
const input = $('#input'), send = $('#send');
input.addEventListener('input', () => { input.style.height = 'auto'; input.style.height = input.scrollHeight + 'px'; send.disabled = !input.value.trim(); });
input.addEventListener('keydown', e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); $('#composer').requestSubmit(); } });
$('#composer').addEventListener('submit', e => { e.preventDefault(); const v = input.value.trim(); if (!v) return; input.value = ''; input.style.height = 'auto'; send.disabled = true; safe(onText(v)); });
onWin('keydown', e => { if (e.key === '/' && document.activeElement !== input && !/INPUT|TEXTAREA|SELECT/.test(document.activeElement?.tagName || '')) { e.preventDefault(); input.focus(); } });

/* ================= missions lists ================= */
function renderLists() {
  $('#examples').innerHTML = EXAMPLES.map((x, i) => `<li><button data-ex="${i}" aria-current="${S.current === 'ex' + i}"><span class="dot"></span><span class="t">${x.title}</span><span class="m">EXAMPLE · ${x.meta}</span></button></li>`).join('');
  $('#mine').innerHTML = S.mine.length ? S.mine.slice(0, 8).map(x => `<li><button data-mine="${esc(x.id)}" aria-current="${S.current === 'mine:' + x.id}"><span class="dot"></span><span class="t">${esc(x.title)}</span><span class="m">Open brief →</span></button></li>`).join('') : '<li class="empty-row">Missions you plan appear here.</li>';
  $$('[data-ex]').forEach(b => b.addEventListener('click', () => loadSlots(EXAMPLES[+b.dataset.ex].slots, 'ex' + b.dataset.ex, `Open example: ${EXAMPLES[+b.dataset.ex].title}`)));
  $$('[data-mine]').forEach(b => b.addEventListener('click', () => deps.navigate(`/missions/${encodeURIComponent(b.dataset.mine)}`)));
}
function loadMine() {
  deps.listMissions().then(list => { if (!alive || !list.length) return; const seen = new Set(S.mine.map(x => x.id)); S.mine.push(...list.filter(x => !seen.has(x.id))); renderLists(); }).catch(() => {});
}
function missionPayload(sl, m) {
  const now = Date.now(), H = 3600e3;
  const [start, end] = sl.freshness === 'archive' ? [now - 72 * H, now] : sl.freshness === 'next24' ? [now, now + 24 * H] : [now, now + 12 * H];
  return {
    title: m.title.slice(0, 120),
    objective_type: sl.freshness === 'archive' ? 'analyze_imagery' : 'remote_sensing_workflow',
    area_of_interest: { type: 'bbox', coordinates: m.aoi.bbox.map(v => +v.toFixed(4)) },
    status: 'exploratory',
    start_time: new Date(start).toISOString(),
    end_time: new Date(end).toISOString(),
    preferred_compute_location: 'cloud',
    data_source_preference: [SENSORS[sl.sensor].label],
    onboard_processing: 'unnecessary',
    use_case: m.tgt.label,
    notes: `${m.tgt.objective}. Priority: ${sl.priority}. Deliver to: ${sl.delivery}. Created in Nomos Console.`,
  };
}
// in-app navigation for links rendered by the engine
root.addEventListener('click', e => { const a = e.target.closest && e.target.closest('a[data-nav]'); if (!a || e.metaKey || e.ctrlKey) return; e.preventDefault(); deps.navigate(a.getAttribute('href')); });
function loadSlots(slots, id, text) {
  root.classList.remove('show-left'); reset({ greet: false }); S.current = id; renderLists();
  Object.entries(slots).forEach(([k, v]) => setSlot(k, v)); userMsg(text); safe(plan({ fast: true }));
}

function reset({ greet = true }: { greet?: boolean; focus?: boolean } = {}) {
  S.token++; S.slots = {}; S.mission = null; S.step = null; S.stage = 0; S.at = {}; S.done = false; S.windows = null; S.log = []; S.running = false; S.noted = {}; S.current = null; S.realId = null; S.realError = null;
  setPicking(false); $('#rail').classList.remove('on'); $$('#rail li').forEach(li => li.className = '');
  if (S.lens !== 'orbit') $$('.seg button')[0].click();
  thread.innerHTML = ''; renderBrief(); renderStack(); renderLists(); target = [rot[0], -18];
  if (greet) safe(ask('intent'));
}
$('#newBtn').addEventListener('click', () => { root.classList.remove('show-left'); reset(); input.focus(); });

$$('.layer').forEach(b => b.addEventListener('click', () => { const k = b.dataset.layer; S.layers[k] = !S.layers[k]; b.setAttribute('aria-pressed', S.layers[k]); }));
$('#openLeft').addEventListener('click', () => { root.classList.remove('show-right'); root.classList.toggle('show-left'); });
$('#openRight').addEventListener('click', () => { root.classList.remove('show-left'); root.classList.toggle('show-right'); });
$('#scrim').addEventListener('click', () => root.classList.remove('show-left', 'show-right'));

reset({ focus: false });
rafId = requestAnimationFrame(frame);
loadMine();

return () => {
  alive = false; S.token++; cancelAnimationFrame(rafId);
  cleanups.forEach(fn => fn());
};
}
