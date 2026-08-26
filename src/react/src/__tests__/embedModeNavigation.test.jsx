import React from 'react';
import { MemoryRouter, Route } from 'react-router-dom';
import { waitFor } from '@testing-library/react';

import { setupStore } from '../configureStore';
import { setFiltersFromQueryString } from '../actions/filters';
import { fetchSingleFacility } from '../actions/facilities';
import FacilityDetailsContent from '../components/FacilityDetailsContent';
import apiRequest from '../util/apiRequest';
import { getFilteredSearchForEmbed } from '../util/util';
import renderWithProviders from '../util/testUtils/renderWithProviders';

jest.mock('../util/apiRequest', () => ({
    __esModule: true,
    default: {
        get: jest.fn(() =>
            Promise.resolve({
                data: {
                    id: 'CN20200165JMYV0',
                    type: 'Feature',
                    properties: {
                        name: 'Test Facility',
                        os_id: 'CN20200165JMYV0',
                        sector: [],
                        extended_fields: {},
                    },
                },
            }),
        ),
    },
}));

jest.mock('../components/FacilityDetailsClaimFlag', () => () => null);
jest.mock('../components/FacilityDetailsClosureStatus', () => () => null);
jest.mock('../components/FacilityDetailsCoreFields', () => () => null);
jest.mock('../components/FacilityDetailsInteractiveMap', () => () => null);
jest.mock('../components/FacilityDetailsLocationFields', () => () => null);
jest.mock('../components/FacilityDetailsGeneralFields', () => () => null);
jest.mock('../components/PartnerFields/PartnerFieldsSection/PartnerFieldsSection', () => () => null);
jest.mock('../components/FacilityDetailsContributors', () => () => null);

const EMBED_LIST_SEARCH = '?contributors=2340&lists=9193&sort_by=name_asc&embed=1';
const OS_ID = 'CN20200165JMYV0';
const CONTRIBUTOR_ID = 2340;

const contributorFilterOption = {
    value: CONTRIBUTOR_ID,
    label: String(CONTRIBUTOR_ID),
};

const minimalFacilitiesState = {
    facilities: {
        data: null,
        fetching: false,
        error: null,
        nextPageURL: null,
        isInfiniteLoading: false,
        hasAppliedFilters: false,
    },
    singleFacility: {
        data: null,
        fetching: false,
        error: null,
    },
};

const minimalAuthState = {
    user: {
        claimed_facility_ids: { approved: [], pending: [] },
    },
};

const createTestStore = (overrides = {}) => {
    const { facilities: facilitiesOverride, ...restOverrides } = overrides;

    return setupStore({
        filterOptions: {
            contributors: { data: null, fetching: false, error: null },
            parentCompanies: { data: null, fetching: false, error: null },
            lists: { data: null, fetching: false, error: null },
        },
        partnerGroupContributors: { data: null, fetching: false, error: null },
        ...restOverrides,
        facilities: {
            ...minimalFacilitiesState,
            ...(facilitiesOverride || {}),
            facilities: {
                ...minimalFacilitiesState.facilities,
                ...(facilitiesOverride?.facilities || {}),
            },
            singleFacility: {
                ...minimalFacilitiesState.singleFacility,
                ...(facilitiesOverride?.singleFacility || {}),
            },
        },
    });
};

describe('embed mode navigation integration', () => {
    beforeEach(() => {
        apiRequest.get.mockReset();
        apiRequest.get.mockImplementation(() =>
            Promise.resolve({
                data: {
                    id: OS_ID,
                    type: 'Feature',
                    properties: {
                        name: 'Test Facility',
                        os_id: OS_ID,
                        sector: [],
                        extended_fields: {},
                    },
                },
            }),
        );
    });

    describe('setFiltersFromQueryString (URL → Redux)', () => {
        it('hydrates contributors and embed from embed list URL', async () => {
            const store = createTestStore();

            await store.dispatch(setFiltersFromQueryString(EMBED_LIST_SEARCH));

            const { filters, embeddedMap } = store.getState();
            expect(embeddedMap.embed).toBe('1');
            expect(filters.contributors).toEqual([contributorFilterOption]);
        });

        it('clears contributors when detail URL has embed only (refresh regression)', async () => {
            const store = createTestStore({
                filters: {
                    contributors: [contributorFilterOption],
                },
                embeddedMap: { embed: '1' },
            });

            await store.dispatch(setFiltersFromQueryString('?embed=1'));

            expect(store.getState().filters.contributors).toEqual([]);
        });

        it('hydrates contributors from embed detail URL produced by getFilteredSearchForEmbed', async () => {
            const store = createTestStore();
            const detailSearch = getFilteredSearchForEmbed(EMBED_LIST_SEARCH);

            expect(detailSearch).toBe('?embed=1&contributors=2340');

            await store.dispatch(setFiltersFromQueryString(detailSearch));

            expect(store.getState().filters.contributors).toEqual([
                contributorFilterOption,
            ]);
        });
    });

    describe('fetchSingleFacility (Redux → API)', () => {
        it('calls API with embed=1 and contributor when Redux has a contributor', async () => {
            const store = createTestStore();

            await store.dispatch(
                fetchSingleFacility(
                    OS_ID,
                    1,
                    [contributorFilterOption],
                    true,
                ),
            );

            expect(apiRequest.get).toHaveBeenCalledTimes(1);
            const url = apiRequest.get.mock.calls[0][0];
            expect(url).toContain(`facilities/${OS_ID}/`);
            expect(url).toContain('embed=1');
            expect(url).toContain(`contributor=${CONTRIBUTOR_ID}`);
        });

        it('uses non-embed API URL when embed flag is off (no contributor in Redux)', async () => {
            const store = createTestStore();

            await store.dispatch(fetchSingleFacility(OS_ID, 0, null, true));

            const url = apiRequest.get.mock.calls[0][0];
            expect(url).not.toContain('contributor=');
            expect(url).not.toContain('embed=1');
        });
    });

    describe('FacilityDetailsContent (hydrate + mount → fetch)', () => {
        const renderDetailPage = async (search, preHydrateSearch) => {
            const store = createTestStore({
                auth: minimalAuthState,
                embeddedMap: { embed: '', config: {}, loading: false, error: null },
                featureFlags: { flags: {}, fetching: false },
            });

            if (preHydrateSearch) {
                await store.dispatch(setFiltersFromQueryString(preHydrateSearch));
            }

            renderWithProviders(
                <MemoryRouter
                    initialEntries={[`/facilities/${OS_ID}${search}`]}
                >
                    <Route
                        path="/facilities/:osID"
                        component={FacilityDetailsContent}
                    />
                </MemoryRouter>,
                { reduxStore: store },
            );

            return store;
        };

        it('fetches facility with embed contributor after list URL hydration', async () => {
            await renderDetailPage(
                '?embed=1&contributors=2340',
                EMBED_LIST_SEARCH,
            );

            await waitFor(() => expect(apiRequest.get).toHaveBeenCalled());

            const url = apiRequest.get.mock.calls[0][0];
            expect(url).toContain('embed=1');
            expect(url).toContain(`contributor=${CONTRIBUTOR_ID}`);
        });

        it('fetches without embed contributor when only embed=1 is hydrated (stripped detail URL)', async () => {
            await renderDetailPage('?embed=1', '?embed=1');

            await waitFor(() => expect(apiRequest.get).toHaveBeenCalled());

            const url = apiRequest.get.mock.calls[0][0];
            expect(url).not.toContain(`contributor=${CONTRIBUTOR_ID}`);
            expect(url).not.toContain('embed=1');
        });
    });
});
