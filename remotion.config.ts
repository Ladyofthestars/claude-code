import fs from 'node:fs';
import {Config} from '@remotion/cli/config';

Config.setEntryPoint('src/index.ts');
Config.setVideoImageFormat('jpeg');
Config.setJpegQuality(92);
Config.setPixelFormat('yuv420p');
Config.setCodec('h264');

// Use the browser that is already installed on this machine, if there is one.
const preinstalled = '/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell';
if (fs.existsSync(preinstalled)) {
	Config.setBrowserExecutable(preinstalled);
	Config.setChromeMode('headless-shell');
}
