// ESLint flat config. Uses only core rules so it runs through `npx eslint`
// without installing any plugin or shared-config package.
const rules = {
  'no-undef': 'error',
  'no-unused-vars': ['error', { args: 'none' }],
  'no-redeclare': 'error',
  'no-dupe-keys': 'error',
  'no-unreachable': 'error',
  'no-constant-condition': 'error',
  'no-self-compare': 'error',
  'use-isnan': 'error',
  'valid-typeof': 'error',
  eqeqeq: ['error', 'smart'],
  'prefer-const': 'error',
  'no-var': 'error',
};

const browserGlobals = Object.fromEntries(
  [
    'window',
    'document',
    'fetch',
    'console',
    'alert',
    'confirm',
    'URLSearchParams',
    'setTimeout',
    'clearTimeout',
  ].map((name) => [name, 'readonly']),
);

const nodeGlobals = Object.fromEntries(
  ['console', 'URL', 'process'].map((name) => [name, 'readonly']),
);

export default [
  {
    files: ['public/**/*.js'],
    languageOptions: { ecmaVersion: 2022, sourceType: 'script', globals: browserGlobals },
    rules,
  },
  {
    files: ['**/*.mjs'],
    languageOptions: { ecmaVersion: 2022, sourceType: 'module', globals: nodeGlobals },
    rules,
  },
];
