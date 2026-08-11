jest.mock('../../util/env');

const mockBundledTaxonomy = Object.freeze({
    sections: [{ code: 'A', label: 'Bundled taxonomy' }],
});

jest.mock('../../data/isicRev4Taxonomy', () => ({
    ISIC_REV4_TAXONOMY: mockBundledTaxonomy,
}));

describe('loadIsic4Taxonomy', () => {
    let env;
    let loadIsic4Taxonomy;
    let isIsic4TaxonomyFeatureEnabled;

    beforeEach(async () => {
        jest.resetModules();
        jest.clearAllMocks();

        env = (await import('../../util/env')).default;
        env.mockImplementation(key => {
            const values = {
                ISIC4_TAXONOMY_ENABLED: 'true',
                ISIC4_TAXONOMY_VERSION: '1',
                ISIC4_TAXONOMY_BUNDLE_URL: '',
                ENVIRONMENT: 'production',
            };
            return values[key];
        });

        ({ loadIsic4Taxonomy, isIsic4TaxonomyFeatureEnabled } = await import(
            '../../data/loadIsic4Taxonomy'
        ));
    });

    test('isIsic4TaxonomyFeatureEnabled accepts boolean and string values', () => {
        env.mockImplementation(key =>
            key === 'ISIC4_TAXONOMY_ENABLED' ? true : undefined,
        );
        expect(isIsic4TaxonomyFeatureEnabled()).toBe(true);

        env.mockImplementation(key =>
            key === 'ISIC4_TAXONOMY_ENABLED' ? 'true' : undefined,
        );
        expect(isIsic4TaxonomyFeatureEnabled()).toBe(true);

        env.mockImplementation(key =>
            key === 'ISIC4_TAXONOMY_ENABLED' ? 'false' : undefined,
        );
        expect(isIsic4TaxonomyFeatureEnabled()).toBe(false);
    });

    test('returns null when the feature flag is disabled', async () => {
        env.mockImplementation(key =>
            key === 'ISIC4_TAXONOMY_ENABLED' ? 'false' : undefined,
        );

        await expect(loadIsic4Taxonomy()).resolves.toBeNull();
    });

    test('falls back to the bundled taxonomy when no bundle URL is configured', async () => {
        await expect(loadIsic4Taxonomy()).resolves.toBe(mockBundledTaxonomy);
    });

    test('caches taxonomy loads for the same version', async () => {
        const first = await loadIsic4Taxonomy();
        const second = await loadIsic4Taxonomy();

        expect(first).toBe(mockBundledTaxonomy);
        expect(second).toBe(first);
    });

    test('reloads taxonomy when the configured version changes', async () => {
        await loadIsic4Taxonomy();

        env.mockImplementation(key => {
            const values = {
                ISIC4_TAXONOMY_ENABLED: 'true',
                ISIC4_TAXONOMY_VERSION: '2',
                ISIC4_TAXONOMY_BUNDLE_URL: '',
            };
            return values[key];
        });

        const reloaded = await loadIsic4Taxonomy();

        expect(reloaded).toBe(mockBundledTaxonomy);
    });

    test('requests the configured bundle URL when dynamic import fails', async () => {
        const bundleUrl = 'https://example.com/isicRev4Taxonomy.js';

        env.mockImplementation(key => {
            const values = {
                ISIC4_TAXONOMY_ENABLED: 'true',
                ISIC4_TAXONOMY_VERSION: 'remote',
                ISIC4_TAXONOMY_BUNDLE_URL: bundleUrl,
                ENVIRONMENT: 'production',
            };
            return values[key];
        });

        global.fetch = jest.fn(() =>
            Promise.resolve({
                ok: false,
                status: 404,
            }),
        );

        await expect(loadIsic4Taxonomy()).rejects.toThrow();

        expect(global.fetch).toHaveBeenCalledWith(bundleUrl);
    });

    test('rewrites minio host to localhost before fetching bundle fallback', async () => {
        env.mockImplementation(key => {
            const values = {
                ISIC4_TAXONOMY_ENABLED: 'true',
                ISIC4_TAXONOMY_VERSION: 'local',
                ISIC4_TAXONOMY_BUNDLE_URL:
                    'https://minio:9000/files/taxonomy/isicRev4Taxonomy.js',
                ENVIRONMENT: 'local',
            };
            return values[key];
        });

        global.fetch = jest.fn(() =>
            Promise.resolve({
                ok: true,
                text: () =>
                    Promise.resolve(
                        'export const ISIC_REV4_TAXONOMY = {"sections":[]};',
                    ),
            }),
        );
        global.URL.createObjectURL = jest.fn(() => 'blob:mock-local-bundle');
        global.URL.revokeObjectURL = jest.fn();

        await expect(loadIsic4Taxonomy()).rejects.toThrow();

        expect(global.fetch).toHaveBeenCalledWith(
            'https://localhost:9000/files/taxonomy/isicRev4Taxonomy.js',
        );
    });
});
