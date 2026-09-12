// Used by babel-jest for the test suite. The Vite build configures babel
// separately via @vitejs/plugin-react in vite.config.js.
module.exports = {
    presets: [
        ['@babel/preset-env', { targets: { node: 'current' } }],
        // CRA 4 used the automatic JSX runtime (react >=16.14 provides
        // react/jsx-runtime), so many components use JSX without importing
        // React. Keep that behavior.
        ['@babel/preset-react', { runtime: 'automatic' }],
    ],
    plugins: [['@babel/plugin-proposal-class-properties', { loose: true }]],
};
