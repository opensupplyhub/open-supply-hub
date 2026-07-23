import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import svgr from 'vite-plugin-svgr';
import browserslistToEsbuild from 'browserslist-to-esbuild';

// Vite 8 no longer reads package.json "browserslist" for build.target and
// defaults to a modern-only baseline, which would narrow our support policy.
// Derive an explicit esbuild target from the same "browserslist" field
// (single source of truth — it also drives autoprefixer) so the supported
// browser set is unchanged and reviewable.
const buildTarget = browserslistToEsbuild();

// Paths the dev server forwards to django (was src/setupProxy.js under CRA).
const pathsToProxy = [
    '/api',
    '/web',
    '/api-auth',
    '/rest-auth',
    '/user-login',
    '/user-logout',
    '/user-signup',
    '/user-profile',
    '/api-token-auth',
    '/user-api-info',
    '/api-feature-flags',
    '/tile',
];

const djangoProxy = Object.fromEntries(
    pathsToProxy.map(path => [path, { target: 'http://django:8081' }]),
);

export default defineConfig(({ mode }) => {
    // Build-time env vars (REACT_APP_*) are injected by the Docker/CI build.
    // util/env.js falls back to process.env when a key is absent from the
    // runtime window.ENVIRONMENT, so keep that contract working under Vite.
    const env = loadEnv(mode, process.cwd(), 'REACT_APP_');

    return {
        plugins: [
            react({
                babel: {
                    plugins: [
                        [
                            '@babel/plugin-proposal-class-properties',
                            { loose: true },
                        ],
                    ],
                },
            }),
            svgr(),
        ],
        envPrefix: 'REACT_APP_',
        define: {
            // Browserify/webpack-era dependencies (object-hash's browser
            // bundle among them) reference node's `global`; map it to the
            // standard globalThis.
            global: 'globalThis',
            // CRA exposed the whole env object, so dynamic access like
            // process.env[v] worked. Reproduce that with the REACT_APP_
            // subset plus NODE_ENV.
            'process.env': JSON.stringify({
                ...env,
                NODE_ENV: mode === 'production' ? 'production' : 'development',
            }),
        },
        server: {
            host: true,
            port: 6543,
            // Vite blocks requests whose Host header isn't recognized
            // (DNS-rebinding protection). Allow the 'react' service name so
            // the e2e container and other compose services can reach the dev
            // server at http://react:6543. CRA's webpack-dev-server did not
            // enforce this, so it worked implicitly before.
            allowedHosts: ['react', 'localhost'],
            // Docker bind mounts need polling (was CHOKIDAR_USEPOLLING).
            watch: {
                usePolling: true,
                interval: 100,
            },
            proxy: djangoProxy,
        },
        build: {
            // Keep CRA's output directory so deploy tooling is untouched.
            outDir: 'build',
            target: buildTarget,
            cssTarget: buildTarget,
        },
    };
});
