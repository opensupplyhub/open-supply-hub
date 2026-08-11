// Standalone jest config replacing the react-scripts (CRA 4) managed setup.
// Mirrors the CRA conventions this suite was written against.
module.exports = {
    // The previous test script ran `craco test --env=node`; setupTests.js
    // builds its own JSDOM on top of the node environment.
    testEnvironment: 'node',
    roots: ['<rootDir>/src'],
    testMatch: [
        '<rootDir>/src/**/__tests__/**/*.{js,jsx}',
        '<rootDir>/src/**/*.{spec,test}.{js,jsx}',
    ],
    setupFilesAfterEnv: ['<rootDir>/src/setupTests.js'],
    transform: {
        '^.+\\.(js|jsx)$': 'babel-jest',
    },
    moduleNameMapper: {
        // SVGs imported as React components (vite-plugin-svgr `?react`).
        '^.+\\.svg\\?react$': '<rootDir>/config/jest/svgrMock.jsx',
        // Styles: class-name lookups return the key itself.
        '^.+\\.(css|scss|sass)$': 'identity-obj-proxy',
        // Other static assets resolve to a filename string.
        '^.+\\.(jpg|jpeg|png|gif|webp|svg|ttf|woff|woff2)$':
            '<rootDir>/config/jest/fileMock.js',
    },
    moduleFileExtensions: ['js', 'jsx', 'json'],
    collectCoverageFrom: ['src/**/*.{js,jsx}', '!src/**/*.d.ts'],
    coverageDirectory: 'coverage',
    resetMocks: true,
};
