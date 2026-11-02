// The whole scene as plain maths: where every picture, line, light, label and the camera
// are at any moment. The renderer draws from this, and tools/check.ts uses the same code
// to test every frame for cut-off pictures, the safe area and gaps with nothing new.
import type {Anchor, DrawingDef, ItemDef, LabelDef, MagnifierDef, PictureDef, Settings, StreamDef, ThreadDef, UV, Words} from './types';
import {bendControl, clamp01, easeInOut, easeOut, easeSine, lerp, monotoneSpline, outerTangents, pointAlong, quadBezier, smoothPolyline, type Pt} from './math';
import {makeTimeResolver} from './time';

// Default frame (vertical short). A video can set its own size in settings.size.
export const FRAME = {width: 1080, height: 1920};
export const FADE = 0.5;

export type Cam = {x: number; y: number; z: number};
export type Box = {x0: number; y0: number; x1: number; y1: number};

export type ItemState = {
	id: string;
	src: string;
	left: number;
	top: number;
	width: number;
	height: number;
	opacity: number;
	blur: number;
	depth: number;
	content: Box;
	zoom: number;
};

type Resolved = {
	def: ItemDef;
	pic: PictureDef;
	height: number;
	depth: number;
	tIn?: number;
	tOut?: number;
	fade: number;
};

// 0 → 1 as something appears, back to 0 as it leaves. Each over `fade` seconds, eased.
export const presence = (t: number, tIn: number | undefined, tOut: number | undefined, fade: number) => {
	const kIn = tIn === undefined ? 1 : easeSine((t - tIn) / fade);
	const kOut = tOut === undefined ? 1 : 1 - easeSine((t - tOut) / fade);
	return {k: Math.min(kIn, kOut), kIn, kOut};
};

export const formatNumber = (n: number, decimals: number) => {
	const fixed = n.toFixed(decimals);
	const [int, dec] = fixed.split('.');
	const withCommas = int.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
	return dec ? `${withCommas}.${dec}` : withCommas;
};

