import type {TimeRef, Words} from './types';

const norm = (s: string) => s.toLowerCase().replace(/[^a-z0-9']/g, '');

// Turns "3:small light+0.2" into seconds, using the narrator's word timings.
export const makeTimeResolver = (words: Words, tailSeconds: number) => {
	const total = words.duration + tailSeconds;
	const cache = new Map<string, number>();

	const resolve = (ref: TimeRef | undefined, fallback?: number): number => {
		if (ref === undefined || ref === null) {
			if (fallback === undefined) {
				throw new Error('Missing time');
			}
			return fallback;
		}
		if (typeof ref === 'number') {
			return ref;
		}
		const cached = cache.get(ref);
		if (cached !== undefined) {
			return cached;
		}
		let body = ref.trim();
		let offset = 0;
		const off = body.match(/^(.*?)\s*([+-]\s*\d+(?:\.\d+)?)$/);
		if (off && off[1].length > 0) {
			body = off[1].trim();
			offset = parseFloat(off[2].replace(/\s/g, ''));
		}
		let base: number;
		if (body === 'start') {
			base = 0;
		} else if (body === 'end') {
			base = total;
		} else if (body === 'voiceEnd') {
			base = words.duration;
		} else {
			const m = body.match(/^(\d+):(.+?)(@end)?$/);
			if (!m) {
				throw new Error(`Cannot read time "${ref}"`);
			}
			const line = parseInt(m[1], 10);
			const tokens = m[2].split(/\s+/).map(norm).filter(Boolean);
			const inLine = words.words.filter((w) => w.line === line);
			let found = -1;
			for (let i = 0; i + tokens.length <= inLine.length; i++) {
				if (tokens.every((tk, j) => norm(inLine[i + j].text) === tk)) {
					found = i;
					break;
				}
			}
			if (found < 0) {
				throw new Error(`Phrase "${m[2]}" not found in narration line ${line} (time "${ref}")`);
			}
			base = m[3] ? inLine[found + tokens.length - 1].end : inLine[found].start;
		}
		const value = base + offset;
		cache.set(ref, value);
		return value;
	};

	return {resolve, total};
};
