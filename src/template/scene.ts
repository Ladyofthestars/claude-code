// The whole scene as plain maths: where every picture, line, light, label and the camera
// are at any moment. The renderer draws from this, and tools/check.ts uses the same code
// to test every frame for cut-off pictures and the safe area.
import type {Anchor, ItemDef, LabelDef, MagnifierDef, PictureDef, Settings, ThreadDef, UV, Words} from './types';
import {bendControl, clamp01, easeInOut, easeOut, easeSine, lerp, monotoneSpline, outerTangents, pointAlong, quadBezier, smoothPolyline, type Pt} from './math';
import {makeTimeResolver} from './time';

export const FRAME = {width: 1080, height: 1920};
export const FADE = 0.5;

export type Cam = {x: number; y: number; z: number};
export type Box = {x0: number; y0: number; x1: number; y1: number};

export type ItemState = {
	id: string;
	src: string;
	// Screen-space image rectangle (after the small fade scale).
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

export const buildScene = (settings: Settings, words: Words) => {
	const {resolve, total} = makeTimeResolver(words, settings.tailSeconds);
	const W = FRAME.width;
	const H = FRAME.height;
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

	// Drawn content of an item on the page.
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
			const boxes = ids.map((id) => pageContent(getItem(id)));
			const b = {
				x0: Math.min(...boxes.map((v) => v.x0)),
				y0: Math.min(...boxes.map((v) => v.y0)),
				x1: Math.max(...boxes.map((v) => v.x1)),
				y1: Math.max(...boxes.map((v) => v.y1)),
			};
			x = (b.x0 + b.x1) / 2;
			y = (b.y0 + b.y1) / 2;
			const fit = k.fit ?? 0.85;
			z = k.zoom ?? fit * Math.min(safeW / (b.x1 - b.x0), safeH / (b.y1 - b.y0));
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

	// Far layers follow the camera only partly (parallax). Each is placed as seen at the
	// moment it appears, then drifts slower than the page.
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
		return {
			id,
			src: it.pic.src,
			left,
			top,
			width: w,
			height: h,
			opacity: k,
			blur: (1 - k) * 10 + (it.depth - 1) * 3,
			depth: it.depth,
			zoom: cam.z * scale,
			content: {x0: left + cb[0] * w, y0: top + cb[1] * h, x1: left + cb[2] * w, y1: top + cb[3] * h},
		};
	};

	// Screen position of a point on a picture.
	const anchorAt = (a: Anchor, t: number) => {
		const s = itemAt(a.item, t);
		return {x: s.left + a.at[0] * s.width, y: s.top + a.at[1] * s.height, zoom: s.zoom, opacity: s.opacity};
	};

	// ---- Threads (lines that draw themselves) ---------------------------------
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

	// ---- Lights ------------------------------------------------------------------
	type LightState = {x: number; y: number; size: number; alpha: number};
	const lightsAt = (t: number): LightState[] => {
		const out: LightState[] = [];
		for (const L of settings.lights) {
			const from = resolve(L.from);
			const to = L.to === undefined ? undefined : resolve(L.to);
			const intensity = L.intensity ?? 1;
			if (L.thread || L.path) {
				// A travelling light: eased along its path, fading in at the start and out at the end.
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
				} else {
					const s = itemAt(L.item as string, t);
					poly = smoothPolyline((L.path as UV[]).map((p) => ({x: s.left + p[0] * s.width, y: s.top + p[1] * s.height})));
					zoom = s.zoom;
					parentAlpha = s.opacity;
				}
				const head = easeInOut(raw);
				const envelope = Math.min(easeSine(raw / 0.18), 1 - easeSine((raw - 0.82) / 0.3));
				const size = (L.size ?? 60) * zoom;
				// A soft head with a fading trail behind it.
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
			// Glowing in place, at one or more points of a picture.
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
			center,
			radius,
			source: {x: src.x, y: src.y, r: srcR},
			// The two joining lines appear once the circle has moved clear of the detail.
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
		return {x, y, size, opacity: k, blur: (1 - k) * 8, scale: lerp(0.96, 1, kIn)};
	};

	return {settings, words, total, resolve, safe, camAt, itemAt, anchorAt, threadAt, lightsAt, magnifierAt, labelAt, layerCam, toScreen};
};

export type Scene = ReturnType<typeof buildScene>;