export const buildScene = (settings: Settings, words: Words) => {
	const {resolve, total} = makeTimeResolver(words, settings.tailSeconds);
	const frame = settings.size ?? FRAME;
	const W = frame.width;
	const H = frame.height;
	const safe = {
		left: W * settings.safeArea.side,
		right: W * (1 - settings.safeArea.side),
		top: H * settings.safeArea.top,
		bottom: H * (1 - settings.safeArea.bottom),
	};
	const safeW = safe.right - safe.left;
	const safeH = safe.bottom - safe.top;
	const cx = (safe.left + safe.right) / 2;
	const cy = (safe.top + safe.bottom) / 2;

	// Nothing is ever cut off: as a box nears the edge of the safe area it fades out
	// (fully gone 20 px past the edge, well before the frame edge), and fades back in
	// when the camera brings it back.
	const edgeGuard = (b: Box) => {
		const d = Math.min(b.x0 - safe.left, b.y0 - safe.top, safe.right - b.x1, safe.bottom - b.y1);
		return clamp01((d + 20) / 40);
	};

	const items = new Map<string, Resolved>();
	for (const def of settings.items) {
		const pic = settings.pictures[def.picture];
		if (!pic) {
			throw new Error(`Item "${def.id}" uses unknown picture "${def.picture}"`);
		}
		items.set(def.id, {
			def,
			pic,
			height: def.width / pic.aspect,
			depth: def.depth ?? 1,
			tIn: def.in === undefined ? undefined : resolve(def.in),
			tOut: def.out === undefined ? undefined : resolve(def.out),
			fade: def.fade ?? FADE,
		});
	}
	const getItem = (id: string) => {
		const it = items.get(id);
		if (!it) {
			throw new Error(`Unknown item "${id}"`);
		}
		return it;
	};

	const pageContent = (it: Resolved): Box => {
		const c = it.pic.content ?? [0, 0, 1, 1];
		const x0 = it.def.x - it.def.width / 2;
		const y0 = it.def.y - it.height / 2;
		return {
			x0: x0 + c[0] * it.def.width,
			y0: y0 + c[1] * it.height,
			x1: x0 + c[2] * it.def.width,
			y1: y0 + c[3] * it.height,
		};
	};

	const drawings = settings.drawings ?? [];
	const drawingDefs = new Map<string, DrawingDef>(drawings.map((d) => [d.id, d]));

	// Page-space points of a drawing.
	const drawingPoints = (d: DrawingDef): Pt[] => {
		if (d.kind === 'circle') {
			const n = 96;
			return Array.from({length: n + 1}, (_, i) => {
				const a = -Math.PI / 2 + (i / n) * Math.PI * 2;
				return {x: (d.cx ?? 0) + (d.r ?? 10) * Math.cos(a), y: (d.cy ?? 0) + (d.r ?? 10) * Math.sin(a)};
			});
		}
		if (d.kind === 'rect') {
			const x = d.x ?? 0;
			const y = d.y ?? 0;
			const w = (d.w ?? 10) / 2;
			const h = (d.h ?? 10) / 2;
			return [
				{x: x - w, y: y - h},
				{x: x + w, y: y - h},
				{x: x + w, y: y + h},
				{x: x - w, y: y + h},
				{x: x - w, y: y - h},
			];
		}
		const pts = (d.points ?? []).map(([x, y]) => ({x, y}));
		if (d.closed && pts.length > 1) {
			pts.push(pts[0]);
		}
		return pts;
	};

	// Box of a drawing on the page (for camera framing).
	const drawingBox = (d: DrawingDef): Box => {
		const pts = drawingPoints(d);
		return {
			x0: Math.min(...pts.map((p) => p.x)),
			y0: Math.min(...pts.map((p) => p.y)),
			x1: Math.max(...pts.map((p) => p.x)),
			y1: Math.max(...pts.map((p) => p.y)),
		};
	};

	// ---- Camera -------------------------------------------------------------
	type Key = {t: number; x: number; y: number; z: number};
	const keys: Key[] = [];
	for (const k of settings.camera) {
		const t = resolve(k.at);
		let x = k.x ?? 0;
		let y = k.y ?? 0;
		let z = k.zoom ?? 1;
		if (k.focus) {
			const ids = Array.isArray(k.focus) ? k.focus : [k.focus];
			const boxes = ids.map((id) => (items.has(id) ? pageContent(getItem(id)) : drawingDefs.has(id) ? drawingBox(drawingDefs.get(id) as DrawingDef) : pageContent(getItem(id))));
			const b = {
				x0: Math.min(...boxes.map((v) => v.x0)),
				y0: Math.min(...boxes.map((v) => v.y0)),
				x1: Math.max(...boxes.map((v) => v.x1)),
				y1: Math.max(...boxes.map((v) => v.y1)),
			};
			x = (b.x0 + b.x1) / 2;
			y = (b.y0 + b.y1) / 2;
			const fit = k.fit ?? 0.85;
			z = k.zoom ?? fit * Math.min(safeW / Math.max(1, b.x1 - b.x0), safeH / Math.max(1, b.y1 - b.y0));
		}
		x += k.dx ?? 0;
		y += k.dy ?? 0;
		keys.push({t, x, y, z});
		if (k.hold) {
			keys.push({t: t + k.hold, x, y, z});
		}
	}
	keys.sort((a, b) => a.t - b.t);
	const ts = keys.map((k) => k.t);
	const camX = monotoneSpline(ts, keys.map((k) => k.x));
	const camY = monotoneSpline(ts, keys.map((k) => k.y));
	const camZ = monotoneSpline(ts, keys.map((k) => Math.log(k.z)));
	const camAt = (t: number): Cam => ({x: camX(t), y: camY(t), z: Math.exp(camZ(t))});

	const layerCam = (depth: number, refT: number, t: number) => {
		const cam = camAt(t);
		if (depth === 1) {
			return cam;
		}
		const ref = camAt(refT);
		const p = 1 / depth;
		return {x: ref.x + (cam.x - ref.x) * p, y: ref.y + (cam.y - ref.y) * p, z: ref.z * Math.pow(cam.z / ref.z, p)};
	};
	const toScreen = (pt: Pt, cam: Cam): Pt => ({x: cx + (pt.x - cam.x) * cam.z, y: cy + (pt.y - cam.y) * cam.z});

	// ---- Pictures -------------------------------------------------------------
	const itemAt = (id: string, t: number): ItemState => {
		const it = getItem(id);
		const {k, kIn, kOut} = presence(t, it.tIn, it.tOut, it.fade);
		const cam = layerCam(it.depth, it.tIn ?? 0, t);
		const scale = (kIn < 1 ? lerp(0.96, 1, kIn) : 1) * (kOut < 1 ? lerp(0.97, 1, kOut) : 1);
		const c = toScreen({x: it.def.x, y: it.def.y}, cam);
		const w = it.def.width * cam.z * scale;
		const h = it.height * cam.z * scale;
		const left = c.x - w / 2;
		const top = c.y - h / 2;
		const cb = it.pic.content ?? [0, 0, 1, 1];
		const content = {x0: left + cb[0] * w, y0: top + cb[1] * h, x1: left + cb[2] * w, y1: top + cb[3] * h};
		return {
			id,
			src: it.pic.src,
			left,
			top,
			width: w,
			height: h,
			opacity: k * edgeGuard(content),
			blur: (1 - k) * 10 + (it.depth - 1) * 3,
			depth: it.depth,
			zoom: cam.z * scale,
			content,
		};
	};

	const anchorAt = (a: Anchor, t: number) => {
		const s = itemAt(a.item, t);
		return {x: s.left + a.at[0] * s.width, y: s.top + a.at[1] * s.height, zoom: s.zoom, opacity: s.opacity};
	};

	// ---- Threads ------------------------------------------------------------------
	const threadDefs = new Map<string, ThreadDef>(settings.threads.map((d) => [d.id, d]));
	const threadAt = (d: ThreadDef, t: number) => {
		const a = anchorAt(d.from, t);
		const b = anchorAt(d.to, t);
		const c = bendControl(a, b, d.bend ?? 0.12);
		const tDraw = resolve(d.draw);
		const progress = easeInOut((t - tDraw) / (d.duration ?? 0.9));
		const {k} = presence(t, tDraw - 0.001, d.out === undefined ? undefined : resolve(d.out), FADE);
		return {a, b, c, progress, opacity: progress > 0 ? Math.min(k, Math.min(a.opacity, b.opacity) * 1.2) : 0, zoom: (a.zoom + b.zoom) / 2};
	};

	// ---- Drawings (diagrams that draw themselves) ------------------------------------
	const drawingAt = (d: DrawingDef, t: number) => {
		const tDraw = resolve(d.draw);
		const depth = d.depth ?? 1;
		const cam = layerCam(depth, tDraw, t);
		const raw = drawingPoints(d).map((p) => toScreen(p, cam));
		const pts = d.curve ? smoothPolyline(raw, 16) : raw;
		const dur = d.duration ?? 0.9;
		const progress = d.dashed ? 1 : easeInOut((t - tDraw) / dur);
		const tOut = d.out === undefined ? undefined : resolve(d.out);
		const pres = presence(t, d.dashed ? tDraw : tDraw - 0.001, tOut, d.dashed ? 0.6 : FADE);
		const visible = d.dashed ? pres.k : progress > 0 ? pres.k : 0;
		const fillStart = d.fillAt === undefined ? tDraw + dur * 0.6 : resolve(d.fillAt);
		const fillK = d.fill ? presence(t, fillStart, tOut, 0.6).k * (d.fillOpacity ?? 0.18) : 0;
		let head: {x: number; y: number; angle: number} | null = null;
		if (d.arrow && pts.length > 1) {
			const end = pointAlong(pts, Math.max(0.0001, progress));
			const back = pointAlong(pts, Math.max(0, progress - 0.02));
			head = {x: end.x, y: end.y, angle: Math.atan2(end.y - back.y, end.x - back.x)};
		}
		// Shapes and short lines fade near the edge like pictures; long lines (timelines, waves) may run off.
		let guard = 1;
		const bx = {x0: Math.min(...pts.map((q) => q.x)), y0: Math.min(...pts.map((q) => q.y)), x1: Math.max(...pts.map((q) => q.x)), y1: Math.max(...pts.map((q) => q.y))};
		const small = bx.x1 - bx.x0 < W * 0.6 && bx.y1 - bx.y0 < H * 0.6;
		if (d.kind === 'rect' || d.kind === 'circle' || small) {
			guard = edgeGuard(bx);
		}
		return {pts, progress, opacity: visible * guard, zoom: cam.z, fill: fillK * guard, head, blur: (depth - 1) * 2};
	};

	// ---- Lights ------------------------------------------------------------------
	type LightState = {x: number; y: number; size: number; alpha: number};
	const lightsAt = (t: number): LightState[] => {
		const out: LightState[] = [];
		for (const L of settings.lights) {
			const from = resolve(L.from);
			const to = L.to === undefined ? undefined : resolve(L.to);
			const intensity = L.intensity ?? 1;
			if (L.thread || L.path || L.drawing) {
				const dur = L.duration ?? 1.4;
				const raw = (t - from) / dur;
				if (raw < -0.05 || raw > 1.15) {
					continue;
				}
				let poly: Pt[];
				let zoom: number;
				let parentAlpha: number;
				if (L.thread) {
					const d = threadDefs.get(L.thread);
					if (!d) {
						throw new Error(`Light uses unknown thread "${L.thread}"`);
					}
					const th = threadAt(d, t);
					poly = Array.from({length: 33}, (_, i) => quadBezier(th.a, th.c, th.b, i / 32));
					zoom = th.zoom;
					parentAlpha = Math.max(th.opacity, 0.001);
				} else if (L.drawing) {
					const d = drawingDefs.get(L.drawing);
					if (!d) {
						throw new Error(`Light uses unknown drawing "${L.drawing}"`);
					}
					const st = drawingAt(d, t);
					poly = st.pts;
					zoom = st.zoom;
					parentAlpha = 1;
				} else {
					const s = itemAt(L.item as string, t);
					poly = smoothPolyline((L.path as UV[]).map((p) => ({x: s.left + p[0] * s.width, y: s.top + p[1] * s.height})));
					zoom = s.zoom;
					parentAlpha = s.opacity;
				}
				if (L.reverse) {
					poly = [...poly].reverse();
				}
				const head = easeInOut(raw);
				const envelope = Math.min(easeSine(raw / 0.18), 1 - easeSine((raw - 0.82) / 0.3));
				const size = (L.size ?? 60) * zoom;
				for (let i = 0; i < 7; i++) {
					const f = head - i * 0.022;
					if (f < 0) {
						break;
					}
					const p = pointAlong(poly, f);
					out.push({x: p.x, y: p.y, size: size * (1 - i * 0.08), alpha: intensity * envelope * parentAlpha * (i === 0 ? 1 : 0.42 * (1 - i / 7))});
				}
				continue;
			}
			if (L.world || L.worldPoints) {
				const pts = L.worldPoints ?? [L.world as [number, number]];
				const cam = camAt(t);
				pts.forEach((wp, i) => {
					const start = from + i * (L.stagger ?? 0);
					const {k} = presence(t, start, to, 0.7);
					if (k <= 0) {
						return;
					}
					const p = toScreen({x: wp[0], y: wp[1]}, cam);
					const breathe = 1 + 0.06 * Math.sin(((t - start) / 3.2 + i * 0.37) * Math.PI * 2);
					const size = (L.size ?? 40) * cam.z * lerp(0.7, 1, k) * breathe;
					const g = edgeGuard({x0: p.x - size * 0.25, y0: p.y - size * 0.25, x1: p.x + size * 0.25, y1: p.y + size * 0.25});
					out.push({x: p.x, y: p.y, size, alpha: intensity * k * g});
				});
				continue;
			}
			const pts = L.points ?? (L.at ? [L.at] : []);
			pts.forEach((uv, i) => {
				const start = from + i * (L.stagger ?? 0);
				const {k} = presence(t, start, to, 0.7);
				if (k <= 0) {
					return;
				}
				const s = itemAt(L.item as string, t);
				const breathe = 1 + 0.05 * Math.sin(((t - start) / 3.2) * Math.PI * 2);
				out.push({
					x: s.left + uv[0] * s.width,
					y: s.top + uv[1] * s.height,
					size: (L.size ?? 50) * s.zoom * lerp(0.7, 1, k) * breathe,
					alpha: intensity * k * s.opacity,
				});
			});
		}
		return out;
	};

	// ---- Magnifiers ---------------------------------------------------------------
	const magnifierAt = (m: MagnifierDef, t: number) => {
		const open = resolve(m.open);
		const close = m.close === undefined ? undefined : resolve(m.close);
		const kOpen = easeOut((t - open) / 0.8);
		const kClose = close === undefined ? 1 : 1 - easeInOut((t - close) / 0.7);
		const k = Math.min(kOpen, kClose);
		const src = anchorAt(m.source, t);
		const cam = camAt(t);
		const target = toScreen({x: m.x, y: m.y}, cam);
		const srcR = m.source.radius * src.zoom;
		const center = {x: lerp(src.x, target.x, k), y: lerp(src.y, target.y, k)};
		const radius = lerp(srcR, m.radius * cam.z, k);
		const contents = m.contents.map((c) => {
			const from = c.from === undefined ? open : resolve(c.from);
			const to = c.to === undefined ? undefined : resolve(c.to);
			const pic = settings.pictures[c.picture];
			const pres = presence(t, c.from === undefined ? undefined : from, to, FADE);
			const w = (c.scale ?? 1) * radius * 2;
			const h = w / pic.aspect;
			const x = center.x + (c.dx ?? 0) * radius * 2 - w / 2;
			const y = center.y + (c.dy ?? 0) * radius * 2 - h / 2;
			const lights = (c.lights ?? []).map((l) => {
				const pl = presence(t, resolve(l.from), l.to === undefined ? undefined : resolve(l.to), 0.7);
				return {x: x + l.at[0] * w, y: y + l.at[1] * h, size: (l.size ?? 0.12) * w * lerp(0.7, 1, pl.k), alpha: pl.k};
			});
			return {src: pic.src, left: x, top: y, width: w, height: h, opacity: pres.k, blur: (1 - pres.k) * 8, lights};
		});
		return {
			k,
			guard: edgeGuard({x0: center.x - radius, y0: center.y - radius, x1: center.x + radius, y1: center.y + radius}),
			center,
			radius,
			source: {x: src.x, y: src.y, r: srcR},
			lines: k > 0 ? outerTangents(src, srcR, center, radius) : [],
			lineAlpha: clamp01((k - 0.15) / 0.3),
			contents,
		};
	};

	// ---- Labels -------------------------------------------------------------------------
	const labelAt = (l: LabelDef, t: number) => {
		const tIn = resolve(l.in);
		const tOut = l.out === undefined ? undefined : resolve(l.out);
		const {k, kIn} = presence(t, tIn, tOut, 0.6);
		let x = l.x;
		let y = l.y;
		let size = l.size ?? 56;
		if (l.space === 'world') {
			const cam = camAt(t);
			const p = toScreen({x: l.x, y: l.y}, cam);
			x = p.x;
			y = p.y;
			size *= cam.z;
		}
		let text = l.text;
		if (l.count) {
			const c = l.count;
			const kc = easeOut((t - tIn) / (c.duration ?? 1.4));
			text = l.text.replace('{n}', formatNumber(lerp(c.from ?? 0, c.to, kc), c.decimals ?? 0));
		}
		let guard = 1;
		if (l.space === 'world') {
			const halfW = (text.length * size * (0.66 + (l.spacing ?? 0.32))) / 2;
			const halfH = size * 0.6;
			const left = l.align === 'left' ? x : x - halfW;
			guard = edgeGuard({x0: left, y0: y - halfH, x1: left + 2 * halfW, y1: y + halfH});
		}
		return {x, y, size, text, opacity: k * guard, blur: (1 - k) * 8, scale: lerp(0.96, 1, kIn), align: l.align ?? 'center'};
	};

	// ---- Streams (flows of atoms) ------------------------------------------------------------
	type Dot = {x: number; y: number; r: number; alpha: number; color: 'ink' | 'accent'};
	const streamPolys = new Map<StreamDef, Pt[]>();
	const streamAt = (S: StreamDef, t: number): Dot[] => {
		const from = resolve(S.from);
		const to = S.to === undefined ? undefined : resolve(S.to);
		const {k} = presence(t, from, to, 0.8);
		if (k <= 0) {
			return [];
		}
		let poly = streamPolys.get(S);
		if (!poly) {
			const raw = S.points.map(([x, y]) => ({x, y}));
			poly = S.curve ? smoothPolyline(raw, 16) : raw;
			if (S.reverse) {
				poly = [...poly].reverse();
			}
			streamPolys.set(S, poly);
		}
		const cam = camAt(t);
		const n = S.count ?? 9;
		const period = S.period ?? 3.2;
		const size = (S.size ?? 14) * cam.z;
		const spread = S.spread ?? 10;
		const out: Dot[] = [];
		for (let i = 0; i < n; i++) {
			const seed = i * 2.399963;
			// Each dot starts at its own moment, so the flow begins at the source and fills the path.
			const age = (t - from) / period - i / n;
			if (age < 0) {
				continue;
			}
			const f = age % 1;
			const p = pointAlong(poly, f);
			const q = pointAlong(poly, Math.min(1, f + 0.01));
			const len = Math.hypot(q.x - p.x, q.y - p.y) || 1;
			const wobble = spread * Math.sin(seed * 3.1 + (t - from) * (0.9 + (i % 3) * 0.25));
			const wp = {x: p.x - ((q.y - p.y) / len) * wobble, y: p.y + ((q.x - p.x) / len) * wobble};
			const sp = toScreen(wp, cam);
			const env = Math.sin(Math.PI * f);
			const r = (size / 2) * (0.75 + 0.25 * Math.sin(seed * 5.3));
			const g = edgeGuard({x0: sp.x - r, y0: sp.y - r, x1: sp.x + r, y1: sp.y + r});
			const alpha = k * g * Math.min(1, env * 1.6);
			if (alpha > 0.01) {
				out.push({x: sp.x, y: sp.y, r, alpha, color: S.color ?? 'ink'});
			}
		}
		return out;
	};
	const streamsAt = (t: number): Dot[] => (settings.streams ?? []).flatMap((S) => streamAt(S, t));

	// ---- Dust (drifting specks of light behind everything) -------------------------------------
	// Fixed pseudo-random specks on a tile that repeats across the page. They depend only on the
	// camera and on the whole video's clock, so parts join without a jump.
	const dustDef = settings.theme.dust;
	const TILE = 1400;
	const dustSeeds = dustDef
		? Array.from({length: dustDef.count}, (_, i) => {
				const h = (v: number) => {
					const s = Math.sin(v * 12.9898 + i * 78.233) * 43758.5453;
					return s - Math.floor(s);
				};
				return {x: h(1) * TILE, y: h(2) * TILE, s: 0.4 + h(3) * 0.9, ph: h(4) * Math.PI * 2, sp: 0.15 + h(5) * 0.35, vx: (h(6) - 0.5), vy: (h(7) - 0.5)};
			})
		: [];
	const dustAt = (t: number) => {
		if (!dustDef) {
			return [];
		}
		const clock = (settings.clock ?? 0) + t;
		const cam = camAt(t);
		const p = dustDef.parallax;
		const z = Math.pow(cam.z, p);
		const tile = TILE * z;
		const drift = dustDef.drift ?? 6;
		const out: {x: number; y: number; r: number; alpha: number}[] = [];
		for (const d of dustSeeds) {
			const wx = d.x + d.vx * drift * clock;
			const wy = d.y + d.vy * drift * clock;
			let sx = cx + (wx - cam.x * p) * z;
			let sy = cy + (wy - cam.y * p) * z;
			sx = ((sx % tile) + tile) % tile;
			sy = ((sy % tile) + tile) % tile;
			const tw = 0.55 + 0.45 * Math.sin(clock * d.sp * Math.PI * 2 * 0.3 + d.ph);
			for (let ox = sx - tile; ox < W + tile; ox += tile) {
				for (let oy = sy - tile; oy < H + tile; oy += tile) {
					if (ox > -10 && ox < W + 10 && oy > -10 && oy < H + 10) {
						out.push({x: ox, y: oy, r: dustDef.size * d.s * Math.sqrt(z), alpha: tw * d.s});
					}
				}
			}
		}
		return out;
	};

	return {settings, words, total, resolve, safe, frame, camAt, itemAt, anchorAt, threadAt, drawingAt, lightsAt, magnifierAt, labelAt, layerCam, toScreen, streamsAt, dustAt};
};

export type Scene = ReturnType<typeof buildScene>;
