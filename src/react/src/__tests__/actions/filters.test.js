import configureStore from 'redux-mock-store';
import thunk from 'redux-thunk';

import {
    setFiltersFromQueryString,
    updateAllFilters,
} from '../../actions/filters';

const mockStore = configureStore([thunk]);

describe('filter actions', () => {
    test('defaults missing sort_by to contributors_desc', () => {
        const store = mockStore({
            filterOptions: {
                contributors: { data: null },
                countries: { data: null },
                parentCompanies: { data: null },
                lists: { data: null },
                facilityProcessingType: { data: null },
            },
            partnerGroupContributors: { data: null },
            embeddedMap: { embed: '' },
        });

        store.dispatch(setFiltersFromQueryString('?contributors=1632'));

        expect(store.getActions()).toContainEqual(
            updateAllFilters(
                expect.objectContaining({
                    sortAlgorithm: expect.objectContaining({
                        value: 'contributors_desc',
                    }),
                }),
            ),
        );
    });
});
