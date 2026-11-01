import React from 'react';
import {Composition, staticFile} from 'remotion';
import {Video, type VideoProps} from './template/Video';
import {FRAME} from './template/scene';
import type {Settings, Words} from './template/types';

const FPS = 60;

// Which video to make. Each video is a folder in public/videos/ with one settings.json.
// Pick another with: npx remotion render Video out/video.mp4 --props='{"video":"my-next-video"}'
const DEFAULT_VIDEO = 'new-earth';

export const Root: React.FC = () => (
	<Composition
		id="Video"
		component={Video}
		fps={FPS}
		width={FRAME.width}
		height={FRAME.height}
		durationInFrames={FPS * 30}
		defaultProps={{video: DEFAULT_VIDEO} as VideoProps}
		calculateMetadata={async ({props}) => {
			const dir = `videos/${props.video}/`;
			const settings: Settings = await (await fetch(staticFile(`${dir}settings.json`))).json();
			const words: Words = await (await fetch(staticFile(`${dir}${settings.words}`))).json();
			return {
				// As long as the voice, plus the tail (one second).
				durationInFrames: Math.ceil((words.duration + settings.tailSeconds) * FPS),
				props: {...props, settings, words},
			};
		}}
	/>
);
