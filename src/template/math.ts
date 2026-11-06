export type Pt = {x: number; y: number};

export const clamp01 = (v: number) => (v < 0 ? 0 : v > 1 ? 1 : v);
export const lerp = (a: number, b: number, k: number) => a + (b - a) * k;

// Starts slowly, speeds up, settles slowly.
export const easeInOut = (v: number) => {
	const x = clamp01(v);
	return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
};

// Gentler version, used for fades.
export const easeSine = (v: number) => -(Math.cos(Math.PI * clamp01(v)) - 1) / 2;

// Leaves quickly, settles slowly. Used for things that grow out of a point.
export const easeOut = (v: number) => 1 - Math.pow(1 - clamp01(v), 3);

// Monotone cubic interpolation through keyframes (Fritsch–Carlson / Brodlie).
// - Never overshoots, so the camera never swings past a framing.
// - Velocity is zero at the first and last key and at every hold or turning point,
//   so each move starts slowly and settles slowly.
// - Velocity is continuous through intermediate keys, so moves flow into each other.
export const monotoneSpline = (xs: number[], ys: number[]) => {
	const n = xs.length;
	if (n === 0) {
		return () => 0;
	}
	if (n === 1) {
		return () => ys[0];
	}
	const d: number[] = [];
	for (let i = 0; i < n - 1; i++) {
		d.push((ys[i + 1] - ys[i]) / (xs[i + 1] - xs[i]));
	}
	const m = new Array<number>(n).fill(0);
	for (let i = 1; i < n - 1; i++) {
		if (d[i - 1] * d[i] <= 0) {
			m[i] = 0;
		} else {
			const h0 = xs[i] - xs[i - 1];
			const h1 = xs[i + 1] - xs[i];
			const w1 = 2 * h1 + h0;
			const w2 = h1 + 2 * h0;
			m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i]);
		}
	}
	return (x: number) => {
		if (x <= xs[0]) {
			return ys[0];
		}
		if (x >= xs[n - 1]) {
			return ys[n - 1];
		}
		let i = 0;
		while (i < n - 2 && x > xs[i + 1]) {
			i++;
		}
		const h = xs[i + 1] - xs[i];
		const s = (x - xs[i]) / h;
		const s2 = s * s;
		const s3 = s2 * s;
		return (
			(2 * s3 - 3 * s2 + 1) * ys[i] +
			(s3 - 2 * s2 + s) * h * m[i] +
			(-2 * s3 + 3 * s2) * ys[i + 1] +
			(s3 - s2) * h * m[i + 1]
		);
	};
};

// Smooth curve through the given points (centripetal-ish Catmull–Rom), sampled densely,
// with arc length so a light can travel along it at an eased pace.
export const smoothPolyline = (pts: Pt[], samplesPerSegment = 24): Pt[] => {
	if (pts.length < 3) {
		return pts;
	}
	const out: Pt[] = [];
	for (let i = 0; i < pts.length - 1; i++) {
		const p0 = pts[Math.max(0, i - 1)];
		const p1 = pts[i];
		const p2 = pts[i + 1];
		const p3 = pts[Math.min(pts.length - 1, i + 2)];
		for (let s = 0; s < samplesPerSegment; s++) {
			const t = s / samplesPerSegment;
			const t2 = t * t;
			const t3 = t2 * t;
			out.push({
				x: 0.5 * (2 * p1.x + (-p0.x + p2.x) * t + (2 * p0.x - 5 * p1.x + 4 * p2.x - p3.x) * t2 + (-p0.x + 3 * p1.x - 3 * p2.x + p3.x) * t3),
				y: 0.5 * (2 * p1.y + (-p0.y + p2.y) * t + (2 * p0.y - 5 * p1.y + 4 * p2.y - p3.y) * t2 + (-p0.y + 3 * p1.y - 3 * p2.y + p3.y) * t3),
			});
		}
	}
	out.push(pts[pts.length - 1]);
	return out;
};

export const pointAlong = (poly: Pt[], fraction: number): Pt => {
	if (poly.length === 0) {
		return {x: 0, y: 0};
	}
	if (poly.length === 1) {
		return poly[0];
	}
	const lens: number[] = [0];
	for (let i = 1; i < poly.length; i++) {
		lens.push(lens[i - 1] + Math.hypot(poly[i].x - poly[i - 1].x, poly[i].y - poly[i - 1].y));
	}
	const target = clamp01(fraction) * lens[lens.length - 1];
	let i = 1;
	while (i < lens.length - 1 && lens[i] < target) {
		i++;
	}
	const seg = lens[i] - lens[i - 1] || 1;
	const k = (target - lens[i - 1]) / seg;
	return {x: lerp(poly[i - 1].x, poly[i].x, k), y: lerp(poly[i - 1].y, poly[i].y, k)};
};

export const quadBezier = (a: Pt, c: Pt, b: Pt, t: number): Pt => ({
	x: (1 - t) * (1 - t) * a.x + 2 * (1 - t) * t * c.x + t * t * b.x,
	y: (1 - t) * (1 - t) * a.y + 2 * (1 - t) * t * c.y + t * t * b.y,
});

// Control point that bows a straight line sideways by `bend` × its length.
export const bendControl = (a: Pt, b: Pt, bend: number): Pt => {
	const mx = (a.x + b.x) / 2;
	const my = (a.y + b.y) / 2;
	const dx = b.x - a.x;
	const dy = b.y - a.y;
	return {x: mx - dy * bend, y: my + dx * bend};
};

// The two outer tangent lines joining a small circle to a big one.
export const outerTangents = (c1: Pt, r1: number, c2: Pt, r2: number): [Pt, Pt][] => {
	const dx = c2.x - c1.x;
	const dy = c2.y - c1.y;
	const d = Math.hypot(dx, dy);
	if (d <= Math.abs(r2 - r1) + 0.5) {
		return [];
	}
	const theta = Math.atan2(dy, dx);
	const alpha = Math.acos((r1 - r2) / d);
	return [1, -1].map((s) => {
		const phi = theta + s * alpha;
		const ux = Math.cos(phi);
		const uy = Math.sin(phi);
		return [
			{x: c1.x + r1 * ux, y: c1.y + r1 * uy},
			{x: c2.x + r2 * ux, y: c2.y + r2 * uy},
		] as [Pt, Pt];
	});
};
