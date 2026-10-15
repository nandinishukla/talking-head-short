// Headless screenshot of a real page (captures for graphics, or a check of the storyboard page). Run from edit/.
//   node shot.mjs <url> <out.png> <width> <height> <fullPage 0|1>
// Uses tools/node_modules/puppeteer-core and HyperFrames' chrome-headless-shell (override with CHROME=...).
import { createRequire } from 'module';
import { existsSync, readdirSync } from 'fs';
import { join } from 'path';
import os from 'os';
const require = createRequire(join(process.cwd(), 'tools', 'package.json'));
const puppeteer = require('puppeteer-core');
function findChrome() {
  if (process.env.CHROME) return process.env.CHROME;
  const base = join(os.homedir(), '.cache/hyperframes/chrome/chrome-headless-shell');
  for (const v of existsSync(base) ? readdirSync(base) : []) {
    for (const d of readdirSync(join(base, v))) {
      const p = join(base, v, d, 'chrome-headless-shell');
      if (existsSync(p)) return p;
    }
  }
  throw new Error('No chrome-headless-shell found: run `tools/node_modules/.bin/hyperframes browser ensure` or set CHROME');
}
const [, , url, out, w, h, full] = process.argv;
const b = await puppeteer.launch({ executablePath: findChrome(), args: ['--no-sandbox', '--force-color-profile=srgb', '--allow-file-access-from-files'] });
const p = await b.newPage();
await p.setViewport({ width: +w, height: +h, deviceScaleFactor: 2 });
await p.emulateMediaFeatures([{ name: 'prefers-color-scheme', value: 'light' }]);
await p.goto(url, { waitUntil: 'networkidle2', timeout: 90000 });
await new Promise((r) => setTimeout(r, 2500));
await p.screenshot({ path: out, fullPage: full === '1' });
await b.close();
