import { execFileSync } from 'node:child_process';
// Python dependency installation remains the framework's responsibility.
execFileSync('npm', ['ci'], { stdio: 'inherit' });
execFileSync('npm', ['run', 'build'], { stdio: 'inherit' });
