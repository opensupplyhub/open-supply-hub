import configureStore from 'redux-mock-store';
import thunk from 'redux-thunk';

import {
    completeFetchProcessingTypeSuggestions,
    failFetchProcessingTypeSuggestions,
    fetchProcessingTypeSuggestions,
    startFetchProcessingTypeSuggestions,
} from '../../actions/filterOptions';
import FilterOptionsReducer from '../../reducers/FilterOptionsReducer';
import apiRequest from '../../util/apiRequest';

jest.mock('../../util/apiRequest', () => ({
    __esModule: true,
    default: { get: jest.fn() },
}));

const mockStore = configureStore([thunk]);

const SUGGESTIONS = Object.freeze([
    Object.freeze({
        value: 'Dyeing',
        count: 1204,
        in_taxonomy: true,
        facility_types: ['Printing, Product Dyeing and Laundering'],
        dim: false,
    }),
]);
const DYEING_REQUEST_IDENTITY =
    '/api/processing-type-suggestions/?q=dyeing';
const FILTERED_DYEING_REQUEST_IDENTITY =
    '/api/processing-type-suggestions/?q=dyeing' +
    '&facility_type=Final+Product+Assembly' +
    '&facility_type=Textile+or+Material+Production';

describe('processing type suggestion filterOptions actions', () => {
    test('fetches suggestions for a query and the selected facility types', async () => {
        apiRequest.get.mockResolvedValue({ data: SUGGESTIONS });

        const store = mockStore({});
        await store.dispatch(
            fetchProcessingTypeSuggestions('dyeing', [
                'Final Product Assembly',
                'Textile or Material Production',
            ]),
        );

        expect(apiRequest.get).toHaveBeenCalledWith(
            FILTERED_DYEING_REQUEST_IDENTITY,
        );
        expect(store.getActions()).toEqual([
            startFetchProcessingTypeSuggestions({
                query: 'dyeing',
                requestIdentity: FILTERED_DYEING_REQUEST_IDENTITY,
            }),
            completeFetchProcessingTypeSuggestions({
                query: 'dyeing',
                requestIdentity: FILTERED_DYEING_REQUEST_IDENTITY,
                data: SUGGESTIONS,
            }),
        ]);
    });

    test('reports a failed fetch against the query it was made for', async () => {
        apiRequest.get.mockRejectedValue(new Error('Network down'));

        const store = mockStore({});
        await store.dispatch(fetchProcessingTypeSuggestions('dyeing'));

        expect(store.getActions()).toEqual([
            startFetchProcessingTypeSuggestions({
                query: 'dyeing',
                requestIdentity: DYEING_REQUEST_IDENTITY,
            }),
            failFetchProcessingTypeSuggestions({
                query: 'dyeing',
                requestIdentity: DYEING_REQUEST_IDENTITY,
                error: [
                    'An error prevented fetching processing type suggestions',
                ],
            }),
        ]);
    });

    test('reducer stores the suggestions of the query in flight', () => {
        let state = FilterOptionsReducer(undefined, { type: '@@INIT' });

        expect(state.processingTypeSuggestions).toEqual({
            query: null,
            requestIdentity: null,
            data: null,
            fetching: false,
            error: null,
        });

        state = FilterOptionsReducer(
            state,
            startFetchProcessingTypeSuggestions({
                query: 'dyeing',
                requestIdentity: DYEING_REQUEST_IDENTITY,
            }),
        );
        expect(state.processingTypeSuggestions.fetching).toBe(true);
        expect(state.processingTypeSuggestions.query).toBe('dyeing');

        state = FilterOptionsReducer(
            state,
            completeFetchProcessingTypeSuggestions({
                query: 'dyeing',
                requestIdentity: DYEING_REQUEST_IDENTITY,
                data: SUGGESTIONS,
            }),
        );
        expect(state.processingTypeSuggestions.fetching).toBe(false);
        expect(state.processingTypeSuggestions.data).toEqual(SUGGESTIONS);
    });

    test('reducer drops a response that answers a stale query', () => {
        let state = FilterOptionsReducer(undefined, { type: '@@INIT' });

        state = FilterOptionsReducer(
            state,
            startFetchProcessingTypeSuggestions({
                query: 'dye',
                requestIdentity: '/api/processing-type-suggestions/?q=dye',
            }),
        );
        state = FilterOptionsReducer(
            state,
            startFetchProcessingTypeSuggestions({
                query: 'dyeing',
                requestIdentity: DYEING_REQUEST_IDENTITY,
            }),
        );
        state = FilterOptionsReducer(
            state,
            completeFetchProcessingTypeSuggestions({
                query: 'dyeing',
                requestIdentity: DYEING_REQUEST_IDENTITY,
                data: SUGGESTIONS,
            }),
        );

        const stateAfterStaleResponse = FilterOptionsReducer(
            state,
            completeFetchProcessingTypeSuggestions({
                query: 'dye',
                requestIdentity: '/api/processing-type-suggestions/?q=dye',
                data: [],
            }),
        );

        expect(stateAfterStaleResponse).toBe(state);
        expect(stateAfterStaleResponse.processingTypeSuggestions.data).toEqual(
            SUGGESTIONS,
        );
    });

    test('reducer drops a failure that answers a stale query', () => {
        let state = FilterOptionsReducer(undefined, { type: '@@INIT' });

        state = FilterOptionsReducer(
            state,
            startFetchProcessingTypeSuggestions({
                query: 'dyeing',
                requestIdentity: DYEING_REQUEST_IDENTITY,
            }),
        );

        const stateAfterStaleFailure = FilterOptionsReducer(
            state,
            failFetchProcessingTypeSuggestions({
                query: 'dye',
                requestIdentity: '/api/processing-type-suggestions/?q=dye',
                error: ['Network down'],
            }),
        );

        expect(stateAfterStaleFailure).toBe(state);
        expect(stateAfterStaleFailure.processingTypeSuggestions.error).toBeNull();
    });

    test('reducer drops stale results for different facility types', () => {
        let state = FilterOptionsReducer(undefined, { type: '@@INIT' });

        state = FilterOptionsReducer(
            state,
            startFetchProcessingTypeSuggestions({
                query: 'dyeing',
                requestIdentity: DYEING_REQUEST_IDENTITY,
            }),
        );
        state = FilterOptionsReducer(
            state,
            startFetchProcessingTypeSuggestions({
                query: 'dyeing',
                requestIdentity: FILTERED_DYEING_REQUEST_IDENTITY,
            }),
        );

        const stateAfterStaleResponse = FilterOptionsReducer(
            state,
            completeFetchProcessingTypeSuggestions({
                query: 'dyeing',
                requestIdentity: DYEING_REQUEST_IDENTITY,
                data: SUGGESTIONS,
            }),
        );

        expect(stateAfterStaleResponse).toBe(state);
        expect(stateAfterStaleResponse.processingTypeSuggestions).toEqual(
            expect.objectContaining({
                requestIdentity: FILTERED_DYEING_REQUEST_IDENTITY,
                data: null,
                fetching: true,
            }),
        );

        const stateAfterStaleFailure = FilterOptionsReducer(
            state,
            failFetchProcessingTypeSuggestions({
                query: 'dyeing',
                requestIdentity: DYEING_REQUEST_IDENTITY,
                error: ['Network down'],
            }),
        );

        expect(stateAfterStaleFailure).toBe(state);
        expect(stateAfterStaleFailure.processingTypeSuggestions.error).toBeNull();
    });
});
