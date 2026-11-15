#!/usr/bin/env node
/**
 * Rebuild @45ck/content-machine dist after a GitHub install.
 * The published tarball ships prebuilt dist; the GitHub master checkout does not.
 */
import { spawnSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const pkg = path.join(root, 'node_modules', '@45ck', 'content-machine');
const esbuildBin = path.join(root, 'node_modules', '.bin', 'esbuild');

if (!existsSync(pkg)) {
  console.error('Missing @45ck/content-machine. Run: npm install');
  process.exit(1);
}

if (!existsSync(esbuildBin)) {
  console.error('Missing esbuild. Run: npm install');
  process.exit(1);
}

function run(args) {
  const result = spawnSync(esbuildBin, args, {
    cwd: pkg,
    stdio: 'inherit',
  });
  if (result.status !== 0) {
    process.exit(result.status ?? 1);
  }
}

const silent = '--log-override:empty-import-meta=silent';

run([
  'src/cli/index.ts',
  '--bundle',
  '--platform=node',
  '--format=cjs',
  '--packages=external',
  silent,
  '--outfile=dist/cli/index.cjs',
]);

run([
  'src/index.ts',
  '--bundle',
  '--platform=node',
  '--format=esm',
  '--packages=external',
  silent,
  '--sourcemap',
  '--outfile=dist/index.js',
]);

run([
  'src/index.ts',
  '--bundle',
  '--platform=node',
  '--format=cjs',
  '--packages=external',
  silent,
  '--sourcemap',
  '--outfile=dist/index.cjs',
]);

console.log('Built @45ck/content-machine dist');
