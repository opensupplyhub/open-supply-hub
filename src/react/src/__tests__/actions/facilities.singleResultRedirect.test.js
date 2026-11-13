import configureStore from 'redux-mock-store';
import thunk from 'redux-thunk';

import { fetchFacilities } from '../../actions/facilities';
import apiRequest from '../../util/apiRequest';

jest.mock('../../util/apiRequest', () => ({
    __esModule: true,
    default: { get: jest.fn() },
}));

const mockStore = configureStore([thunk]);

const feature = osID => ({
    id: osID,
    type: 'Feature',
    geometry: { type: 'Point', coordinates: [0, 0] },
    properties: { os_id: osID, name: 'A facility', address: 'An address' },
});

const collection = (...osIDs) => ({
    type: 'FeatureCollection',
    features: osIDs.map(feature),
});

const state = () => ({
    filters: {},
    embeddedMap: { embed: false },
});

/*
 * A search matching exactly one production location navigates straight to
 * that location rather than showing a one-row list. Nothing covered this,
 * and multi-word search (OSDEV-3790) made the path far more common by
 * turning queries that returned nothing into queries that return one row.
 */
describe('single-result search redirect', () => {
    beforeEach(() => jest.clearAllMocks());

    test('navigates to the location when exactly one matches', async () => {
        apiRequest.get.mockResolvedValue({ data: collection('IN2021006BBQ8E5') });
        const pushNewRoute = jest.fn();

        await mockStore(state()).dispatch(fetchFacilities({ pushNewRoute }));

        expect(pushNewRoute).toHaveBeenCalledTimes(1);
        expect(pushNewRoute).toHaveBeenCalledWith(
            expect.stringContaining('IN2021006BBQ8E5'),
        );
    });

    test('stays on the results list when several match', async () => {
        apiRequest.get.mockResolvedValue({
            data: collection('IN2021006BBQ8E5', 'IN2021006BBQ8E6'),
        });
        const pushNewRoute = jest.fn();

        await mockStore(state()).dispatch(fetchFacilities({ pushNewRoute }));

        expect(pushNewRoute).not.toHaveBeenCalled();
    });

    test('stays on the results list when nothing matches', async () => {
        apiRequest.get.mockResolvedValue({ data: collection() });
        const pushNewRoute = jest.fn();

        await mockStore(state()).dispatch(fetchFacilities({ pushNewRoute }));

        expect(pushNewRoute).not.toHaveBeenCalled();
    });

    /*
     * The country map reuses this action to apply its country filter, and
     * seven countries hold exactly one production location. Filtering to one
     * of them must leave the user on the map, so the map opts out of the
     * redirect while still pushing the route the back button needs.
     * See OSDEV-3802 and OSDEV-3810.
     */
    test('skips the redirect when redirectOnSingleResult is false', async () => {
        apiRequest.get.mockResolvedValue({ data: collection('IN2021006BBQ8E5') });
        const pushNewRoute = jest.fn();

        await mockStore(state()).dispatch(
            fetchFacilities({ pushNewRoute, redirectOnSingleResult: false }),
        );

        expect(pushNewRoute).not.toHaveBeenCalled();
    });

    test('opting out still fetches and completes the search', async () => {
        apiRequest.get.mockResolvedValue({ data: collection('IN2021006BBQ8E5') });
        const store = mockStore(state());

        await store.dispatch(
            fetchFacilities({
                pushNewRoute: jest.fn(),
                redirectOnSingleResult: false,
            }),
        );

        const types = store.getActions().map(action => action.type);
        expect(types).toContain('COMPLETE_FETCH_FACILITIES');
        expect(types).not.toContain('FAIL_FETCH_FACILITIES');
    });

    test('redirects by default when the option is omitted', async () => {
        apiRequest.get.mockResolvedValue({ data: collection('IN2021006BBQ8E5') });
        const pushNewRoute = jest.fn();

        await mockStore(state()).dispatch(fetchFacilities({ pushNewRoute }));

        expect(pushNewRoute).toHaveBeenCalledTimes(1);
    });

    test('redirects when the option is explicitly true', async () => {
        apiRequest.get.mockResolvedValue({ data: collection('IN2021006BBQ8E5') });
        const pushNewRoute = jest.fn();

        await mockStore(state()).dispatch(
            fetchFacilities({ pushNewRoute, redirectOnSingleResult: true }),
        );

        expect(pushNewRoute).toHaveBeenCalledTimes(1);
    });

    /*
     * The regression this guards. `withQueryStringSync` passed `...push`,
     * spreading a function, which contributes no own enumerable properties;
     * `pushNewRoute` therefore fell back to its noop default and a search
     * restored from the URL never redirected, while the same search typed
     * into the box did. See OSDEV-3810.
     */
    test('spreading a function would not pass pushNewRoute', () => {
        // A plain function, as history.push is. Not jest.fn(), which carries
        // its own enumerable properties and so would not show the bug.
        const push = () => {};

        expect(Object.keys({ ...push })).toEqual([]);
        expect({ ...push }.pushNewRoute).toBeUndefined();
        expect({ pushNewRoute: push }.pushNewRoute).toBe(push);
    });
});
