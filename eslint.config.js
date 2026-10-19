import js from '@eslint/js';
import ts from 'typescript-eslint';
import hooks from 'eslint-plugin-react-hooks';
import globals from 'globals';

export default ts.config(
  { ignores: ['vendor/**', 'dist/**', 'node_modules/**', 'src/**', 'scripts/**', 'tests/**'] },
  js.configs.recommended,
  ...ts.configs.recommended,
  { files: ['web/**/*.{ts,tsx}'], languageOptions: { globals: globals.browser }, plugins: { 'react-hooks': hooks }, rules: hooks.configs.recommended.rules },
  { files: ['*.{js,ts}'], languageOptions: { globals: globals.node } },
);
