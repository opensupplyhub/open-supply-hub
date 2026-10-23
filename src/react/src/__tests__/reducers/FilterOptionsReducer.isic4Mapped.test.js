import reducer from '../../reducers/FilterOptionsReducer';
import {
    completeFetchIsic4MappedExtraCount,
    completeFetchTaxonomyCounts,
    failFetchIsic4MappedExtraCount,
    startFetchIsic4MappedExtraCount,
    startFetchTaxonomyCounts,
} from '../../actions/filterOptions';

const initialState = reducer(undefined, { type: '@@INIT' });

describe('FilterOptionsReducer ISIC mapped values', () => {
    test('keeps submitted-only and mapped counts apart', () => {
        let state = reducer(
            initialState,
            startFetchTaxonomyCounts('isic4Mapped'),
        );
        expect(state.taxonomyCounts.isic4Mapped.fetching).toBe(true);
        expect(state.taxonomyCounts.isic4.fetching).toBe(false);

        state = reducer(
            state,
            completeFetchTaxonomyCounts({
                kind: 'isic4Mapped',
                data: { 'section:C': 3 },
            }),
        );
        expect(state.taxonomyCounts.isic4Mapped.data).toEqual({
            'section:C': 3,
        });
        expect(state.taxonomyCounts.isic4.data).toBeNull();
    });

    test('still stores isic4 counts dispatched without a kind', () => {
        const state = reducer(
            initialState,
            completeFetchTaxonomyCounts({ data: { 'section:C': 1 } }),
        );
        expect(state.taxonomyCounts.isic4.data).toEqual({ 'section:C': 1 });
    });

    test('stores the extra count for the current selection', () => {
        let state = reducer(
            initialState,
            startFetchIsic4MappedExtraCount({ requestKey: 'a' }),
        );
        state = reducer(
            state,
            completeFetchIsic4MappedExtraCount({ requestKey: 'a', count: 7 }),
        );
        expect(state.isic4MappedExtraCount.count).toBe(7);
        expect(state.isic4MappedExtraCount.fetching).toBe(false);
    });

    test('ignores a late response for an earlier selection', () => {
        let state = reducer(
            initialState,
            startFetchIsic4MappedExtraCount({ requestKey: 'old' }),
        );
        state = reducer(
            state,
            startFetchIsic4MappedExtraCount({ requestKey: 'new' }),
        );
        state = reducer(
            state,
            completeFetchIsic4MappedExtraCount({ requestKey: 'old', count: 99 }),
        );
        state = reducer(
            state,
            failFetchIsic4MappedExtraCount({ requestKey: 'old', error: ['x'] }),
        );
        expect(state.isic4MappedExtraCount).toEqual({
            requestKey: 'new',
            count: null,
            fetching: true,
            error: null,
        });
    });
});
