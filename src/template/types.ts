// Everything a video needs lives in one settings.json (see public/videos/<name>/settings.json).
// These types describe that file.

// A moment in the narration. Either seconds, or a text reference:
//   "start" | "end" (video end, after the tail) | "voiceEnd"
//   "<line>:<phrase>"       start of that phrase in that narration line (lines are numbered from 1)
//   "<line>:<phrase>@end"   end of the phrase's last word
//   any of the above + or - seconds, e.g. "3:small light-0.2"
export type TimeRef = number | string;

// A point on a picture, as a fraction of its width and height (0,0 = top left, 1,1 = bottom right).
export type UV = [number, number];

export interface Theme {
	background: string;
	dotColor: string;
	dotSpacing: number;
	dotSize: number;
	// How much the dot grid follows the camera (1 = exactly with the page).
	dotParallax: number;
	ink: string;
	accent: string;
	// 'screen' makes lights add light (for dark pages), 'normal' paints them (for light pages).
	lightBlend: 'screen' | 'normal';
	font: string;
	// Optional extras for dark pages (all off when left out):
	// a CSS gradient painted over the background colour (fixed to the screen, e.g. a vignette)
	backgroundImage?: string;
	// a soft glow around labels and around drawn lines (CSS colours)
	labelGlow?: string;
	drawingGlow?: string;
	// drifting, twinkling specks of light behind everything, following the camera at `parallax`
	dust?: {count: number; color: string; size: number; parallax: number; drift?: number};
}

// A flow of small glowing dots ("atoms") along a path on the page, looping while it is on.
export interface StreamDef {
	id?: string;
	points: [number, number][];
	curve?: boolean;
	from: TimeRef;
	to?: TimeRef;
	// dots on the path at once, seconds for one dot to travel the whole path
	count?: number;
	period?: number;
	// dot diameter and sideways wander, in page units
	size?: number;
	spread?: number;
	color?: 'ink' | 'accent';
	// travel the path backwards
	reverse?: boolean;
}

export interface PictureDef {
	src: string;
	// width / height of the image file
	aspect: number;
	// Where the drawn object sits inside the image, as fractions [left, top, right, bottom].
	content?: [number, number, number, number];
}

export interface ItemDef {
	id: string;
	picture: string;
	// Centre of the image on the page, in page units (1 unit = 1 output pixel at zoom 1).
	x: number;
	y: number;
	width: number;
	// 1 = on the page. Bigger = further away: moves slower and is a little blurred.
	depth?: number;
	in?: TimeRef;
	out?: TimeRef;
	fade?: number;
}

export interface CameraKey {
	at: TimeRef;
	// Frame one or more items: their drawn content fits inside the safe area, times `fit`.
	focus?: string | string[];
	fit?: number;
	// Or place the camera directly (page units / zoom factor).
	x?: number;
	y?: number;
	zoom?: number;
	// Nudge the framed centre (page units).
	dx?: number;
	dy?: number;
	// Stay on this framing for this many seconds before the next move.
	hold?: number;
}

export interface Anchor {
	item: string;
	at: UV;
}

export interface LightDef {
	// A light that travels along a path drawn on a picture...
	item?: string;
	path?: UV[];
	// ...or along a thread, or along a drawing...
	thread?: string;
	drawing?: string;
	// travel the path backwards (end to start)
	reverse?: boolean;
	// ...or glows in place at a point on the page (page units).
	world?: [number, number];
	worldPoints?: [number, number][];
	// ...or a light that glows in place at one or more points of a picture.
	at?: UV;
	points?: UV[];
	stagger?: number;
	from: TimeRef;
	to?: TimeRef;
	duration?: number;
	// Glow diameter in page units.
	size?: number;
	intensity?: number;
}

export interface ThreadDef {
	id: string;
	from: Anchor;
	to: Anchor;
	// Sideways bow of the line, as a fraction of its length.
	bend?: number;
	draw: TimeRef;
	duration?: number;
	out?: TimeRef;
	color?: 'ink' | 'accent';
	width?: number;
}

export interface MagnifierContent {
	picture: string;
	from?: TimeRef;
	to?: TimeRef;
	// Picture width as a fraction of the circle's diameter, and offset as fractions of it.
	scale?: number;
	dx?: number;
	dy?: number;
	lights?: {at: UV; from: TimeRef; size?: number; to?: TimeRef}[];
}

export interface MagnifierDef {
	source: Anchor & {radius: number};
	// Centre and radius of the big circle on the page.
	x: number;
	y: number;
	radius: number;
	open: TimeRef;
	close?: TimeRef;
	contents: MagnifierContent[];
}

export interface LabelDef {
	// Use {n} in the text for a number that counts up, e.g. "{n} TONS".
	text: string;
	count?: {from?: number; to: number; decimals?: number; duration?: number};
	weight?: 500 | 700;
	// false keeps the text's own case (element symbols like Fe, Au)
	upper?: boolean;
	// left: x is where the text starts (for lists)
	align?: 'center' | 'left';
	spacing?: number;
	// Screen pixels (space "screen") or page units (space "world").
	x: number;
	y: number;
	space?: 'screen' | 'world';
	size?: number;
	in: TimeRef;
	out?: TimeRef;
	color?: 'ink' | 'accent';
}

// Diagrams that draw themselves, line by line, on the page.
export interface DrawingDef {
	id: string;
	kind?: 'path' | 'circle' | 'rect';
	// path: points in page units; curve smooths through them.
	points?: [number, number][];
	curve?: boolean;
	closed?: boolean;
	// circle
	cx?: number;
	cy?: number;
	r?: number;
	// rect (centre, size)
	x?: number;
	y?: number;
	w?: number;
	h?: number;
	draw: TimeRef;
	duration?: number;
	out?: TimeRef;
	color?: 'ink' | 'accent' | 'muted';
	width?: number;
	// dashed lines fade in instead of drawing on
	dashed?: boolean;
	arrow?: boolean;
	fill?: 'accent' | 'paper';
	fillOpacity?: number;
	fillAt?: TimeRef;
	depth?: number;
}

export interface Settings {
	title: string;
	size?: {width: number; height: number};
	drawings?: DrawingDef[];
	audio: string;
	words: string;
	tailSeconds: number;
	// Fractions of the frame that must stay free of anything important.
	safeArea: {top: number; bottom: number; side: number};
	theme: Theme;
	pictures: Record<string, PictureDef>;
	items: ItemDef[];
	camera: CameraKey[];
	threads: ThreadDef[];
	lights: LightDef[];
	magnifiers: MagnifierDef[];
	labels: LabelDef[];
	streams?: StreamDef[];
	// Seconds since the start of the whole video when this part starts, so drifting dust
	// continues smoothly across parts.
	clock?: number;
}

export interface Word {
	text: string;
	start: number;
	end: number;
	// Narration line the word belongs to (1-based).
	line: number;
}

export interface Words {
	duration: number;
	words: Word[];
}
