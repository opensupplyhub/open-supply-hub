jest.mock('../../util/env');

const mockTaxonomy = Object.freeze({
    sections: [{ code: 'A', label: 'Remote taxonomy', divisions: [] }],
});

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
                ISIC4_TAXONOMY_URL: '/api/taxonomy/isic4/',
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

    test('loads taxonomy JSON from the Django API endpoint', async () => {
        global.fetch = jest.fn(() =>
            Promise.resolve({
                ok: true,
                json: () => Promise.resolve(mockTaxonomy),
            }),
        );

        await expect(loadIsic4Taxonomy()).resolves.toBe(mockTaxonomy);
        expect(global.fetch).toHaveBeenCalledWith('/api/taxonomy/isic4/');
    });

    test('caches taxonomy loads for the same version', async () => {
        global.fetch = jest.fn(() =>
            Promise.resolve({
                ok: true,
                json: () => Promise.resolve(mockTaxonomy),
            }),
        );

        const first = await loadIsic4Taxonomy();
        const second = await loadIsic4Taxonomy();

        expect(first).toBe(mockTaxonomy);
        expect(second).toBe(first);
        expect(global.fetch).toHaveBeenCalledTimes(1);
    });

    test('reloads taxonomy when the configured version changes', async () => {
        global.fetch = jest.fn(() =>
            Promise.resolve({
                ok: true,
                json: () => Promise.resolve(mockTaxonomy),
            }),
        );

        await loadIsic4Taxonomy();

        env.mockImplementation(key => {
            const values = {
                ISIC4_TAXONOMY_ENABLED: 'true',
                ISIC4_TAXONOMY_VERSION: '2',
                ISIC4_TAXONOMY_URL: '/api/taxonomy/isic4/',
            };
            return values[key];
        });

        const reloaded = await loadIsic4Taxonomy();

        expect(reloaded).toBe(mockTaxonomy);
        expect(global.fetch).toHaveBeenCalledTimes(2);
    });

    test('throws when the taxonomy API request fails', async () => {
        global.fetch = jest.fn(() =>
            Promise.resolve({
                ok: false,
                status: 404,
            }),
        );

        await expect(loadIsic4Taxonomy()).rejects.toThrow(
            'Failed to load ISIC taxonomy (404)',
        );
    });
});
