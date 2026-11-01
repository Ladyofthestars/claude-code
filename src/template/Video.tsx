import '@fontsource/montserrat/500.css';
import '@fontsource/montserrat/700.css';
import React, {useEffect, useMemo, useState} from 'react';
import {AbsoluteFill, Audio, continueRender, delayRender, Img, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {buildScene} from './scene';
import type {Settings, Words} from './types';

export type VideoProps = {
	video: string;
	settings?: Settings;
	words?: Words;
};

const useFont = (family: string) => {
	const [handle] = useState(() => delayRender(`font ${family}`));
	useEffect(() => {
		Promise.all([document.fonts.load(`700 64px "${family}"`), document.fonts.load(`500 64px "${family}"`)])
			.then(() => continueRender(handle))
			.catch(() => continueRender(handle));
	}, [family, handle]);
};

export const Video: React.FC<VideoProps> = ({video, settings, words}) => {
	if (!settings || !words) {
		throw new Error('Settings were not loaded. Check public/videos/<name>/settings.json');
	}
	useFont(settings.theme.font);
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	const t = frame / fps;
	const scene = useMemo(() => buildScene(settings, words), [settings, words]);
	const theme = settings.theme;
	// Paths starting with / are from the public folder, so parts of one video can share pictures.
	const base = (p: string) => (p.startsWith('/') ? staticFile(p.slice(1)) : staticFile(`videos/${video}/${p}`));
	const FRAME = scene.frame;
	const inkOf = (c?: string) => (c === 'accent' ? theme.accent : c === 'muted' ? `${theme.ink}66` : theme.ink);

	// The dot grid follows the camera a little slower than the page. It depends only on the
	// camera, so parts of a long video join seamlessly when their cameras match.
	const cam = scene.camAt(t);
	const grid = {x: cam.x * theme.dotParallax, y: cam.y * theme.dotParallax, z: Math.pow(cam.z, theme.dotParallax)};
	const spacing = theme.dotSpacing * grid.z;
	const gx = scene.toScreen({x: 0, y: 0}, grid);

	const items = [...settings.items].sort((a, b) => (b.depth ?? 1) - (a.depth ?? 1));
	const lights = scene.lightsAt(t);
	const blend = theme.lightBlend === 'screen' ? 'screen' : 'normal';

	// A soft light: a wide warm halo with a brighter core. Never a hard dot.
	const glow = (x: number, y: number, size: number, alpha: number, key: string) => {
		const halo = size * 1.9;
		const core = size * 0.6;
		const a = Math.min(1, alpha);
		return (
			<React.Fragment key={key}>
				<div
					style={{
						position: 'absolute',
						left: x - halo / 2,
						top: y - halo / 2,
						width: halo,
						height: halo,
						borderRadius: '50%',
						opacity: a * 0.75,
						background: `radial-gradient(circle, ${theme.accent}99 0%, ${theme.accent}40 35%, ${theme.accent}00 70%)`,
						filter: `blur(${Math.max(2, halo * 0.08)}px)`,
						mixBlendMode: blend,
					}}
				/>
				<div
					style={{
						position: 'absolute',
						left: x - core / 2,
						top: y - core / 2,
						width: core,
						height: core,
						borderRadius: '50%',
						opacity: a,
						background: `radial-gradient(circle, #fffaf0 0%, #ffe9b8 22%, ${theme.accent} 48%, ${theme.accent}00 72%)`,
						filter: `blur(${Math.max(1.5, core * 0.12)}px)`,
						mixBlendMode: blend,
					}}
				/>
			</React.Fragment>
		);
	};

	return (
		<AbsoluteFill style={{backgroundColor: theme.background, overflow: 'hidden'}}>
			{/* Faint dot grid on the page, so the camera move can be felt. */}
			<AbsoluteFill
				style={{
					backgroundImage: `radial-gradient(circle, ${theme.dotColor} ${theme.dotSize * Math.sqrt(grid.z)}px, transparent ${theme.dotSize * Math.sqrt(grid.z) + 0.8}px)`,
					backgroundSize: `${spacing}px ${spacing}px`,
					backgroundPosition: `${gx.x - spacing / 2}px ${gx.y - spacing / 2}px`,
				}}
			/>

			{items.map((def) => {
				const s = scene.itemAt(def.id, t);
				if (s.opacity <= 0.001) {
					return null;
				}
				return (
					<Img
						key={def.id}
						src={base(s.src)}
						style={{
							position: 'absolute',
							left: s.left,
							top: s.top,
							width: s.width,
							height: s.height,
							opacity: s.opacity,
							filter: s.blur > 0.05 ? `blur(${s.blur}px)` : undefined,
						}}
					/>
				);
			})}

			<svg width={FRAME.width} height={FRAME.height} style={{position: 'absolute', left: 0, top: 0}}>
				{settings.threads.map((d) => {
					const th = scene.threadAt(d, t);
					if (th.opacity <= 0.001) {
						return null;
					}
					return (
						<path
							key={d.id}
							d={`M ${th.a.x} ${th.a.y} Q ${th.c.x} ${th.c.y} ${th.b.x} ${th.b.y}`}
							pathLength={1}
							strokeDasharray="1 1"
							strokeDashoffset={1 - th.progress}
							fill="none"
							stroke={d.color === 'ink' ? theme.ink : theme.accent}
							strokeWidth={Math.max(1.2, (d.width ?? 2.2) * th.zoom)}
							strokeLinecap="round"
							opacity={th.opacity * 0.85}
						/>
					);
				})}
			</svg>

			{lights.map((l, i) => glow(l.x, l.y, l.size, l.alpha, `light-${i}`))}

			{settings.magnifiers.map((m, mi) => {
				const g = scene.magnifierAt(m, t);
				if (g.k * g.guard <= 0.001) {
					return null;
				}
				const d = g.radius * 2;
				return (
					<React.Fragment key={`mag-${mi}`}>
						<div style={{opacity: g.guard}}>
						<svg width={FRAME.width} height={FRAME.height} style={{position: 'absolute', left: 0, top: 0}}>
							<circle cx={g.source.x} cy={g.source.y} r={g.source.r} fill="none" stroke={theme.ink} strokeWidth={1.6} opacity={0.7 * Math.min(1, g.k * 3)} />
							{g.lines.map(([a, b], li) => (
								<line key={li} x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke={theme.ink} strokeWidth={1.3} opacity={0.55 * g.lineAlpha} />
							))}
						</svg>
						<div
							style={{
								position: 'absolute',
								left: g.center.x - g.radius,
								top: g.center.y - g.radius,
								width: d,
								height: d,
								borderRadius: '50%',
								overflow: 'hidden',
								backgroundColor: theme.background,
								boxShadow: `0 0 0 ${Math.max(1.5, g.radius * 0.008)}px ${theme.ink}`,
								opacity: Math.min(1, g.k * 1.6),
								filter: g.k < 1 ? `blur(${(1 - g.k) * 6}px)` : undefined,
							}}
						>
							{g.contents.map((c, ci) =>
								c.opacity <= 0.001 ? null : (
									<React.Fragment key={ci}>
										<Img
											src={base(c.src)}
											style={{
												position: 'absolute',
												left: c.left - (g.center.x - g.radius),
												top: c.top - (g.center.y - g.radius),
												width: c.width,
												height: c.height,
												opacity: c.opacity,
												filter: c.blur > 0.05 ? `blur(${c.blur}px)` : undefined,
											}}
										/>
										{c.lights.map((l, li) =>
											glow(l.x - (g.center.x - g.radius), l.y - (g.center.y - g.radius), l.size, l.alpha * c.opacity, `ml-${ci}-${li}`),
										)}
									</React.Fragment>
								),
							)}
						</div>
						</div>
					</React.Fragment>
				);
			})}

			<svg width={FRAME.width} height={FRAME.height} style={{position: 'absolute', left: 0, top: 0}}>
				{(settings.drawings ?? []).map((d) => {
					const g = scene.drawingAt(d, t);
					if (g.opacity <= 0.001 || g.pts.length < 2) {
						return null;
					}
					const path = g.pts.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(' ');
					const stroke = inkOf(d.color);
					const w = Math.max(1.2, (d.width ?? 2.4) * Math.min(1.6, g.zoom));
					const hs = w * 4.2;
					return (
						<g key={d.id} opacity={g.opacity} style={g.blur > 0 ? {filter: `blur(${g.blur}px)`} : undefined}>
							{g.fill > 0 ? <path d={path + ' Z'} fill={d.fill === 'paper' ? theme.background : theme.accent} opacity={d.fill === 'paper' ? 1 : g.fill} stroke="none" /> : null}
							<path
								d={path}
								pathLength={1}
								strokeDasharray={d.dashed ? `${w * 3} ${w * 3}` : '1 1'}
								strokeDashoffset={d.dashed ? 0 : 1 - g.progress}
								fill="none"
								stroke={stroke}
								strokeWidth={w}
								strokeLinecap="round"
								strokeLinejoin="round"
							/>
							{g.head && g.progress > 0.02 ? (
								<path
									d={`M ${-hs} ${-hs * 0.55} L 0 0 L ${-hs} ${hs * 0.55}`}
									transform={`translate(${g.head.x} ${g.head.y}) rotate(${(g.head.angle * 180) / Math.PI})`}
									fill="none"
									stroke={stroke}
									strokeWidth={w}
									strokeLinecap="round"
									strokeLinejoin="round"
									opacity={Math.min(1, g.progress * 3)}
								/>
							) : null}
						</g>
					);
				})}
			</svg>

			{settings.labels.map((l, li) => {
				const s = scene.labelAt(l, t);
				if (s.opacity <= 0.001) {
					return null;
				}
				return (
					<div
						key={`label-${li}`}
						style={{
							position: 'absolute',
							left: s.x,
							top: s.y,
							transform: `translate(-50%, -50%) scale(${s.scale})`,
							whiteSpace: 'nowrap',
							fontFamily: `"${theme.font}", sans-serif`,
							fontWeight: l.weight ?? 700,
							fontSize: s.size,
							letterSpacing: `${l.spacing ?? 0.32}em`,
							paddingLeft: `${l.spacing ?? 0.32}em`,
							textTransform: 'uppercase',
							color: l.color === 'accent' ? theme.accent : theme.ink,
							opacity: s.opacity,
							filter: s.blur > 0.05 ? `blur(${s.blur}px)` : undefined,
						}}
					>
						{s.text}
					</div>
				);
			})}

			<Audio src={base(settings.audio)} />
		</AbsoluteFill>
	);
};
