import configureStore from 'redux-mock-store';
import thunk from 'redux-thunk';

import {
    completeFetchIsicTaxonomy,
    fetchIsicTaxonomy,
    fetchIsicTaxonomyIfNeeded,
    startFetchIsicTaxonomy,
} from '../../actions/filterOptions';
import FilterOptionsReducer from '../../reducers/FilterOptionsReducer';
import apiRequest from '../../util/apiRequest';

jest.mock('../../util/apiRequest', () => ({
    __esModule: true,
    default: { get: jest.fn() },
}));

const mockStore = configureStore([thunk]);
const ENTRIES = Object.freeze([
    { id: '4:13', title: 'Manufacture of textiles', level: 'division' },
]);

describe('ISIC taxonomy filterOptions actions', () => {
    beforeEach(() => jest.clearAllMocks());

    test('fetches the ISIC 4 and ISIC 5 entries', async () => {
        apiRequest.get.mockResolvedValue({ data: { entries: ENTRIES } });
        const store = mockStore({});

        await store.dispatch(fetchIsicTaxonomy());

        expect(apiRequest.get).toHaveBeenCalledWith('/api/taxonomy/isic/');
        expect(store.getActions()).toEqual([
            startFetchIsicTaxonomy(),
            completeFetchIsicTaxonomy(ENTRIES),
        ]);
    });

    test('fetches only once', () => {
        const state = FilterOptionsReducer(
            undefined,
            completeFetchIsicTaxonomy(ENTRIES),
        );
        const store = mockStore({ filterOptions: state });

        store.dispatch(fetchIsicTaxonomyIfNeeded());

        expect(apiRequest.get).not.toHaveBeenCalled();
        expect(state.isicTaxonomy.data).toEqual(ENTRIES);
    });
});
