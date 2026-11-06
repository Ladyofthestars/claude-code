// Renders a still every half second and at the start of every narration line,
// then joins them into contact sheets for review.
// Usage: npx tsx tools/stills.ts [video-name] [out-dir] [from-to,from-to ...]
// The optional third argument limits the stills to time windows in seconds, e.g. "20-31,48-53".
import fs from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';
import type {Words} from '../src/template/types';

const video = process.argv[2] ?? 'new-earth';
const outDir = process.argv[3] ?? path.join('out', 'stills');
const windows = (process.argv[4] ?? '').split(',').filter(Boolean).map((w) => w.split('-').map(Number));
const wanted = (t: number) => windows.length === 0 || windows.some(([a, b]) => t >= a && t <= b);
const browser = '/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell';
const browserExecutable = fs.existsSync(browser) ? browser : null;

const main = async () => {
	fs.rmSync(outDir, {recursive: true, force: true});
	fs.mkdirSync(outDir, {recursive: true});
	const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts')});
	const inputProps = {video};
	const composition = await selectComposition({serveUrl, id: 'Video', inputProps, browserExecutable, chromeMode: 'headless-shell'});
	const fps = composition.fps;
	const words: Words = composition.props.words as Words;

	const shots = new Map<number, string>();
	for (let f = 0; f < composition.durationInFrames; f += fps / 2) {
		shots.set(f, `t=${(f / fps).toFixed(1)}s`);
	}
	// Every sentence start (or every line start, if the timings don't mark sentences).
	const seen = new Set<number>();
	const marked = words.words.some((w) => (w as {sentence?: boolean}).sentence);
	words.words.forEach((w, i) => {
		const isStart = marked ? (w as {sentence?: boolean}).sentence : !seen.has(w.line);
		seen.add(w.line);
		if (isStart) {
			// A beat after the first word starts, so its visual has begun.
			const f = Math.min(composition.durationInFrames - 1, Math.round(w.start * fps) + 6);
			shots.set(f, `${w.line}: "${words.words.slice(i, i + 3).map((x) => x.text).join(' ')}…"`);
		}
	});
	const list = [...shots.entries()].filter(([f]) => wanted(f / fps)).sort((a, b) => a[0] - b[0]);
	const index: {frame: number; file: string; label: string}[] = [];
	for (const [frame, label] of list) {
		const file = path.join(outDir, `f${String(frame).padStart(5, '0')}.jpg`);
		await renderStill({composition, serveUrl, frame, output: file, inputProps, imageFormat: 'jpeg', jpegQuality: 85, scale: 0.5, browserExecutable, chromeMode: 'headless-shell'});
		index.push({frame, file, label});
		process.stdout.write('.');
	}
	fs.writeFileSync(path.join(outDir, 'index.json'), JSON.stringify(index, null, 1));
	console.log(`\n${index.length} stills in ${outDir}`);
	execFileSync('python3', [path.resolve('tools/contact_sheet.py'), outDir], {stdio: 'inherit'});
};

main().catch((e) => {
	console.error(e);
	process.exit(1);
});
