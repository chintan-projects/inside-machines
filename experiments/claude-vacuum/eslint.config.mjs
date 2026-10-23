import js from '@eslint/js';
import globals from 'globals';

export default [{
  files: ['**/*.mjs'],
  languageOptions: {globals: {...globals.node, ...globals.browser}},
  rules: js.configs.recommended.rules,
}];
