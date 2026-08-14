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

const emptyIsic4TaxonomyState = Object.freeze({
    config: null,
    data: null,
    fetching: false,
    error: null,
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
                isic4Taxonomy: {
                    ...emptyIsic4TaxonomyState,
                    config: mockIsic4Config,
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
                isic4Taxonomy: {
                    ...emptyIsic4TaxonomyState,
                    config: mockIsic4Config,
                },
            },
        });

        const taxonomy = await store.dispatch(fetchIsic4Taxonomy());

        expect(global.fetch).toHaveBeenCalledWith('/api/taxonomy/isic4/?v=1');
        expect(taxonomy).toEqual(mockTaxonomy);
        expect(store.getActions()).toEqual([
            startFetchIsic4Taxonomy(),
            completeFetchIsic4Taxonomy(mockTaxonomy),
        ]);
    });

    test('fetchIsic4Taxonomy refetches after config version change clears cache', async () => {
        const updatedConfig = {
            ...mockIsic4Config,
            version: 2,
            taxonomyUrl: '/api/taxonomy/isic4/?v=2',
        };
        const updatedTaxonomy = Object.freeze({
            sections: [{ code: 'B', label: 'Updated taxonomy', divisions: [] }],
        });

        global.fetch = jest.fn(() =>
            Promise.resolve({
                ok: true,
                json: () => Promise.resolve(updatedTaxonomy),
            }),
        );

        const store = mockStore({
            filterOptions: {
                isic4Taxonomy: {
                    ...emptyIsic4TaxonomyState,
                    config: updatedConfig,
                },
            },
        });

        const result = await store.dispatch(fetchIsic4Taxonomy());

        expect(global.fetch).toHaveBeenCalledWith('/api/taxonomy/isic4/?v=2');
        expect(result).toEqual(updatedTaxonomy);
        expect(store.getActions()).toEqual([
            startFetchIsic4Taxonomy(),
            completeFetchIsic4Taxonomy(updatedTaxonomy),
        ]);
    });

    test('fetchIsic4Taxonomy skips fetch when taxonomy is cached', async () => {
        const store = mockStore({
            filterOptions: {
                isic4Taxonomy: {
                    ...emptyIsic4TaxonomyState,
                    config: mockIsic4Config,
                    data: mockTaxonomy,
                },
            },
        });

        global.fetch = jest.fn();
        const result = await store.dispatch(fetchIsic4Taxonomy());

        expect(result).toBe(mockTaxonomy);
        expect(global.fetch).not.toHaveBeenCalled();
        expect(store.getActions()).toEqual([]);
    });

    test('reducer stores config and taxonomy fetch state', () => {
        let state = FilterOptionsReducer(undefined, { type: '@@INIT' });

        state = FilterOptionsReducer(
            state,
            startFetchIsic4TaxonomyConfig(),
        );
        expect(state.isic4Taxonomy.fetching).toBe(true);

        state = FilterOptionsReducer(
            state,
            completeFetchIsic4TaxonomyConfig(mockIsic4Config),
        );
        expect(state.isic4Taxonomy.config).toEqual(mockIsic4Config);

        state = FilterOptionsReducer(state, startFetchIsic4Taxonomy());
        expect(state.isic4Taxonomy.fetching).toBe(true);

        state = FilterOptionsReducer(
            state,
            completeFetchIsic4Taxonomy(mockTaxonomy),
        );
        expect(state.isic4Taxonomy.data).toEqual(mockTaxonomy);

        state = FilterOptionsReducer(
            state,
            failFetchIsic4TaxonomyConfig(['Config failed']),
        );
        expect(state.isic4Taxonomy.error).toEqual(['Config failed']);

        state = FilterOptionsReducer(
            state,
            failFetchIsic4Taxonomy(['Taxonomy failed']),
        );
        expect(state.isic4Taxonomy.error).toEqual(['Taxonomy failed']);
    });

    test('reducer clears cached taxonomy when config version changes', () => {
        let state = FilterOptionsReducer(undefined, { type: '@@INIT' });

        state = FilterOptionsReducer(
            state,
            completeFetchIsic4TaxonomyConfig(mockIsic4Config),
        );
        state = FilterOptionsReducer(
            state,
            completeFetchIsic4Taxonomy(mockTaxonomy),
        );
        expect(state.isic4Taxonomy.data).toEqual(mockTaxonomy);

        state = FilterOptionsReducer(
            state,
            completeFetchIsic4TaxonomyConfig({
                ...mockIsic4Config,
                version: 2,
                taxonomyUrl: '/api/taxonomy/isic4/?v=2',
            }),
        );

        expect(state.isic4Taxonomy.config.version).toBe(2);
        expect(state.isic4Taxonomy.data).toBeNull();
    });
});
