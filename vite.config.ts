import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';

export default defineConfig({
  plugins: [react()],
  define:{__AC_SCENE_HASH__:JSON.stringify(createHash('sha256').update(readFileSync('public/figures/ac-outside.svg')).update(readFileSync('public/figures/ac-inside.svg')).digest('hex'))},
  server: { host: '127.0.0.1', port: 5173, proxy: { '/api': 'http://127.0.0.1:8000' } },
  build: { outDir: 'dist', emptyOutDir: true },
});
