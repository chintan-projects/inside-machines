import { readdirSync, readFileSync, writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
const files = ['/', '/manifest.webmanifest', '/icon.svg', '/icon-192.png', '/icon-512.png', ...readdirSync('dist/assets').filter(f => /\.(js|css)$/.test(f)).map(f => `/assets/${f}`)];
writeFileSync('dist/shell-assets.json', JSON.stringify(files));
const digest = createHash('sha256');
for (const file of files) digest.update(readFileSync(file === '/' ? 'dist/index.html' : `dist${file}`));
const version = digest.digest('hex').slice(0, 12);
writeFileSync('dist/sw.js', readFileSync('scripts/service-worker.js', 'utf8').replace('inside-shell-v1', `inside-shell-${version}`));
