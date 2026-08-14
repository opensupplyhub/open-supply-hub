import configureStore from 'redux-mock-store';
import thunk from 'redux-thunk';

import {
    completeFetchIsic4Taxonomy,
    completeFetchIsic4TaxonomyConfig,
    failFetchIsic4Taxonomy,
    failFetchIsic4TaxonomyConfig,
    fetchIsic4Taxonomy,
    fetchIsic4TaxonomyConfig,
    fetchIsic4TaxonomyConfigIfNeeded,
    fetchIsic4TaxonomyIfNeeded,
    startFetchIsic4Taxonomy,
    startFetchIsic4TaxonomyConfig,
} from '../../actions/filterOptions';
import FilterOptionsReducer from '../../reducers/FilterOptionsReducer';

const mockStore = configureStore([thunk]);

const mockTaxonomy = Object.freeze({
    sections: [{ code: 'A', label: 'Remote taxonomy', divisions: [] }],
});

const mockIsic4Config = Object.freeze({
    enabled: true,
    version: 1,
    taxonomyUrl: '/api/taxonomy/isic4/?v=1',
});

describe('ISIC taxonomy filterOptions actions', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    test('fetchIsic4TaxonomyConfig stores config in filterOptions', async () => {
        global.fetch = jest.fn(() =>
            Promise.resolve({
                ok: true,
                json: () => Promise.resolve({ isic4: mockIsic4Config }),
            }),
        );

        const store = mockStore({});
        await store.dispatch(fetchIsic4TaxonomyConfig());

        expect(global.fetch).toHaveBeenCalledWith('/api/taxonomy-config/');
        expect(store.getActions()).toEqual([
            startFetchIsic4TaxonomyConfig(),
            completeFetchIsic4TaxonomyConfig(mockIsic4Config),
        ]);
    });

    test('fetchIsic4TaxonomyConfigIfNeeded skips fetch when config is cached', async () => {
        const store = mockStore({
            filterOptions: {
                isic4TaxonomyConfig: {
                    data: mockIsic4Config,
                    fetching: false,
                    error: null,
                },
            },
        });

        global.fetch = jest.fn();
        await store.dispatch(fetchIsic4TaxonomyConfigIfNeeded());

        expect(global.fetch).not.toHaveBeenCalled();
        expect(store.getActions()).toEqual([]);
    });

    test('fetchIsic4Taxonomy loads taxonomy using config from the store', async () => {
        global.fetch = jest.fn(() =>
            Promise.resolve({
                ok: true,
                json: () => Promise.resolve(mockTaxonomy),
            }),
        );

        const store = mockStore({
            filterOptions: {
                isic4TaxonomyConfig: {
                    data: mockIsic4Config,
                    fetching: false,
                    error: null,
                },
            },
        });

        const payload = await store.dispatch(fetchIsic4Taxonomy());

        expect(global.fetch).toHaveBeenCalledWith('/api/taxonomy/isic4/?v=1');
        expect(payload).toEqual({
            taxonomy: mockTaxonomy,
            version: '1',
            taxonomyUrl: '/api/taxonomy/isic4/?v=1',
        });
        expect(store.getActions()).toEqual([
            startFetchIsic4Taxonomy(),
            completeFetchIsic4Taxonomy({
                taxonomy: mockTaxonomy,
                version: '1',
                taxonomyUrl: '/api/taxonomy/isic4/?v=1',
            }),
        ]);
    });

    test('fetchIsic4TaxonomyIfNeeded skips fetch when taxonomy is cached for the URL', async () => {
        const cachedPayload = {
            taxonomy: mockTaxonomy,
            version: '1',
            taxonomyUrl: '/api/taxonomy/isic4/?v=1',
        };
        const store = mockStore({
            filterOptions: {
                isic4TaxonomyConfig: {
                    data: mockIsic4Config,
                    fetching: false,
                    error: null,
                },
                isic4Taxonomy: {
                    data: cachedPayload,
                    taxonomyUrl: '/api/taxonomy/isic4/?v=1',
                    fetching: false,
                    error: null,
                },
            },
        });

        global.fetch = jest.fn();
        const result = await store.dispatch(fetchIsic4TaxonomyIfNeeded());

        expect(result).toBe(cachedPayload);
        expect(global.fetch).not.toHaveBeenCalled();
        expect(store.getActions()).toEqual([]);
    });

    test('reducer stores config and taxonomy fetch state', () => {
        let state = FilterOptionsReducer(undefined, { type: '@@INIT' });

        state = FilterOptionsReducer(
            state,
            startFetchIsic4TaxonomyConfig(),
        );
        expect(state.isic4TaxonomyConfig.fetching).toBe(true);

        state = FilterOptionsReducer(
            state,
            completeFetchIsic4TaxonomyConfig(mockIsic4Config),
        );
        expect(state.isic4TaxonomyConfig.data).toEqual(mockIsic4Config);

        const taxonomyPayload = {
            taxonomy: mockTaxonomy,
            version: '1',
            taxonomyUrl: '/api/taxonomy/isic4/?v=1',
        };

        state = FilterOptionsReducer(state, startFetchIsic4Taxonomy());
        expect(state.isic4Taxonomy.fetching).toBe(true);

        state = FilterOptionsReducer(
            state,
            completeFetchIsic4Taxonomy(taxonomyPayload),
        );
        expect(state.isic4Taxonomy.data).toEqual(taxonomyPayload);
        expect(state.isic4Taxonomy.taxonomyUrl).toBe('/api/taxonomy/isic4/?v=1');

        state = FilterOptionsReducer(
            state,
            failFetchIsic4TaxonomyConfig(['Config failed']),
        );
        expect(state.isic4TaxonomyConfig.error).toEqual(['Config failed']);

        state = FilterOptionsReducer(
            state,
            failFetchIsic4Taxonomy(['Taxonomy failed']),
        );
        expect(state.isic4Taxonomy.error).toEqual(['Taxonomy failed']);
    });
});
