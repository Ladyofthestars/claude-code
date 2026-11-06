// Checks every frame of a video's settings, without rendering:
//   - no visible picture is cut off at the frame edge
//   - pictures, magnifiers and labels stay out of the top 8% and bottom 18%
//   - prints the timeline of everything that starts, so overlaps are easy to spot
// Usage: npx tsx tools/check.ts [video-name]
import fs from 'node:fs';
import path from 'node:path';
import {buildScene} from '../src/template/scene';
import type {Settings, Words} from '../src/template/types';

const video = process.argv[2] ?? 'new-earth';
const dir = path.join('public', 'videos', video);
const settings: Settings = JSON.parse(fs.readFileSync(path.join(dir, 'settings.json'), 'utf8'));
const words: Words = JSON.parse(fs.readFileSync(path.join(dir, settings.words), 'utf8'));
const scene = buildScene(settings, words);
const fps = 60;
const frames = Math.ceil(scene.total * fps);
const tol = 2;
const problems = new Map<string, {first: number; last: number; worst: string}>();
const note = (key: string, t: number, detail: string) => {
	const p = problems.get(key);
	if (p) {
		p.last = t;
	} else {
		problems.set(key, {first: t, last: t, worst: detail});
	}
};
const {safe} = scene;
const FRAME = scene.frame;

for (let f = 0; f < frames; f++) {
	const t = f / fps;
	for (const it of settings.items) {
		const s = scene.itemAt(it.id, t);
		const c = s.content;
		if (s.opacity > 0.02 && (c.x0 < -tol || c.y0 < -tol || c.x1 > FRAME.width + tol || c.y1 > FRAME.height + tol)) {
			note(`${it.id}: cut off at the frame edge`, t, `box ${c.x0.toFixed(0)},${c.y0.toFixed(0)} – ${c.x1.toFixed(0)},${c.y1.toFixed(0)}, opacity ${s.opacity.toFixed(2)}`);
		}
		if (s.opacity > 0.5 && (c.y0 < safe.top - tol || c.y1 > safe.bottom + tol)) {
			note(`${it.id}: inside the top 8% / bottom 18%`, t, `top ${c.y0.toFixed(0)} bottom ${c.y1.toFixed(0)} (safe ${safe.top.toFixed(0)}–${safe.bottom.toFixed(0)})`);
		}
	}
	settings.magnifiers.forEach((m, i) => {
		const g = scene.magnifierAt(m, t);
		if (g.k * g.guard > 0.5) {
			const y0 = g.center.y - g.radius;
			const y1 = g.center.y + g.radius;
			const x0 = g.center.x - g.radius;
			const x1 = g.center.x + g.radius;
			if (y0 < safe.top - tol || y1 > safe.bottom + tol || x0 < -tol || x1 > FRAME.width + tol) {
				note(`magnifier ${i + 1}: outside the safe area`, t, `circle ${x0.toFixed(0)},${y0.toFixed(0)} – ${x1.toFixed(0)},${y1.toFixed(0)}`);
			}
		}
	});
	settings.labels.forEach((l) => {
		const s = scene.labelAt(l, t);
		if (s.opacity > 0.5) {
			const halfW = (s.text.length * s.size * (0.66 + (l.spacing ?? 0.32))) / 2;
			const halfH = s.size * 0.6;
			const left = s.align === 'left' ? s.x : s.x - halfW;
			if (s.y - halfH < safe.top - tol || s.y + halfH > safe.bottom + tol || left < -tol || left + 2 * halfW > FRAME.width + tol) {
				note(`label "${l.text}": outside the safe area`, t, `centre ${s.x.toFixed(0)},${s.y.toFixed(0)} size ${s.size.toFixed(0)}`);
			}
		}
	});
}

// Timeline of things that start, to check that one thing happens at a time.
const events: {t: number; what: string}[] = [];
const r = scene.resolve;
settings.items.forEach((i) => i.in !== undefined && events.push({t: r(i.in), what: `fade in ${i.id}`}));
settings.items.forEach((i) => i.out !== undefined && events.push({t: r(i.out), what: `fade out ${i.id}`}));
settings.threads.forEach((d) => events.push({t: r(d.draw), what: `draw line ${d.id}`}));
settings.lights.forEach((l, i) => events.push({t: r(l.from), what: `light ${i + 1}${l.thread ? ` along ${l.thread}` : l.path ? ` along ${l.item}` : ` on ${l.item}`}`}));
settings.magnifiers.forEach((m, i) => {
	events.push({t: r(m.open), what: `magnifier ${i + 1} opens`});
	if (m.close !== undefined) {
		events.push({t: r(m.close), what: `magnifier ${i + 1} closes`});
	}
});
settings.labels.forEach((l) => events.push({t: r(l.in), what: `label "${l.text}"`}));
(settings.drawings ?? []).forEach((d) => events.push({t: r(d.draw), what: `draw ${d.id}`}));
(settings.streams ?? []).forEach((d, i) => events.push({t: r(d.from), what: `stream ${d.id ?? i + 1}`}));
settings.camera.forEach((k) => events.push({t: r(k.at), what: `camera → ${k.focus ?? `${k.x},${k.y}`}${k.hold ? ` (hold ${k.hold}s)` : ''}`}));
events.sort((a, b) => a.t - b.t);

const lineStarts = new Map<number, number>();
for (const w of words.words) {
	if (!lineStarts.has(w.line)) {
		lineStarts.set(w.line, w.start);
	}
}
console.log(`Video "${video}": ${scene.total.toFixed(2)}s, ${frames} frames at ${fps} fps`);
console.log('\nTimeline:');
let nextLine = 1;
for (const e of events) {
	while (lineStarts.has(nextLine) && (lineStarts.get(nextLine) as number) <= e.t) {
		const w = words.words.filter((x) => x.line === nextLine).map((x) => x.text).join(' ');
		console.log(`  ${(lineStarts.get(nextLine) as number).toFixed(2).padStart(6)}s  ── line ${nextLine}: ${w}`);
		nextLine++;
	}
	console.log(`  ${e.t.toFixed(2).padStart(6)}s     ${e.what}`);
}
// Something new on screen at least every few seconds.
const maxGap = Number(process.env.MAX_GAP ?? 5);
const starts = [0, ...events.map((e) => e.t).filter((t) => t >= 0 && t <= scene.total), scene.total].sort((a, b) => a - b);
for (let i = 1; i < starts.length; i++) {
	if (starts[i] - starts[i - 1] > maxGap) {
		note(`nothing new for ${(starts[i] - starts[i - 1]).toFixed(1)}s`, starts[i - 1], `from ${starts[i - 1].toFixed(2)}s to ${starts[i].toFixed(2)}s`);
	}
}
console.log(problems.size === 0 ? '\nNo problems found.' : `\n${problems.size} problem(s):`);
for (const [k, v] of problems) {
	console.log(`  - ${k}, from ${v.first.toFixed(2)}s to ${v.last.toFixed(2)}s (${v.worst})`);
}
process.exitCode = problems.size === 0 ? 0 : 1;
